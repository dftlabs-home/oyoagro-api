"""
FILE: src/lgas/services.py
Business logic for LGA operations
"""
from sqlmodel import Session, select
from src.shared.models import Lga, Region, Farmer, Address, Userprofile
from src.lgas.schemas import LgaCreate, LgaUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class LgaService:
    """Service class for LGA business logic"""
    
    @staticmethod
    async def create(data: LgaCreate, session: Session) -> Lga:
        """
        Create new LGA
        
        Args:
            data: LGA creation data
            session: Database session
            
        Returns:
            Lga: Created LGA
            
        Raises:
            HTTPException: If LGA name already exists or region not found
        """
        # Verify region exists
        region = session.get(Region, data.regionid)
        if not region or region.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region with ID {data.regionid} not found"
            )
        
        # Check for duplicate name in same region
        existing = session.exec(
            select(Lga).where(
                Lga.lganame == data.lganame,
                Lga.regionid == data.regionid,
                Lga.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"LGA '{data.lganame}' already exists in this region"
            )
        
        # Create LGA
        lga = Lga(
            lganame=data.lganame,
            regionid=data.regionid,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(lga)
        session.commit()
        session.refresh(lga)
        
        logger.info(f"Created LGA: {lga.lgaid} - {lga.lganame}")
        return lga
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        region_id: Optional[int] = None
    ) -> List[Lga]:
        """
        Get all active LGAs with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            region_id: Optional filter by region
            
        Returns:
            List[Lga]: List of LGAs
        """
        statement = select(Lga).where(Lga.deletedat == None)
        
        if region_id:
            statement = statement.where(Lga.regionid == region_id)
        
        statement = statement.offset(skip).limit(limit).order_by(Lga.lganame)
        
        lgas = session.exec(statement).all()
        return list(lgas)
    
    @staticmethod
    async def get_by_id(lga_id: int, session: Session) -> Lga:
        """
        Get LGA by ID
        
        Args:
            lga_id: LGA ID
            session: Database session
            
        Returns:
            Lga: Found LGA
            
        Raises:
            HTTPException: If LGA not found
        """
        lga = session.get(Lga, lga_id)
        
        if not lga or lga.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LGA with ID {lga_id} not found"
            )
        
        return lga
    
    @staticmethod
    async def get_by_region(region_id: int, session: Session) -> List[Lga]:
        """
        Get all LGAs in a region
        
        Args:
            region_id: Region ID
            session: Database session
            
        Returns:
            List[Lga]: LGAs in the region
        """
        # Verify region exists
        region = session.get(Region, region_id)
        if not region or region.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region with ID {region_id} not found"
            )
        
        statement = select(Lga).where(
            Lga.regionid == region_id,
            Lga.deletedat == None
        ).order_by(Lga.lganame)
        
        lgas = session.exec(statement).all()
        return list(lgas)
    
    @staticmethod
    async def get_with_stats(lga_id: int, session: Session) -> dict:
        """
        Get LGA with statistics
        
        Args:
            lga_id: LGA ID
            session: Database session
            
        Returns:
            dict: LGA with statistics
        """
        lga = await LgaService.get_by_id(lga_id, session)
        
        # Get region name
        region = session.get(Region, lga.regionid)
        
        # Count farmers in this LGA (via address)
        farmer_addresses = session.exec(
            select(Address).where(
                Address.lgaid == lga_id,
                Address.farmerid != None,
                Address.deletedat == None
            )
        ).all()
        
        # Count farms in this LGA (via address)
        farm_addresses = session.exec(
            select(Address).where(
                Address.lgaid == lga_id,
                Address.farmid != None,
                Address.deletedat == None
            )
        ).all()
        
        # Count officers assigned to this LGA
        officers = session.exec(
            select(Userprofile).where(
                Userprofile.lgaid == lga_id,
                Userprofile.deletedat == None
            )
        ).all()
        
        return {
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "regionname": region.regionname if region else None,
            "farmer_count": len(farmer_addresses),
            "farm_count": len(farm_addresses),
            "officer_count": len(officers),
            "createdat": lga.createdat,
            "updatedat": lga.updatedat
        }
    
    @staticmethod
    async def update(
        lga_id: int,
        data: LgaUpdate,
        session: Session
    ) -> Lga:
        """
        Update LGA
        
        Args:
            lga_id: LGA ID
            data: Update data
            session: Database session
            
        Returns:
            Lga: Updated LGA
            
        Raises:
            HTTPException: If LGA not found, duplicate name, or region not found
        """
        lga = await LgaService.get_by_id(lga_id, session)
        
        # Update region if provided
        if data.regionid and data.regionid != lga.regionid:
            region = session.get(Region, data.regionid)
            if not region or region.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Region with ID {data.regionid} not found"
                )
            lga.regionid = data.regionid
        
        # Update name if provided
        if data.lganame and data.lganame != lga.lganame:
            # Check for duplicate name in the region
            existing = session.exec(
                select(Lga).where(
                    Lga.lganame == data.lganame,
                    Lga.regionid == lga.regionid,
                    Lga.deletedat == None,
                    Lga.lgaid != lga_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"LGA '{data.lganame}' already exists in this region"
                )
            
            lga.lganame = data.lganame
        
        lga.updatedat = datetime.utcnow()
        lga.version = (lga.version or 0) + 1
        
        session.add(lga)
        session.commit()
        session.refresh(lga)
        
        logger.info(f"Updated LGA: {lga.lgaid}")
        return lga
    
    @staticmethod
    async def delete(lga_id: int, session: Session) -> None:
        """
        Soft delete LGA
        
        Args:
            lga_id: LGA ID
            session: Database session
            
        Raises:
            HTTPException: If LGA not found or has farmers/farms/officers
        """
        lga = await LgaService.get_by_id(lga_id, session)
        
        # Check if LGA has farmers
        farmer_addresses = session.exec(
            select(Address).where(
                Address.lgaid == lga_id,
                Address.farmerid != None,
                Address.deletedat == None
            )
        ).first()
        
        if farmer_addresses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete LGA with registered farmers"
            )
        
        # Check if LGA has farms
        farm_addresses = session.exec(
            select(Address).where(
                Address.lgaid == lga_id,
                Address.farmid != None,
                Address.deletedat == None
            )
        ).first()
        
        if farm_addresses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete LGA with registered farms"
            )
        
        # Check if LGA has officers
        officers = session.exec(
            select(Userprofile).where(
                Userprofile.lgaid == lga_id,
                Userprofile.deletedat == None
            )
        ).first()
        
        if officers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete LGA with assigned officers"
            )
        
        lga.deletedat = datetime.utcnow()
        session.add(lga)
        session.commit()
        
        logger.info(f"Deleted LGA: {lga_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        region_id: Optional[int] = None
    ) -> List[Lga]:
        """
        Search LGAs by name
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            region_id: Optional filter by region
            
        Returns:
            List[Lga]: Matching LGAs
        """
        statement = select(Lga).where(
            Lga.deletedat == None,
            Lga.lganame.ilike(f"%{query}%") # type: ignore
        )
        
        if region_id:
            statement = statement.where(Lga.regionid == region_id)
        
        statement = statement.offset(skip).limit(limit).order_by(Lga.lganame)
        
        lgas = session.exec(statement).all()
        return list(lgas)