"""
FILE: src/farmtypes/router.py
FarmType CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.farmtypes.services import FarmTypeService
from src.farmtypes.schemas import FarmTypeCreate, FarmTypeUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/farmtypes", tags=["Farm Types"])


@router.post("/create", response_model=ResponseModel)
async def create_farmtype(
    data: FarmTypeCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new farm type
    
    Requires authentication
    """
    farmtype = await FarmTypeService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="Farm type created successfully",
        data={
            "farmtypeid": farmtype.farmtypeid,
            "typename": farmtype.typename,
            "createdat": farmtype.createdat,
            "updatedat": farmtype.updatedat,
            "deletedat": farmtype.deletedat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_farmtypes(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all farm types with pagination
    
    Requires authentication
    """
    farmtypes = await FarmTypeService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "farmtypeid": ft.farmtypeid,
            "typename": ft.typename,
            "createdat": ft.createdat,
            "updatedat": ft.updatedat,
            "deletedat": ft.deletedat
        } for ft in farmtypes],
        total=len(farmtypes),
        tag=1
    )


@router.get("/with-counts", response_model=ResponseModel)
async def get_farmtypes_with_counts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all farm types with farm counts
    
    Requires authentication
    """
    farmtypes = await FarmTypeService.get_all_with_farm_counts(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=farmtypes,
        total=len(farmtypes),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_farmtypes(
    q: str = Query(..., min_length=2, description="Search query"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search farm types by name or description
    
    Requires authentication
    """
    farmtypes = await FarmTypeService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "farmtypeid": ft.farmtypeid,
            "typename": ft.typename,
            "createdat": ft.createdat
        } for ft in farmtypes],
        total=len(farmtypes),
        tag=1
    )


@router.get("/{farmtype_id}", response_model=ResponseModel)
async def get_farmtype(
    farmtype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get farm type by ID
    
    Requires authentication
    """
    farmtype = await FarmTypeService.get_by_id(farmtype_id, session)
    
    return ResponseModel(
        success=True,
        data={
            "farmtypeid": farmtype.farmtypeid,
            "typename": farmtype.typename,
            "createdat": farmtype.createdat,
            "updatedat": farmtype.updatedat,
            "deletedat": farmtype.deletedat
        },
        tag=1
    )


@router.get("/{farmtype_id}/stats", response_model=ResponseModel)
async def get_farmtype_stats(
    farmtype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get farm type with statistics (farm count)
    
    Requires authentication
    """
    data = await FarmTypeService.get_with_stats(farmtype_id, session)
    
    return ResponseModel(
        success=True,
        data=data,
        tag=1
    )


@router.put("/{farmtype_id}", response_model=ResponseModel)
async def update_farmtype(
    farmtype_id: int,
    data: FarmTypeUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update farm type
    
    Requires authentication
    """
    farmtype = await FarmTypeService.update(farmtype_id, data, session)
    
    return ResponseModel(
        success=True,
        message="Farm type updated successfully",
        data={
            "farmtypeid": farmtype.farmtypeid,
            "typename": farmtype.typename,
            "createdat": farmtype.createdat,
            "updatedat": farmtype.updatedat
        },
        tag=1
    )


@router.delete("/{farmtype_id}", response_model=ResponseModel)
async def delete_farmtype(
    farmtype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete farm type (soft delete)
    
    Requires authentication
    """
    await FarmTypeService.delete(farmtype_id, session)
    
    return ResponseModel(
        success=True,
        message="Farm type deleted successfully",
        tag=1
    )