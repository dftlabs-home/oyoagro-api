"""
FILE: src/agroalliedregistry/services.py
Business logic for AgroAlliedRegistry operations
"""
from sqlmodel import Session, select, func
from src.shared.models import AgroAlliedRegistry, Farm, Season, BusinessType, PrimaryProduct, Farmer
from src.agroalliedregistry.schemas import AgroAlliedRegistryCreate, AgroAlliedRegistryUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AgroAlliedRegistryService:
    """Service class for AgroAlliedRegistry business logic"""
    
    @staticmethod
    async def create(data: AgroAlliedRegistryCreate, session: Session) -> AgroAlliedRegistry:
        """Create new agro-allied registry"""
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
        
        # Validate business type exists
        businesstype = session.get(BusinessType, data.businesstypeid)
        if not businesstype or businesstype.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business type with ID {data.businesstypeid} not found"
            )
        
        # Validate primary product exists
        product = session.get(PrimaryProduct, data.primaryproducttypeid)
        if not product or product.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Primary product with ID {data.primaryproducttypeid} not found"
            )
        
        # Create registry
        registry = AgroAlliedRegistry(
            farmid=data.farmid,
            seasonid=data.seasonid,
            businesstypeid=data.businesstypeid,
            primaryproducttypeid=data.primaryproducttypeid,
            productioncapacity=data.productioncapacity,
            createdat=datetime.utcnow()
        )
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Created agro-allied registry: {registry.agroalliedregistryid} for farm {data.farmid}")
        return registry
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        farm_id: Optional[int] = None,
        season_id: Optional[int] = None,
        businesstype_id: Optional[int] = None,
        product_id: Optional[int] = None,
        farmer_id: Optional[int] = None
    ) -> List[AgroAlliedRegistry]:
        """Get all active agro-allied registries with filters"""
        statement = select(AgroAlliedRegistry).where(AgroAlliedRegistry.deletedat == None)
        
        if farm_id:
            statement = statement.where(AgroAlliedRegistry.farmid == farm_id)
        
        if season_id:
            statement = statement.where(AgroAlliedRegistry.seasonid == season_id)
        
        if businesstype_id:
            statement = statement.where(AgroAlliedRegistry.businesstypeid == businesstype_id)
        
        if product_id:
            statement = statement.where(AgroAlliedRegistry.primaryproducttypeid == product_id)
        
        if farmer_id:
            statement = statement.join(Farm, AgroAlliedRegistry.farmid == Farm.farmid).where( # type: ignore
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(AgroAlliedRegistry.createdat.desc()) # type: ignore
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(registry_id: int, session: Session) -> AgroAlliedRegistry:
        """Get agro-allied registry by ID"""
        registry = session.get(AgroAlliedRegistry, registry_id)
        
        if not registry or registry.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agro-allied registry with ID {registry_id} not found"
            )
        
        return registry
    
    @staticmethod
    async def get_with_details(registry_id: int, session: Session) -> dict:
        """Get agro-allied registry with full details"""
        registry = await AgroAlliedRegistryService.get_by_id(registry_id, session)
        
        # Get farm and farmer details
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        farmer_name = f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown"
        
        # Get season details
        season = session.get(Season, registry.seasonid)
        season_name = season.name if season else "Unknown"
        
        # Get business type details
        businesstype = session.get(BusinessType, registry.businesstypeid)
        business_type_name = businesstype.name if businesstype else "Unknown"
        
        # Get primary product details
        product = session.get(PrimaryProduct, registry.primaryproducttypeid)
        primary_product_name = product.name if product else "Unknown"
        
        return {
            "agroalliedregistryid": registry.agroalliedregistryid,
            "farmid": registry.farmid,
            "farm_name": f"Farm #{registry.farmid}",
            "farmer_name": farmer_name,
            "seasonid": registry.seasonid,
            "season_name": season_name,
            "businesstypeid": registry.businesstypeid,
            "business_type_name": business_type_name,
            "primaryproducttypeid": registry.primaryproducttypeid,
            "primary_product_name": primary_product_name,
            "productioncapacity": registry.productioncapacity,
            "createdat": registry.createdat,
            "updatedat": registry.updatedat
        }
    
    @staticmethod
    async def update(registry_id: int, data: AgroAlliedRegistryUpdate, session: Session) -> AgroAlliedRegistry:
        """Update agro-allied registry"""
        registry = await AgroAlliedRegistryService.get_by_id(registry_id, session)
        
        if data.productioncapacity is not None:
            registry.productioncapacity = data.productioncapacity
        
        registry.updatedat = datetime.utcnow()
        
        session.add(registry)
        session.commit()
        session.refresh(registry)
        
        logger.info(f"Updated agro-allied registry: {registry_id}")
        return registry
    
    @staticmethod
    async def delete(registry_id: int, session: Session) -> None:
        """Soft delete agro-allied registry"""
        registry = await AgroAlliedRegistryService.get_by_id(registry_id, session)
        
        registry.deletedat = datetime.utcnow()
        session.add(registry)
        session.commit()
        
        logger.info(f"Deleted agro-allied registry: {registry_id}")
    
    @staticmethod
    async def get_statistics(session: Session, season_id: Optional[int] = None) -> dict:
        """Get agro-allied registry statistics"""
        statement = select(AgroAlliedRegistry).where(AgroAlliedRegistry.deletedat == None)
        
        if season_id:
            statement = statement.where(AgroAlliedRegistry.seasonid == season_id)
        
        registries = session.exec(statement).all()
        
        total_registries = len(registries)
        total_capacity = sum(r.productioncapacity or 0 for r in registries)
        
        # Group by business type
        by_business_type = {}
        for registry in registries:
            bt = session.get(BusinessType, registry.businesstypeid)
            bt_name = bt.name if bt else "Unknown"
            
            if bt_name not in by_business_type:
                by_business_type[bt_name] = {"count": 0, "total_capacity": 0}
            
            by_business_type[bt_name]["count"] += 1
            by_business_type[bt_name]["total_capacity"] += float(registry.productioncapacity or 0)
        
        # Group by primary product
        by_product = {}
        for registry in registries:
            product = session.get(PrimaryProduct, registry.primaryproducttypeid)
            product_name = product.name if product else "Unknown"
            
            if product_name not in by_product:
                by_product[product_name] = {"count": 0, "total_capacity": 0}
            
            by_product[product_name]["count"] += 1
            by_product[product_name]["total_capacity"] += float(registry.productioncapacity or 0)
        
        return {
            "total_registries": total_registries,
            "total_production_capacity": float(total_capacity),
            "avg_capacity_per_registry": round(float(total_capacity) / total_registries, 2) if total_registries > 0 else 0,
            "by_business_type": by_business_type,
            "by_primary_product": by_product
        }