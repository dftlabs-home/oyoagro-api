"""
FILE: src/livestockregistry/services.py
Business logic for LivestockRegistry operations
"""
from sqlmodel import Session, select, func
from src.shared.models import LivestockRegistry, Farm, Season, Livestock, Farmer
from src.livestockregistry.schemas import LivestockRegistryCreate, LivestockRegistryUpdate
from datetime import datetime, date
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class LivestockRegistryService:
    """Service class for LivestockRegistry business logic"""
    
    @staticmethod
    async def create(data: LivestockRegistryCreate, session: Session) -> LivestockRegistry:
        """Create new livestock registry"""
        # Validate farm exists
        farm = session.get(Farm, data.farmid)
        if not farm or farm.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {data.farmid} not found"
            )
        
        # Validate season exists
        season = session.get(Season, data.seasonid)
        if not season or season.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Season with ID {data.seasonid} not found"
            )
        
        # Validate livestock type exists
        livestock = session.get(Livestock, data.livestocktypeid)
        if not livestock or livestock.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livestock with ID {data.livestocktypeid} not found"
            )
        
        # Validate start date is within season
        if data.startdate:
            if data.startdate < season.startdate or data.startdate > season.enddate: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Start date must be within season dates ({season.startdate} to {season.enddate})"
                )
        
        # Validate end date is within season
        if data.enddate:
            if data.enddate < season.startdate: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"End date must be within season dates ({season.startdate} to {season.enddate})"
                )
        
        # Create registry
        registry = LivestockRegistry(
            farmid=data.farmid,
            seasonid=data.seasonid,
            livestocktypeid=data.livestocktypeid,
            quantity=data.quantity,
            startdate=data.startdate,
            enddate=data.enddate,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Created livestock registry: {registry.livestockregistryid} for farm {data.farmid}")
        return registry
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        farm_id: Optional[int] = None,
        season_id: Optional[int] = None,
        livestock_id: Optional[int] = None,
        farmer_id: Optional[int] = None
    ) -> List[LivestockRegistry]:
        """Get all active livestock registries with filters"""
        statement = select(LivestockRegistry).where(LivestockRegistry.deletedat == None)
        
        if farm_id:
            statement = statement.where(LivestockRegistry.farmid == farm_id)
        
        if season_id:
            statement = statement.where(LivestockRegistry.seasonid == season_id)
        
        if livestock_id:
            statement = statement.where(LivestockRegistry.livestocktypeid == livestock_id)
        
        if farmer_id:
            statement = statement.join(Farm, LivestockRegistry.farmid == Farm.farmid).where( # type: ignore
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(LivestockRegistry.createdat.desc()) # type: ignore
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(registry_id: int, session: Session) -> LivestockRegistry:
        """Get livestock registry by ID"""
        registry = session.get(LivestockRegistry, registry_id)
        
        if not registry or registry.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livestock registry with ID {registry_id} not found"
            )
        
        return registry
    
    @staticmethod
    async def get_with_details(registry_id: int, session: Session) -> dict:
        """Get livestock registry with full details"""
        registry = await LivestockRegistryService.get_by_id(registry_id, session)
        
        # Get farm and farmer details
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        farmer_name = f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown"
        
        # Get season details
        season = session.get(Season, registry.seasonid)
        season_name = season.name if season else "Unknown"
        
        # Get livestock details
        livestock = session.get(Livestock, registry.livestocktypeid)
        livestock_name = livestock.name if livestock else "Unknown"
        
        # Determine status
        status = "Active"
        if registry.enddate and registry.enddate <= date.today():
            status = "Completed"
        
        return {
            "livestockregistryid": registry.livestockregistryid,
            "farmid": registry.farmid,
            "farm_name": f"Farm #{registry.farmid}",
            "farmer_name": farmer_name,
            "seasonid": registry.seasonid,
            "season_name": season_name,
            "livestocktypeid": registry.livestocktypeid,
            "livestock_name": livestock_name,
            "quantity": registry.quantity,
            "startdate": registry.startdate,
            "enddate": registry.enddate,
            "status": status,
            "createdat": registry.createdat,
            "updatedat": registry.updatedat,
            "version": registry.version
        }
    
    @staticmethod
    async def update(registry_id: int, data: LivestockRegistryUpdate, session: Session) -> LivestockRegistry:
        """Update livestock registry"""
        registry = await LivestockRegistryService.get_by_id(registry_id, session)
        
        # Get season for validation
        season = session.get(Season, registry.seasonid)
        
        # Update fields
        if data.quantity is not None:
            registry.quantity = data.quantity
        
        if data.startdate is not None:
            if season and (data.startdate < season.startdate or data.startdate > season.enddate): # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Start date must be within season dates"
                )
            registry.startdate = data.startdate
        
        if data.enddate is not None:
            if season and data.enddate < season.startdate: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"End date must be within season dates"
                )
            registry.enddate = data.enddate
        
        registry.updatedat = datetime.utcnow()
        registry.version = (registry.version or 0) + 1
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Updated livestock registry: {registry_id}")
        return registry
    
    @staticmethod
    async def delete(registry_id: int, session: Session) -> None:
        """Soft delete livestock registry"""
        registry = await LivestockRegistryService.get_by_id(registry_id, session)
        
        registry.deletedat = datetime.utcnow()
        session.add(registry)
        session.commit()
        
        logger.info(f"Deleted livestock registry: {registry_id}")
    
    @staticmethod
    async def get_statistics(session: Session, season_id: Optional[int] = None) -> dict:
        """Get livestock registry statistics"""
        statement = select(LivestockRegistry).where(LivestockRegistry.deletedat == None)
        
        if season_id:
            statement = statement.where(LivestockRegistry.seasonid == season_id)
        
        registries = session.exec(statement).all()
        
        total_registries = len(registries)
        total_quantity = sum(r.quantity for r in registries) # type: ignore
        
        # Count by status
        active = sum(1 for r in registries if not r.enddate or r.enddate > date.today())
        completed = sum(1 for r in registries if r.enddate and r.enddate <= date.today())
        
        # Group by livestock type
        by_type = {}
        for registry in registries:
            livestock = session.get(Livestock, registry.livestocktypeid)
            livestock_name = livestock.name if livestock else "Unknown"
            
            if livestock_name not in by_type:
                by_type[livestock_name] = {"count": 0, "total_quantity": 0}
            
            by_type[livestock_name]["count"] += 1
            by_type[livestock_name]["total_quantity"] += registry.quantity
        
        return {
            "total_registries": total_registries,
            "total_quantity": total_quantity,
            "avg_quantity_per_registry": round(total_quantity / total_registries, 2) if total_registries > 0 else 0,
            "status_breakdown": {
                "active": active,
                "completed": completed
            },
            "by_livestock_type": by_type
        }
