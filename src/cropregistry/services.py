"""
FILE: src/cropregistry/services.py
Business logic for CropRegistry operations
"""
from sqlmodel import Session, select, func
from src.shared.models import CropRegistry, Farm, Season, Crop, Farmer
from src.cropregistry.schemas import CropRegistryCreate, CropRegistryUpdate
from datetime import datetime, date
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class CropRegistryService:
    """Service class for CropRegistry business logic"""
    
    @staticmethod
    async def create(data: CropRegistryCreate, session: Session) -> CropRegistry:
        """
        Create new crop registry
        
        Args:
            data: Crop registry creation data
            session: Database session
            
        Returns:
            CropRegistry: Created registry
            
        Raises:
            HTTPException: If validation fails
        """
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
        
        # Validate crop type exists
        crop = session.get(Crop, data.croptypeid)
        if not crop or crop.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with ID {data.croptypeid} not found"
            )
        
        # Validate planting date is within season
        if data.plantingdate:
            if data.plantingdate < season.startdate or data.plantingdate > season.enddate: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Planting date must be within season dates ({season.startdate} to {season.enddate})"
                )
        
        # Validate harvest date is within season
        if data.harvestdate:
            if data.harvestdate < season.startdate or data.harvestdate > season.enddate: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Harvest date must be within season dates ({season.startdate} to {season.enddate})"
                )
        
        # Create registry
        registry = CropRegistry(
            farmid=data.farmid,
            seasonid=data.seasonid,
            croptypeid=data.croptypeid,
            cropvariety=data.cropvariety,
            areaplanted=data.areaplanted,
            plantedquantity=data.plantedquantity,
            plantingdate=data.plantingdate,
            harvestdate=data.harvestdate,
            areaharvested=data.areaharvested,
            yieldquantity=data.yieldquantity,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Created crop registry: {registry.cropregistryid} for farm {data.farmid}")
        return registry
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        farm_id: Optional[int] = None,
        season_id: Optional[int] = None,
        crop_id: Optional[int] = None,
        farmer_id: Optional[int] = None
    ) -> List[CropRegistry]:
        """Get all active crop registries with filters"""
        statement = select(CropRegistry).where(CropRegistry.deletedat == None)
        
        if farm_id:
            statement = statement.where(CropRegistry.farmid == farm_id)
        
        if season_id:
            statement = statement.where(CropRegistry.seasonid == season_id)
        
        if crop_id:
            statement = statement.where(CropRegistry.croptypeid == crop_id)
        
        if farmer_id:
            # Filter by farmer through farm
            statement = statement.join(Farm, CropRegistry.farmid == Farm.farmid).where( # type: ignore
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(CropRegistry.createdat.desc()) # type: ignore
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(registry_id: int, session: Session) -> CropRegistry:
        """Get crop registry by ID"""
        registry = session.get(CropRegistry, registry_id)
        
        if not registry or registry.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop registry with ID {registry_id} not found"
            )
        
        return registry
    
    @staticmethod
    async def get_with_details(registry_id: int, session: Session) -> dict:
        """Get crop registry with full details"""
        registry = await CropRegistryService.get_by_id(registry_id, session)
        
        # Get farm and farmer details
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        farmer_name = f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown"
        
        # Get season details
        season = session.get(Season, registry.seasonid)
        season_name = season.name if season else "Unknown"
        
        # Get crop details
        crop = session.get(Crop, registry.croptypeid)
        crop_name = crop.name if crop else "Unknown"
        
        # Determine status
        status = "Pending"
        if registry.harvestdate:
            status = "Harvested"
        elif registry.plantingdate:
            status = "Planted"
        
        return {
            "cropregistryid": registry.cropregistryid,
            "farmid": registry.farmid,
            "farm_name": f"Farm #{registry.farmid}",
            "farmer_name": farmer_name,
            "seasonid": registry.seasonid,
            "season_name": season_name,
            "croptypeid": registry.croptypeid,
            "crop_name": crop_name,
            "cropvariety": registry.cropvariety,
            "areaplanted": registry.areaplanted,
            "plantedquantity": registry.plantedquantity,
            "plantingdate": registry.plantingdate,
            "harvestdate": registry.harvestdate,
            "areaharvested": registry.areaharvested,
            "yieldquantity": registry.yieldquantity,
            "status": status,
            "createdat": registry.createdat,
            "updatedat": registry.updatedat,
            "version": registry.version
        }
    
    @staticmethod
    async def update(registry_id: int, data: CropRegistryUpdate, session: Session) -> CropRegistry:
        """Update crop registry"""
        registry = await CropRegistryService.get_by_id(registry_id, session)
        
        # Update fields
        if data.cropvariety is not None:
            registry.cropvariety = data.cropvariety
        if data.areaplanted is not None:
            registry.areaplanted = data.areaplanted
        if data.plantedquantity is not None:
            registry.plantedquantity = data.plantedquantity
        if data.plantingdate is not None:
            # Validate within season
            season = session.get(Season, registry.seasonid)
            if season and (data.plantingdate < season.startdate or data.plantingdate > season.enddate): # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Planting date must be within season dates"
                )
            registry.plantingdate = data.plantingdate
        if data.harvestdate is not None:
            # Validate within season
            season = session.get(Season, registry.seasonid)
            if season and (data.harvestdate < season.startdate or data.harvestdate > season.enddate): # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Harvest date must be within season dates"
                )
            registry.harvestdate = data.harvestdate
        if data.areaharvested is not None:
            registry.areaharvested = data.areaharvested
        if data.yieldquantity is not None:
            registry.yieldquantity = data.yieldquantity
        
        registry.updatedat = datetime.utcnow()
        registry.version = (registry.version or 0) + 1
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Updated crop registry: {registry_id}")
        return registry
    
    @staticmethod
    async def delete(registry_id: int, session: Session) -> None:
        """Soft delete crop registry"""
        registry = await CropRegistryService.get_by_id(registry_id, session)
        
        registry.deletedat = datetime.utcnow()
        session.add(registry)
        session.commit()
        
        logger.info(f"Deleted crop registry: {registry_id}")
    
    @staticmethod
    async def get_statistics(session: Session, season_id: Optional[int] = None) -> dict:
        """Get crop registry statistics"""
        statement = select(CropRegistry).where(CropRegistry.deletedat == None)
        
        if season_id:
            statement = statement.where(CropRegistry.seasonid == season_id)
        
        registries = session.exec(statement).all()
        
        total_registries = len(registries)
        total_area_planted = sum(r.areaplanted or 0 for r in registries)
        total_area_harvested = sum(r.areaharvested or 0 for r in registries)
        total_yield = sum(r.yieldquantity or 0 for r in registries)
        
        # Count by status
        planted = sum(1 for r in registries if r.plantingdate and not r.harvestdate)
        harvested = sum(1 for r in registries if r.harvestdate)
        pending = sum(1 for r in registries if not r.plantingdate)
        
        # Average yield per hectare
        avg_yield_per_hectare = 0
        if total_area_harvested > 0:
            avg_yield_per_hectare = float(total_yield) / float(total_area_harvested)
        
        return {
            "total_registries": total_registries,
            "total_area_planted": float(total_area_planted),
            "total_area_harvested": float(total_area_harvested),
            "total_yield": float(total_yield),
            "avg_yield_per_hectare": round(avg_yield_per_hectare, 2),
            "status_breakdown": {
                "pending": pending,
                "planted": planted,
                "harvested": harvested
            }
        }