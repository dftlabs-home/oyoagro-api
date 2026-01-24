"""
FILE: src/livestockregistry/router.py
LivestockRegistry CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.livestockregistry.services import LivestockRegistryService
from src.livestockregistry.schemas import LivestockRegistryCreate, LivestockRegistryUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/livestockregistry", tags=["Livestock Registry"])


@router.post("/create", response_model=ResponseModel)
async def create_livestock_registry(
    data: LivestockRegistryCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Create new livestock registry"""
    registry = await LivestockRegistryService.create(data, session)
    details = await LivestockRegistryService.get_with_details(registry.livestockregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Livestock registry created successfully",
        data=details,
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_livestock_registries(
    farm_id: Optional[int] = Query(None, description="Filter by farm"),
    season_id: Optional[int] = Query(None, description="Filter by season"),
    livestock_id: Optional[int] = Query(None, description="Filter by livestock type"),
    farmer_id: Optional[int] = Query(None, description="Filter by farmer"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get all livestock registries with filters"""
    registries = await LivestockRegistryService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        farm_id=farm_id,
        season_id=season_id,
        livestock_id=livestock_id,
        farmer_id=farmer_id
    )
    
    # Build response with details
    from src.shared.models import Farm, Season, Livestock, Farmer
    from datetime import date
    
    data = []
    for registry in registries:
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        season = session.get(Season, registry.seasonid)
        livestock = session.get(Livestock, registry.livestocktypeid)
        
        status = "Active"
        if registry.enddate and registry.enddate <= date.today():
            status = "Completed"
        
        data.append({
            "livestockregistryid": registry.livestockregistryid,
            "farmid": registry.farmid,
            "farmer_name": f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown",
            "livestock_name": livestock.name if livestock else "Unknown",
            "season_name": season.name if season else "Unknown",
            "quantity": registry.quantity,
            "startdate": registry.startdate,
            "enddate": registry.enddate,
            "status": status,
            "createdat": registry.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/statistics", response_model=ResponseModel)
async def get_livestock_registry_statistics(
    season_id: Optional[int] = Query(None, description="Filter by season"),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get livestock registry statistics"""
    stats = await LivestockRegistryService.get_statistics(session, season_id=season_id)
    
    return ResponseModel(
        success=True,
        data=stats,
        tag=1
    )


@router.get("/{registry_id}", response_model=ResponseModel)
async def get_livestock_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get livestock registry by ID with full details"""
    details = await LivestockRegistryService.get_with_details(registry_id, session)
    
    return ResponseModel(
        success=True,
        data=details,
        tag=1
    )


@router.put("/{registry_id}", response_model=ResponseModel)
async def update_livestock_registry(
    registry_id: int,
    data: LivestockRegistryUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Update livestock registry"""
    registry = await LivestockRegistryService.update(registry_id, data, session)
    details = await LivestockRegistryService.get_with_details(registry.livestockregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Livestock registry updated successfully",
        data=details,
        tag=1
    )


@router.delete("/{registry_id}", response_model=ResponseModel)
async def delete_livestock_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Delete livestock registry (soft delete)"""
    await LivestockRegistryService.delete(registry_id, session)
    
    return ResponseModel(
        success=True,
        message="Livestock registry deleted successfully",
        tag=1
    )
