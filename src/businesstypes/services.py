"""
FILE: src/businesstypes/services.py
Business logic for BusinessType operations
"""
from sqlmodel import Session, select, func
from src.shared.models import BusinessType, AgroAlliedRegistry
from src.businesstypes.schemas import BusinessTypeCreate, BusinessTypeUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class BusinessTypeService:
    """Service class for BusinessType business logic"""
    
    @staticmethod
    async def create(data: BusinessTypeCreate, session: Session) -> BusinessType:
        """Create new business type"""
        # Check for duplicate name (case-insensitive)
        existing = session.exec(
            select(BusinessType).where(
                func.lower(BusinessType.name) == func.lower(data.name),
                BusinessType.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business type '{data.name}' already exists"
            )
        
        businesstype = BusinessType(name=data.name, createdat=datetime.utcnow())
        session.add(businesstype)
        session.commit()
        session.refresh(businesstype)
        
        logger.info(f"Created business type: {businesstype.businesstypeid} - {businesstype.name}")
        return businesstype
    
    @staticmethod
    async def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[BusinessType]:
        """Get all active business types"""
        statement = select(BusinessType).where(
            BusinessType.deletedat == None
        ).offset(skip).limit(limit).order_by(BusinessType.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(businesstype_id: int, session: Session) -> BusinessType:
        """Get business type by ID"""
        businesstype = session.get(BusinessType, businesstype_id)
        
        if not businesstype or businesstype.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business type with ID {businesstype_id} not found"
            )
        
        return businesstype
    
    @staticmethod
    async def get_with_stats(businesstype_id: int, session: Session) -> dict:
        """Get business type with statistics"""
        businesstype = await BusinessTypeService.get_by_id(businesstype_id, session)
        
        # Count registries
        registry_count = session.exec(
            select(func.count(AgroAlliedRegistry.agroalliedregistryid)) # type: ignore
            .where(
                AgroAlliedRegistry.businesstypeid == businesstype_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first() or 0
        
        return {
            "businesstypeid": businesstype.businesstypeid,
            "name": businesstype.name,
            "registry_count": registry_count,
            "createdat": businesstype.createdat,
            "updatedat": businesstype.updatedat
        }
    
    @staticmethod
    async def update(businesstype_id: int, data: BusinessTypeUpdate, session: Session) -> BusinessType:
        """Update business type"""
        businesstype = await BusinessTypeService.get_by_id(businesstype_id, session)
        
        if data.name and data.name != businesstype.name:
            existing = session.exec(
                select(BusinessType).where(
                    func.lower(BusinessType.name) == func.lower(data.name),
                    BusinessType.deletedat == None,
                    BusinessType.businesstypeid != businesstype_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Business type '{data.name}' already exists"
                )
            
            businesstype.name = data.name
        
        businesstype.updatedat = datetime.utcnow()
        session.add(businesstype)
        session.commit()
        session.refresh(businesstype)
        
        logger.info(f"Updated business type: {businesstype_id}")
        return businesstype
    
    @staticmethod
    async def delete(businesstype_id: int, session: Session) -> None:
        """Soft delete business type"""
        businesstype = await BusinessTypeService.get_by_id(businesstype_id, session)
        
        # Check if has registries
        registries = session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.businesstypeid == businesstype_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first()
        
        if registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete business type with existing registries"
            )
        
        businesstype.deletedat = datetime.utcnow()
        session.add(businesstype)
        session.commit()
        
        logger.info(f"Deleted business type: {businesstype_id}")
    
    @staticmethod
    async def search(query: str, session: Session, skip: int = 0, limit: int = 100) -> List[BusinessType]:
        """Search business types by name"""
        statement = select(BusinessType).where(
            BusinessType.deletedat == None,
            BusinessType.name.ilike(f"%{query}%") # type: ignore
        ).offset(skip).limit(limit).order_by(BusinessType.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_all_with_counts(session: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all business types with registry counts"""
        businesstypes = await BusinessTypeService.get_all(session, skip, limit)
        
        result = []
        for bt in businesstypes:
            count = session.exec(
                select(func.count(AgroAlliedRegistry.agroalliedregistryid)) # type: ignore
                .where(
                    AgroAlliedRegistry.businesstypeid == bt.businesstypeid,
                    AgroAlliedRegistry.deletedat == None
                )
            ).first() or 0
            
            result.append({
                "businesstypeid": bt.businesstypeid,
                "name": bt.name,
                "registry_count": count,
                "createdat": bt.createdat
            })
        
        return result
