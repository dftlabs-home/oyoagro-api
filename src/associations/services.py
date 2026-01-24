"""
FILE: src/associations/services.py
Business logic for Association operations
"""
from sqlmodel import Session, select
from src.shared.models import Association
from src.associations.schemas import AssociationCreate, AssociationUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AssociationService:
    """Service class for Association business logic"""
    
    @staticmethod
    async def create(data: AssociationCreate, session: Session) -> Association:
        """
        Create new association
        
        Args:
            data: Association creation data
            session: Database session
            
        Returns:
            Association: Created association
            
        Raises:
            HTTPException: If association name already exists
        """
        # Check for duplicate name
        existing = session.exec(
            select(Association).where(
                Association.name == data.name,
                Association.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Association with name '{data.name}' already exists"
            )
        
        # Check for duplicate registration number
        existing_reg = session.exec(
            select(Association).where(
                Association.registrationno == data.registrationno,
                Association.deletedat == None
            )
        ).first()
        
        if existing_reg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Association with registration number '{data.registrationno}' already exists"
            )
        
        # Create association
        association = Association(
            name=data.name,
            registrationno=data.registrationno,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(association)
        session.commit()
        session.refresh(association)
        
        logger.info(f"Created association: {association.associationid} - {association.name}")
        return association
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Association]:
        """
        Get all active associations with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Association]: List of associations
        """
        statement = select(Association).where(
            Association.deletedat == None
        ).offset(skip).limit(limit).order_by(Association.name)
        
        associations = session.exec(statement).all()
        return list(associations)
    
    @staticmethod
    async def get_by_id(association_id: int, session: Session) -> Association:
        """
        Get association by ID
        
        Args:
            association_id: Association ID
            session: Database session
            
        Returns:
            Association: Found association
            
        Raises:
            HTTPException: If association not found
        """
        association = session.get(Association, association_id)
        
        if not association or association.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Association with ID {association_id} not found"
            )
        
        return association
    
    @staticmethod
    async def update(
        association_id: int,
        data: AssociationUpdate,
        session: Session
    ) -> Association:
        """
        Update association
        
        Args:
            association_id: Association ID
            data: Update data
            session: Database session
            
        Returns:
            Association: Updated association
            
        Raises:
            HTTPException: If association not found or duplicate name/reg
        """
        association = await AssociationService.get_by_id(association_id, session)
        
        # Check for duplicate name if name is being updated
        if data.name and data.name != association.name:
            existing = session.exec(
                select(Association).where(
                    Association.name == data.name,
                    Association.deletedat == None,
                    Association.associationid != association_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Association with name '{data.name}' already exists"
                )
            
            association.name = data.name
        
        # Check for duplicate registration number if being updated
        if data.registrationno and data.registrationno != association.registrationno:
            existing_reg = session.exec(
                select(Association).where(
                    Association.registrationno == data.registrationno,
                    Association.deletedat == None,
                    Association.associationid != association_id
                )
            ).first()
            
            if existing_reg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Registration number '{data.registrationno}' already exists"
                )
            
            association.registrationno = data.registrationno
        
        association.updatedat = datetime.utcnow()
        association.version = (association.version or 0) + 1
        
        session.add(association)
        session.commit()
        session.refresh(association)
        
        logger.info(f"Updated association: {association.associationid}")
        return association
    
    @staticmethod
    async def delete(association_id: int, session: Session) -> None:
        """
        Soft delete association
        
        Args:
            association_id: Association ID
            session: Database session
            
        Raises:
            HTTPException: If association not found or has farmers
        """
        association = await AssociationService.get_by_id(association_id, session)
        
        # Check if association has farmers
        from src.shared.models import Farmer
        farmers_count = session.exec(
            select(Farmer).where(
                Farmer.associationid == association_id,
                Farmer.deletedat == None
            )
        ).first()
        
        if farmers_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete association with registered farmers"
            )
        
        association.deletedat = datetime.utcnow()
        session.add(association)
        session.commit()
        
        logger.info(f"Deleted association: {association_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Association]:
        """
        Search associations by name or registration number
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Association]: Matching associations
        """
        statement = select(Association).where(
            Association.deletedat == None,
            (Association.name.ilike(f"%{query}%")) |  # type: ignore
            (Association.registrationno.ilike(f"%{query}%")) # type: ignore
        ).offset(skip).limit(limit).order_by(Association.name)
        
        associations = session.exec(statement).all()
        return list(associations)