"""
FILE: src/cropregistry/router.py
CropRegistry CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.cropregistry.services import CropRegistryService
from src.cropregistry.schemas import CropRegistryCreate, CropRegistryUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cropregistry", tags=["Crop Registry"])


@router.post("/create", response_model=ResponseModel)
async def create_crop_registry(
    data: CropRegistryCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new crop registry
    
    Requires authentication
    """
    registry = await CropRegistryService.create(data, session)
    details = await CropRegistryService.get_with_details(registry.cropregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Crop registry created successfully",
        data=details,
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_crop_registries(
    farm_id: Optional[int] = Query(None, description="Filter by farm"),
    season_id: Optional[int] = Query(None, description="Filter by season"),
    crop_id: Optional[int] = Query(None, description="Filter by crop type"),
    farmer_id: Optional[int] = Query(None, description="Filter by farmer"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all crop registries with filters
    
    Requires authentication
    """
    registries = await CropRegistryService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        farm_id=farm_id,
        season_id=season_id,
        crop_id=crop_id,
        farmer_id=farmer_id
    )
    
    # Build response with details
    from src.shared.models import Farm, Season, Crop, Farmer
    
    data = []
    for registry in registries:
        # Get related entities
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        season = session.get(Season, registry.seasonid)
        crop = session.get(Crop, registry.croptypeid)
        
        # Determine status
        status = "Pending"
        if registry.harvestdate:
            status = "Harvested"
        elif registry.plantingdate:
            status = "Planted"
        
        data.append({
            "cropregistryid": registry.cropregistryid,
            "farmid": registry.farmid,
            "farmer_name": f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown",
            "crop_name": crop.name if crop else "Unknown",
            "cropvariety": registry.cropvariety,
            "season_name": season.name if season else "Unknown",
            "areaplanted": registry.areaplanted,
            "yieldquantity": registry.yieldquantity,
            "plantingdate": registry.plantingdate,
            "harvestdate": registry.harvestdate,
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
async def get_crop_registry_statistics(
    season_id: Optional[int] = Query(None, description="Filter by season"),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get crop registry statistics
    
    Requires authentication
    """
    stats = await CropRegistryService.get_statistics(session, season_id=season_id)
    
    return ResponseModel(
        success=True,
        data=stats,
        tag=1
    )


@router.get("/{registry_id}", response_model=ResponseModel)
async def get_crop_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get crop registry by ID with full details
    
    Requires authentication
    """
    details = await CropRegistryService.get_with_details(registry_id, session)
    
    return ResponseModel(
        success=True,
        data=details,
        tag=1
    )


@router.put("/{registry_id}", response_model=ResponseModel)
async def update_crop_registry(
    registry_id: int,
    data: CropRegistryUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update crop registry
    
    Requires authentication
    """
    registry = await CropRegistryService.update(registry_id, data, session)
    details = await CropRegistryService.get_with_details(registry.cropregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Crop registry updated successfully",
        data=details,
        tag=1
    )


@router.delete("/{registry_id}", response_model=ResponseModel)
async def delete_crop_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete crop registry (soft delete)
    
    Requires authentication
    """
    await CropRegistryService.delete(registry_id, session)
    
    return ResponseModel(
        success=True,
        message="Crop registry deleted successfully",
        tag=1
    )