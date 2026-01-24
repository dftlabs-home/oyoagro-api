"""
FILE: src/crops/router.py
Crop CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.crops.services import CropService
from src.crops.schemas import CropCreate, CropUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crops", tags=["Crops"])


@router.post("/create", response_model=ResponseModel)
async def create_crop(
    data: CropCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new crop type
    
    Requires authentication
    """
    crop = await CropService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="Crop created successfully",
        data={
            "croptypeid": crop.croptypeid,
            "name": crop.name,
            "createdat": crop.createdat,
            "updatedat": crop.updatedat,
            "deletedat": crop.deletedat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_crops(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all crops with pagination
    
    Requires authentication
    """
    crops = await CropService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "croptypeid": c.croptypeid,
            "name": c.name,
            "createdat": c.createdat,
            "updatedat": c.updatedat,
            "deletedat": c.deletedat
        } for c in crops],
        total=len(crops),
        tag=1
    )


@router.get("/with-counts", response_model=ResponseModel)
async def get_crops_with_counts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all crops with registry counts
    
    Requires authentication
    """
    crops = await CropService.get_all_with_counts(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=crops,
        total=len(crops),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_crops(
    q: str = Query(..., min_length=2, description="Search query"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search crops by name
    
    Requires authentication
    """
    crops = await CropService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "croptypeid": c.croptypeid,
            "name": c.name,
            "createdat": c.createdat
        } for c in crops],
        total=len(crops),
        tag=1
    )


@router.get("/{crop_id}", response_model=ResponseModel)
async def get_crop(
    crop_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get crop by ID
    
    Requires authentication
    """
    crop = await CropService.get_by_id(crop_id, session)
    
    return ResponseModel(
        success=True,
        data={
            "croptypeid": crop.croptypeid,
            "name": crop.name,
            "createdat": crop.createdat,
            "updatedat": crop.updatedat,
            "deletedat": crop.deletedat
        },
        tag=1
    )


@router.get("/{crop_id}/stats", response_model=ResponseModel)
async def get_crop_stats(
    crop_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get crop with statistics
    
    Requires authentication
    """
    data = await CropService.get_with_stats(crop_id, session)
    
    return ResponseModel(
        success=True,
        data=data,
        tag=1
    )


@router.put("/{crop_id}", response_model=ResponseModel)
async def update_crop(
    crop_id: int,
    data: CropUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update crop
    
    Requires authentication
    """
    crop = await CropService.update(crop_id, data, session)
    
    return ResponseModel(
        success=True,
        message="Crop updated successfully",
        data={
            "croptypeid": crop.croptypeid,
            "name": crop.name,
            "createdat": crop.createdat,
            "updatedat": crop.updatedat
        },
        tag=1
    )


@router.delete("/{crop_id}", response_model=ResponseModel)
async def delete_crop(
    crop_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete crop (soft delete)
    
    Requires authentication
    """
    await CropService.delete(crop_id, session)
    
    return ResponseModel(
        success=True,
        message="Crop deleted successfully",
        tag=1
    )