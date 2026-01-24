"""
FILE: src/businesstypes/router.py
BusinessType CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.businesstypes.services import BusinessTypeService
from src.businesstypes.schemas import BusinessTypeCreate, BusinessTypeUpdate

router = APIRouter(prefix="/businesstypes", tags=["Business Types"])


@router.post("/create", response_model=ResponseModel)
async def create_businesstype(
    data: BusinessTypeCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Create new business type"""
    businesstype = await BusinessTypeService.create(data, session)
    return ResponseModel(
        success=True,
        message="Business type created successfully",
        data={
            "businesstypeid": businesstype.businesstypeid,
            "name": businesstype.name,
            "createdat": businesstype.createdat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_businesstypes(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get all business types"""
    businesstypes = await BusinessTypeService.get_all(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "businesstypeid": bt.businesstypeid,
            "name": bt.name,
            "createdat": bt.createdat
        } for bt in businesstypes],
        total=len(businesstypes),
        tag=1
    )


@router.get("/with-counts", response_model=ResponseModel)
async def get_businesstypes_with_counts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get business types with registry counts"""
    businesstypes = await BusinessTypeService.get_all_with_counts(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(success=True, data=businesstypes, total=len(businesstypes), tag=1)


@router.get("/search", response_model=ResponseModel)
async def search_businesstypes(
    q: str = Query(..., min_length=2),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Search business types"""
    businesstypes = await BusinessTypeService.search(
        q, session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{"businesstypeid": bt.businesstypeid, "name": bt.name} for bt in businesstypes],
        total=len(businesstypes),
        tag=1
    )


@router.get("/{businesstype_id}", response_model=ResponseModel)
async def get_businesstype(
    businesstype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get business type by ID"""
    businesstype = await BusinessTypeService.get_by_id(businesstype_id, session)
    return ResponseModel(
        success=True,
        data={"businesstypeid": businesstype.businesstypeid, "name": businesstype.name},
        tag=1
    )


@router.get("/{businesstype_id}/stats", response_model=ResponseModel)
async def get_businesstype_stats(
    businesstype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get business type with statistics"""
    data = await BusinessTypeService.get_with_stats(businesstype_id, session)
    return ResponseModel(success=True, data=data, tag=1)


@router.put("/{businesstype_id}", response_model=ResponseModel)
async def update_businesstype(
    businesstype_id: int,
    data: BusinessTypeUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Update business type"""
    businesstype = await BusinessTypeService.update(businesstype_id, data, session)
    return ResponseModel(
        success=True,
        message="Business type updated successfully",
        data={"businesstypeid": businesstype.businesstypeid, "name": businesstype.name},
        tag=1
    )


@router.delete("/{businesstype_id}", response_model=ResponseModel)
async def delete_businesstype(
    businesstype_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Delete business type"""
    await BusinessTypeService.delete(businesstype_id, session)
    return ResponseModel(success=True, message="Business type deleted successfully", tag=1)
