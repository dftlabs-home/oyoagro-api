"""
FILE: src/seasons/services.py
Business logic for Season operations
"""
from sqlmodel import Session, select
from src.shared.models import Season, AgroAlliedRegistry, CropRegistry, LivestockRegistry
from src.seasons.schemas import SeasonCreate, SeasonUpdate
from datetime import datetime, date
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SeasonService:
    """Service class for Season business logic"""
    
    @staticmethod
    async def create(data: SeasonCreate, session: Session) -> Season:
        """
        Create new season
        
        Args:
            data: Season creation data
            session: Database session
            
        Returns:
            Season: Created season
            
        Raises:
            HTTPException: If season name already exists or dates overlap
        """
        # Check for duplicate name
        existing = session.exec(
            select(Season).where(
                Season.name == data.name,
                Season.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Season '{data.name}' already exists"
            )
        
        # Check for overlapping seasons in the same year
        overlapping = session.exec(
            select(Season).where(
                Season.year == data.year,
                Season.deletedat == None,
                Season.startdate <= data.enddate, # type: ignore 
                Season.enddate >= data.startdate # type: ignore
            )
        ).first()
        
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Season dates overlap with existing season: {overlapping.name}"
            )
        
        # Create season
        season = Season(
            name=data.name,
            year=data.year,
            startdate=data.startdate,
            enddate=data.enddate,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(season)
        session.commit()
        session.refresh(season)
        
        logger.info(f"Created season: {season.seasonid} - {season.name}")
        return season
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        year: Optional[int] = None
    ) -> List[Season]:
        """
        Get all active seasons with pagination
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            year: Optional filter by year
            
        Returns:
            List[Season]: List of seasons
        """
        statement = select(Season).where(Season.deletedat == None)
        
        if year:
            statement = statement.where(Season.year == year)
        
        statement = statement.offset(skip).limit(limit).order_by(
            Season.year.desc(), Season.startdate.desc() # type: ignore
        )
        
        seasons = session.exec(statement).all()
        return list(seasons)
    
    @staticmethod
    async def get_by_id(season_id: int, session: Session) -> Season:
        """
        Get season by ID
        
        Args:
            season_id: Season ID
            session: Database session
            
        Returns:
            Season: Found season
            
        Raises:
            HTTPException: If season not found
        """
        season = session.get(Season, season_id)
        
        if not season or season.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Season with ID {season_id} not found"
            )
        
        return season
    
    @staticmethod
    async def get_active_season(session: Session) -> Optional[Season]:
        """
        Get currently active season
        
        Args:
            session: Database session
            
        Returns:
            Optional[Season]: Active season or None
        """
        today = date.today()
        
        statement = select(Season).where(
            Season.deletedat == None,
            Season.startdate <= today, # type: ignore
            Season.enddate >= today # type: ignore
        ).order_by(Season.startdate.desc()) # type: ignore
        
        season = session.exec(statement).first()
        return season
    
    @staticmethod
    async def get_by_year(year: int, session: Session) -> List[Season]:
        """
        Get all seasons in a specific year
        
        Args:
            year: Year
            session: Database session
            
        Returns:
            List[Season]: Seasons in the year
        """
        statement = select(Season).where(
            Season.year == year,
            Season.deletedat == None
        ).order_by(Season.startdate) # type: ignore
        
        seasons = session.exec(statement).all()
        return list(seasons)
    
    @staticmethod
    async def get_with_stats(season_id: int, session: Session) -> dict:
        """
        Get season with statistics
        
        Args:
            season_id: Season ID
            session: Database session
            
        Returns:
            dict: Season with statistics
        """
        season = await SeasonService.get_by_id(season_id, session)
        
        # Check if season is currently active
        today = date.today()
        is_active = season.startdate <= today <= season.enddate # type: ignore
        days_remaining = (season.enddate - today).days if is_active else None # type: ignore
        
        
        # Count crop registries
        crop_count = len(session.exec(
            select(CropRegistry).where(
                CropRegistry.seasonid == season_id,
                CropRegistry.deletedat == None
            )
        ).all())
        
        # Count livestock registries
        livestock_count = len(session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.seasonid == season_id,
                LivestockRegistry.deletedat == None
            )
        ).all())
        
        # Count agro-allied registries
        agroallied_count = len(session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.seasonid == season_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).all())
        
        return {
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": is_active,
            "days_remaining": days_remaining,
            "crop_registry_count": crop_count,
            "livestock_registry_count": livestock_count,
            "agroallied_registry_count": agroallied_count,
            "createdat": season.createdat,
            "updatedat": season.updatedat
        }
    
    @staticmethod
    async def update(
        season_id: int,
        data: SeasonUpdate,
        session: Session
    ) -> Season:
        """
        Update season
        
        Args:
            season_id: Season ID
            data: Update data
            session: Database session
            
        Returns:
            Season: Updated season
            
        Raises:
            HTTPException: If season not found, duplicate name, or invalid dates
        """
        season = await SeasonService.get_by_id(season_id, session)
        
        # Update name if provided
        if data.name and data.name != season.name:
            existing = session.exec(
                select(Season).where(
                    Season.name == data.name,
                    Season.deletedat == None,
                    Season.seasonid != season_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Season '{data.name}' already exists"
                )
            
            season.name = data.name
        
        # Update dates
        new_startdate = data.startdate if data.startdate else season.startdate
        new_enddate = data.enddate if data.enddate else season.enddate
        new_year = data.year if data.year else season.year
        
        # Validate dates
        if new_enddate <= new_startdate: # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        # Check for overlapping seasons
        if data.startdate or data.enddate or data.year:
            overlapping = session.exec(
                select(Season).where(
                    Season.year == new_year,
                    Season.deletedat == None,
                    Season.seasonid != season_id,
                    Season.startdate <= new_enddate, # type: ignore
                    Season.enddate >= new_startdate # type: ignore
                )
            ).first()
            
            if overlapping:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Season dates overlap with: {overlapping.name}"
                )
        
        if data.startdate:
            season.startdate = data.startdate
        if data.enddate:
            season.enddate = data.enddate
        if data.year:
            season.year = data.year
        
        season.updatedat = datetime.utcnow()
        season.version = (season.version or 0) + 1
        
        session.add(season)
        session.commit()
        session.refresh(season)
        
        logger.info(f"Updated season: {season.seasonid}")
        return season
    
    @staticmethod
    async def delete(season_id: int, session: Session) -> None:
        """
        Soft delete season
        
        Args:
            season_id: Season ID
            session: Database session
            
        Raises:
            HTTPException: If season not found or has registries
        """
        season = await SeasonService.get_by_id(season_id, session)
        
        # Check if season has crop registries
        crop_registries = session.exec(
            select(CropRegistry).where(
                CropRegistry.seasonid == season_id,
                CropRegistry.deletedat == None
            )
        ).first()
        
        if crop_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete season with crop registries"
            )
        
        # Check if season has livestock registries
        livestock_registries = session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.seasonid == season_id,
                LivestockRegistry.deletedat == None
            )
        ).first()
        
        if livestock_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete season with livestock registries"
            )
        
        # Check if season has agro-allied registries
        agroallied_registries = session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.seasonid == season_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first()
        
        if agroallied_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete season with agro-allied registries"
            )
        
        season.deletedat = datetime.utcnow()
        session.add(season)
        session.commit()
        
        logger.info(f"Deleted season: {season_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Season]:
        """
        Search seasons by name
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Season]: Matching seasons
        """
        statement = select(Season).where(
            Season.deletedat == None,
            Season.name.ilike(f"%{query}%") # type: ignore
        ).offset(skip).limit(limit).order_by(Season.year.desc(), Season.startdate.desc()) # type: ignore
        
        seasons = session.exec(statement).all()
        return list(seasons)