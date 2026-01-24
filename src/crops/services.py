"""
FILE: src/crops/services.py
Business logic for Crop operations
"""
from sqlmodel import Session, select, func
from src.shared.models import Crop, CropRegistry
from src.crops.schemas import CropCreate, CropUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class CropService:
    """Service class for Crop business logic"""
    
    @staticmethod
    async def create(data: CropCreate, session: Session) -> Crop:
        """
        Create new crop type
        
        Args:
            data: Crop creation data
            session: Database session
            
        Returns:
            Crop: Created crop
            
        Raises:
            HTTPException: If crop name already exists
        """
        # Check for duplicate name (case-insensitive)
        existing = session.exec(
            select(Crop).where(
                func.lower(Crop.name) == func.lower(data.name),
                Crop.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Crop '{data.name}' already exists"
            )
        
        # Create crop
        crop = Crop(
            name=data.name,
            createdat=datetime.utcnow()
        )
        
        session.add(crop)
        session.commit()
        session.refresh(crop)
        
        logger.info(f"Created crop: {crop.croptypeid} - {crop.name}")
        return crop
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Crop]:
        """
        Get all active crops with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Crop]: List of crops
        """
        statement = select(Crop).where(
            Crop.deletedat == None
        ).offset(skip).limit(limit).order_by(Crop.name)
        
        crops = session.exec(statement).all()
        return list(crops)
    
    @staticmethod
    async def get_by_id(crop_id: int, session: Session) -> Crop:
        """
        Get crop by ID
        
        Args:
            crop_id: Crop ID
            session: Database session
            
        Returns:
            Crop: Found crop
            
        Raises:
            HTTPException: If crop not found
        """
        crop = session.get(Crop, crop_id)
        
        if not crop or crop.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with ID {crop_id} not found"
            )
        
        return crop
    
    @staticmethod
    async def get_with_stats(crop_id: int, session: Session) -> dict:
        """
        Get crop with statistics
        
        Args:
            crop_id: Crop ID
            session: Database session
            
        Returns:
            dict: Crop with statistics
        """
        crop = await CropService.get_by_id(crop_id, session)
        
        # Count registries
        registry_count = session.exec(
            select(func.count(CropRegistry.cropregistryid)) # type: ignore
            .where(
                CropRegistry.croptypeid == crop_id,
                CropRegistry.deletedat == None
            )
        ).first() or 0
        
        # Calculate total area planted
        total_area_planted = session.exec(
            select(func.sum(CropRegistry.areaplanted))
            .where(
                CropRegistry.croptypeid == crop_id,
                CropRegistry.deletedat == None
            )
        ).first() or 0
        
        # Calculate total yield
        total_yield = session.exec(
            select(func.sum(CropRegistry.yieldquantity))
            .where(
                CropRegistry.croptypeid == crop_id,
                CropRegistry.deletedat == None
            )
        ).first() or 0
        
        return {
            "croptypeid": crop.croptypeid,
            "name": crop.name,
            "registry_count": registry_count,
            "total_area_planted": float(total_area_planted) if total_area_planted else 0.0,
            "total_yield": float(total_yield) if total_yield else 0.0,
            "createdat": crop.createdat,
            "updatedat": crop.updatedat
        }
    
    @staticmethod
    async def update(
        crop_id: int,
        data: CropUpdate,
        session: Session
    ) -> Crop:
        """
        Update crop
        
        Args:
            crop_id: Crop ID
            data: Update data
            session: Database session
            
        Returns:
            Crop: Updated crop
        """
        crop = await CropService.get_by_id(crop_id, session)
        
        # Check for duplicate name if being updated
        if data.name and data.name != crop.name:
            existing = session.exec(
                select(Crop).where(
                    func.lower(Crop.name) == func.lower(data.name),
                    Crop.deletedat == None,
                    Crop.croptypeid != crop_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Crop '{data.name}' already exists"
                )
            
            crop.name = data.name
        
        crop.updatedat = datetime.utcnow()
        
        session.add(crop)
        session.commit()
        session.refresh(crop)
        
        logger.info(f"Updated crop: {crop_id}")
        return crop
    
    @staticmethod
    async def delete(crop_id: int, session: Session) -> None:
        """
        Soft delete crop
        
        Args:
            crop_id: Crop ID
            session: Database session
            
        Raises:
            HTTPException: If crop not found or has registries
        """
        crop = await CropService.get_by_id(crop_id, session)
        
        # Check if crop has registries
        registries = session.exec(
            select(CropRegistry).where(
                CropRegistry.croptypeid == crop_id,
                CropRegistry.deletedat == None
            )
        ).first()
        
        if registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete crop type with existing registries"
            )
        
        crop.deletedat = datetime.utcnow()
        session.add(crop)
        session.commit()
        
        logger.info(f"Deleted crop: {crop_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Crop]:
        """
        Search crops by name
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Crop]: Matching crops
        """
        statement = select(Crop).where(
            Crop.deletedat == None,
            Crop.name.ilike(f"%{query}%") # type: ignore
        ).offset(skip).limit(limit).order_by(Crop.name)
        
        crops = session.exec(statement).all()
        return list(crops)
    
    @staticmethod
    async def get_all_with_counts(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Get all crops with their registry counts
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[dict]: Crops with counts
        """
        crops = await CropService.get_all(session, skip, limit)
        
        result = []
        for crop in crops:
            count = session.exec(
                select(func.count(CropRegistry.cropregistryid)) # type: ignore
                .where(
                    CropRegistry.croptypeid == crop.croptypeid,
                    CropRegistry.deletedat == None
                )
            ).first() or 0
            
            result.append({
                "croptypeid": crop.croptypeid,
                "name": crop.name,
                "registry_count": count,
                "createdat": crop.createdat
            })
        
        return result