"""
FILE: src/seasons/router.py
Season CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from datetime import date
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.seasons.services import SeasonService
from src.seasons.schemas import SeasonCreate, SeasonUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.post("/create", response_model=ResponseModel)
async def create_season(
    data: SeasonCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new season
    
    Requires authentication
    """
    season = await SeasonService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="Season created successfully",
        data={
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "createdat": season.createdat,
            "updatedat": season.updatedat,
            "deletedat": season.deletedat,
            "version": season.version
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_seasons(
    year: Optional[int] = Query(None, description="Filter by year"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all seasons with pagination
    
    Optional filter by year
    Requires authentication
    """
    seasons = await SeasonService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        year=year
    )
    
    # Add is_active flag
    today = date.today()
    data = []
    for season in seasons:
        is_active = season.startdate <= today <= season.enddate # type: ignore
        data.append({
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": is_active,
            "createdat": season.createdat,
            "updatedat": season.updatedat,
            "deletedat": season.deletedat,
            "version": season.version
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/active", response_model=ResponseModel)
async def get_active_season(
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get currently active season
    
    Requires authentication
    """
    season = await SeasonService.get_active_season(session)
    
    if not season:
        return ResponseModel(
            success=True,
            data={
                "is_active": False,
                "message": "No active season found"
            },
            tag=0
        )
    
    today = date.today()
    days_remaining = (season.enddate - today).days # type: ignore
    
    return ResponseModel(
        success=True,
        data={
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": True,
            "days_remaining": days_remaining,
            "createdat": season.createdat
        },
        tag=1
    )


@router.get("/year/{year}", response_model=ResponseModel)
async def get_seasons_by_year(
    year: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all seasons in a specific year
    
    Requires authentication
    """
    seasons = await SeasonService.get_by_year(year, session)
    
    today = date.today()
    data = []
    for season in seasons:
        is_active = season.startdate <= today <= season.enddate # type: ignore
        data.append({
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": is_active,
            "createdat": season.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_seasons(
    q: str = Query(..., min_length=2, description="Search query"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search seasons by name
    
    Requires authentication
    """
    seasons = await SeasonService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "seasonid": s.seasonid,
            "name": s.name,
            "year": s.year,
            "startdate": s.startdate,
            "enddate": s.enddate,
            "createdat": s.createdat
        } for s in seasons],
        total=len(seasons),
        tag=1
    )


@router.get("/{season_id}", response_model=ResponseModel)
async def get_season(
    season_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get season by ID
    
    Requires authentication
    """
    season = await SeasonService.get_by_id(season_id, session)
    
    today = date.today()
    is_active = season.startdate <= today <= season.enddate # type: ignore
    
    return ResponseModel(
        success=True,
        data={
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": is_active,
            "createdat": season.createdat,
            "updatedat": season.updatedat,
            "deletedat": season.deletedat,
            "version": season.version
        },
        tag=1
    )


@router.get("/{season_id}/stats", response_model=ResponseModel)
async def get_season_stats(
    season_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get season with statistics
    
    Requires authentication
    """
    data = await SeasonService.get_with_stats(season_id, session)
    
    return ResponseModel(
        success=True,
        data=data,
        tag=1
    )


@router.put("/{season_id}", response_model=ResponseModel)
async def update_season(
    season_id: int,
    data: SeasonUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update season
    
    Requires authentication
    """
    season = await SeasonService.update(season_id, data, session)
    
    today = date.today()
    is_active = season.startdate <= today <= season.enddate # type: ignore
    
    return ResponseModel(
        success=True,
        message="Season updated successfully",
        data={
            "seasonid": season.seasonid,
            "name": season.name,
            "year": season.year,
            "startdate": season.startdate,
            "enddate": season.enddate,
            "is_active": is_active,
            "createdat": season.createdat,
            "updatedat": season.updatedat,
            "version": season.version
        },
        tag=1
    )


@router.delete("/{season_id}", response_model=ResponseModel)
async def delete_season(
    season_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete season (soft delete)
    
    Requires authentication
    """
    await SeasonService.delete(season_id, session)
    
    return ResponseModel(
        success=True,
        message="Season deleted successfully",
        tag=1
    )