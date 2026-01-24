"""
FILE: src/farmtypes/services.py
Business logic for FarmType operations
"""
from sqlmodel import Session, select
from src.shared.models import Farmtype, Farm
from src.farmtypes.schemas import FarmTypeCreate, FarmTypeUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class FarmTypeService:
    """Service class for FarmType business logic"""
    
    @staticmethod
    async def create(data: FarmTypeCreate, session: Session) -> Farmtype:
        """
        Create new farm type
        
        Args:
            data: Farm type creation data
            session: Database session
            
        Returns:
            Farmtype: Created farm type
            
        Raises:
            HTTPException: If farm type name already exists
        """
        # Check for duplicate name
        existing = session.exec(
            select(Farmtype).where(
                Farmtype.typename == data.typename,
                Farmtype.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Farm type '{data.typename}' already exists"
            )
        
        # Create farm type
        farmtype = Farmtype(
            typename=data.typename,
            createdat=datetime.utcnow()
        )
        
        session.add(farmtype)
        session.commit()
        session.refresh(farmtype)
        
        logger.info(f"Created farm type: {farmtype.farmtypeid} - {farmtype.typename}")
        return farmtype
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Farmtype]:
        """
        Get all active farm types with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Farmtype]: List of farm types
        """
        statement = select(Farmtype).where(
            Farmtype.deletedat == None
        ).offset(skip).limit(limit).order_by(Farmtype.typename)
        
        farmtypes = session.exec(statement).all()
        return list(farmtypes)
    
    @staticmethod
    async def get_by_id(farmtype_id: int, session: Session) -> Farmtype:
        """
        Get farm type by ID
        
        Args:
            farmtype_id: Farm type ID
            session: Database session
            
        Returns:
            Farmtype: Found farm type
            
        Raises:
            HTTPException: If farm type not found
        """
        farmtype = session.get(Farmtype, farmtype_id)
        
        if not farmtype or farmtype.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm type with ID {farmtype_id} not found"
            )
        
        return farmtype
    
    @staticmethod
    async def get_with_stats(farmtype_id: int, session: Session) -> dict:
        """
        Get farm type with statistics
        
        Args:
            farmtype_id: Farm type ID
            session: Database session
            
        Returns:
            dict: Farm type with statistics
        """
        farmtype = await FarmTypeService.get_by_id(farmtype_id, session)
        
        # Count farms with this type
        farm_count = len(session.exec(
            select(Farm).where(
                Farm.farmtypeid == farmtype_id,
                Farm.deletedat == None
            )
        ).all())
        
        return {
            "farmtypeid": farmtype.farmtypeid,
            "typename": farmtype.typename,
            "farm_count": farm_count,
            "createdat": farmtype.createdat,
            "updatedat": farmtype.updatedat
        }
    
    @staticmethod
    async def update(
        farmtype_id: int,
        data: FarmTypeUpdate,
        session: Session
    ) -> Farmtype:
        """
        Update farm type
        
        Args:
            farmtype_id: Farm type ID
            data: Update data
            session: Database session
            
        Returns:
            Farmtype: Updated farm type
            
        Raises:
            HTTPException: If farm type not found or duplicate name
        """
        farmtype = await FarmTypeService.get_by_id(farmtype_id, session)
        
        # Check for duplicate name if name is being updated
        if data.typename and data.typename != farmtype.typename:
            existing = session.exec(
                select(Farmtype).where(
                    Farmtype.typename == data.typename,
                    Farmtype.deletedat == None,
                    Farmtype.farmtypeid != farmtype_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Farm type '{data.typename}' already exists"
                )
            
            farmtype.typename = data.typename
        
        farmtype.updatedat = datetime.utcnow()
        #farmtype.version = (farmtype.version or 0) + 1 # type: ignore
        
        session.add(farmtype)
        session.commit()
        session.refresh(farmtype)
        
        logger.info(f"Updated farm type: {farmtype.farmtypeid}")
        return farmtype
    
    @staticmethod
    async def delete(farmtype_id: int, session: Session) -> None:
        """
        Soft delete farm type
        
        Args:
            farmtype_id: Farm type ID
            session: Database session
            
        Raises:
            HTTPException: If farm type not found or has farms
        """
        farmtype = await FarmTypeService.get_by_id(farmtype_id, session)
        
        # Check if farm type has farms
        farms_count = session.exec(
            select(Farm).where(
                Farm.farmtypeid == farmtype_id,
                Farm.deletedat == None
            )
        ).first()
        
        if farms_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete farm type with existing farms"
            )
        
        farmtype.deletedat = datetime.utcnow()
        session.add(farmtype)
        session.commit()
        
        logger.info(f"Deleted farm type: {farmtype_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Farmtype]:
        """
        Search farm types by name
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Farmtype]: Matching farm types
        """
        statement = select(Farmtype).where(
            Farmtype.deletedat == None,
            (Farmtype.typename.ilike(f"%{query}%")) # type: ignore
        ).offset(skip).limit(limit).order_by(Farmtype.typename)
        
        farmtypes = session.exec(statement).all()
        return list(farmtypes)
    
    @staticmethod
    async def get_all_with_farm_counts(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Get all farm types with their farm counts
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[dict]: Farm types with farm counts
        """
        farmtypes = await FarmTypeService.get_all(session, skip, limit)
        
        result = []
        for farmtype in farmtypes:
            farm_count = len(session.exec(
                select(Farm).where(
                    Farm.farmtypeid == farmtype.farmtypeid,
                    Farm.deletedat == None
                )
            ).all())
            
            result.append({
                "farmtypeid": farmtype.farmtypeid,
                "typename": farmtype.typename,
                "farm_count": farm_count,
                "createdat": farmtype.createdat,
                "updatedat": farmtype.updatedat
            })
        
        return result