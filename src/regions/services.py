"""
FILE: src/regions/services.py
Business logic for Region operations
"""
from sqlmodel import Session, select
from src.shared.models import Region, Lga
from src.regions.schemas import RegionCreate, RegionUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class RegionService:
    """Service class for Region business logic"""
    
    @staticmethod
    async def create(data: RegionCreate, session: Session) -> Region:
        """
        Create new region
        
        Args:
            data: Region creation data
            session: Database session
            
        Returns:
            Region: Created region
            
        Raises:
            HTTPException: If region name already exists
        """
        # Check for duplicate name
        existing = session.exec(
            select(Region).where(
                Region.regionname == data.regionname,
                Region.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region '{data.regionname}' already exists"
            )
        
        # Create region
        region = Region(
            regionname=data.regionname,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(region)
        session.commit()
        session.refresh(region)
        
        logger.info(f"Created region: {region.regionid} - {region.regionname}")
        return region
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Region]:
        """
        Get all active regions with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Region]: List of regions
        """
        statement = select(Region).where(
            Region.deletedat == None
        ).offset(skip).limit(limit).order_by(Region.regionname)
        
        regions = session.exec(statement).all()
        return list(regions)
    
    @staticmethod
    async def get_by_id(region_id: int, session: Session) -> Region:
        """
        Get region by ID
        
        Args:
            region_id: Region ID
            session: Database session
            
        Returns:
            Region: Found region
            
        Raises:
            HTTPException: If region not found
        """
        region = session.get(Region, region_id)
        
        if not region or region.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region with ID {region_id} not found"
            )
        
        return region
    
    @staticmethod
    async def get_with_lgas(region_id: int, session: Session) -> dict:
        """
        Get region with its LGAs
        
        Args:
            region_id: Region ID
            session: Database session
            
        Returns:
            dict: Region with LGAs list
        """
        region = await RegionService.get_by_id(region_id, session)
        
        # Get LGAs in this region
        lgas = session.exec(
            select(Lga).where(
                Lga.regionid == region_id,
                Lga.deletedat == None
            ).order_by(Lga.lganame)
        ).all()
        
        return {
            "regionid": region.regionid,
            "regionname": region.regionname,
            "lga_count": len(lgas),
            "lgas": [{
                "lgaid": lga.lgaid,
                "lganame": lga.lganame,
                "createdat": lga.createdat
            } for lga in lgas],
            "createdat": region.createdat,
            "updatedat": region.updatedat
        }
    
    @staticmethod
    async def update(
        region_id: int,
        data: RegionUpdate,
        session: Session
    ) -> Region:
        """
        Update region
        
        Args:
            region_id: Region ID
            data: Update data
            session: Database session
            
        Returns:
            Region: Updated region
            
        Raises:
            HTTPException: If region not found or duplicate name
        """
        region = await RegionService.get_by_id(region_id, session)
        
        # Check for duplicate name if name is being updated
        if data.regionname and data.regionname != region.regionname:
            existing = session.exec(
                select(Region).where(
                    Region.regionname == data.regionname,
                    Region.deletedat == None,
                    Region.regionid != region_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Region '{data.regionname}' already exists"
                )
            
            region.regionname = data.regionname
        
        region.updatedat = datetime.utcnow()
        region.version = (region.version or 0) + 1
        
        session.add(region)
        session.commit()
        session.refresh(region)
        
        logger.info(f"Updated region: {region.regionid}")
        return region
    
    @staticmethod
    async def delete(region_id: int, session: Session) -> None:
        """
        Soft delete region
        
        Args:
            region_id: Region ID
            session: Database session
            
        Raises:
            HTTPException: If region not found or has LGAs
        """
        region = await RegionService.get_by_id(region_id, session)
        
        # Check if region has LGAs
        lgas_count = session.exec(
            select(Lga).where(
                Lga.regionid == region_id,
                Lga.deletedat == None
            )
        ).first()
        
        if lgas_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete region with existing LGAs"
            )
        
        region.deletedat = datetime.utcnow()
        session.add(region)
        session.commit()
        
        logger.info(f"Deleted region: {region_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Region]:
        """
        Search regions by name
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Region]: Matching regions
        """
        statement = select(Region).where(
            Region.deletedat == None,
            Region.regionname.ilike(f"%{query}%") # type: ignore
        ).offset(skip).limit(limit).order_by(Region.regionname)
        
        regions = session.exec(statement).all()
        return list(regions)
    
    @staticmethod
    async def get_all_with_lga_counts(
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Get all regions with their LGA counts
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[dict]: Regions with LGA counts
        """
        regions = await RegionService.get_all(session, skip, limit)
        
        result = []
        for region in regions:
            lga_count = len(session.exec(
                select(Lga).where(
                    Lga.regionid == region.regionid,
                    Lga.deletedat == None
                )
            ).all())
            
            result.append({
                "regionid": region.regionid,
                "regionname": region.regionname,
                "lga_count": lga_count,
                "createdat": region.createdat,
                "updatedat": region.updatedat
            })
        
        return result