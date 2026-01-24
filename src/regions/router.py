"""
FILE: src/regions/router.py
Region CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.regions.services import RegionService
from src.regions.schemas import RegionCreate, RegionUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/regions", tags=["Regions"])


@router.post("/create", response_model=ResponseModel)
async def create_region(
    data: RegionCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new region
    
    Requires authentication
    """
    region = await RegionService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="Region created successfully",
        data={
            "regionid": region.regionid,
            "regionname": region.regionname,
            "createdat": region.createdat,
            "updatedat": region.updatedat,
            "deletedat": region.deletedat,
            "version": region.version
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_regions(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all regions with pagination
    
    Requires authentication
    """
    regions = await RegionService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "regionid": r.regionid,
            "regionname": r.regionname,
            "createdat": r.createdat,
            "updatedat": r.updatedat,
            "deletedat": r.deletedat,
            "version": r.version
        } for r in regions],
        total=len(regions),
        tag=1
    )


@router.get("/with-lgas", response_model=ResponseModel)
async def get_regions_with_lgas(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all regions with LGA counts
    
    Requires authentication
    """
    regions = await RegionService.get_all_with_lga_counts(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=regions,
        total=len(regions),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_regions(
    q: str = Query(..., min_length=2, description="Search query"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search regions by name
    
    Requires authentication
    """
    regions = await RegionService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "regionid": r.regionid,
            "regionname": r.regionname,
            "createdat": r.createdat
        } for r in regions],
        total=len(regions),
        tag=1
    )


@router.get("/{region_id}", response_model=ResponseModel)
async def get_region(
    region_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get region by ID
    
    Requires authentication
    """
    region = await RegionService.get_by_id(region_id, session)
    
    return ResponseModel(
        success=True,
        data={
            "regionid": region.regionid,
            "regionname": region.regionname,
            "createdat": region.createdat,
            "updatedat": region.updatedat,
            "deletedat": region.deletedat,
            "version": region.version
        },
        tag=1
    )


@router.get("/{region_id}/lgas", response_model=ResponseModel)
async def get_region_with_lgas(
    region_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get region with all its LGAs
    
    Requires authentication
    """
    data = await RegionService.get_with_lgas(region_id, session)
    
    return ResponseModel(
        success=True,
        data=data,
        tag=1
    )


@router.put("/{region_id}", response_model=ResponseModel)
async def update_region(
    region_id: int,
    data: RegionUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update region
    
    Requires authentication
    """
    region = await RegionService.update(region_id, data, session)
    
    return ResponseModel(
        success=True,
        message="Region updated successfully",
        data={
            "regionid": region.regionid,
            "regionname": region.regionname,
            "createdat": region.createdat,
            "updatedat": region.updatedat,
            "version": region.version
        },
        tag=1
    )


@router.delete("/{region_id}", response_model=ResponseModel)
async def delete_region(
    region_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete region (soft delete)
    
    Requires authentication
    """
    await RegionService.delete(region_id, session)
    
    return ResponseModel(
        success=True,
        message="Region deleted successfully",
        tag=1
    )