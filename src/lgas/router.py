"""
FILE: src/lgas/router.py
LGA CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount, Region
from src.shared.schemas import ResponseModel
from src.lgas.services import LgaService
from src.lgas.schemas import LgaCreate, LgaUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lgas", tags=["LGAs"])


@router.post("/create", response_model=ResponseModel)
async def create_lga(
    data: LgaCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new LGA
    
    Requires authentication
    """
    lga = await LgaService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="LGA created successfully",
        data={
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "createdat": lga.createdat,
            "updatedat": lga.updatedat,
            "deletedat": lga.deletedat,
            "version": lga.version
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_lgas(
    region_id: Optional[int] = Query(None, description="Filter by region ID"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all LGAs with pagination
    
    Optional filter by region_id
    Requires authentication
    """
    lgas = await LgaService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        region_id=region_id
    )
    
    # Get region names
    data = []
    for lga in lgas:
        region = session.get(Region, lga.regionid)
        data.append({
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "regionname": region.regionname if region else None,
            "createdat": lga.createdat,
            "updatedat": lga.updatedat,
            "deletedat": lga.deletedat,
            "version": lga.version
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/by-region/{region_id}", response_model=ResponseModel)
async def get_lgas_by_region(
    region_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all LGAs in a specific region
    
    Requires authentication
    """
    lgas = await LgaService.get_by_region(region_id, session)
    
    return ResponseModel(
        success=True,
        data=[{
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "createdat": lga.createdat
        } for lga in lgas],
        total=len(lgas),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_lgas(
    q: str = Query(..., min_length=2, description="Search query"),
    region_id: Optional[int] = Query(None, description="Filter by region ID"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search LGAs by name
    
    Optional filter by region_id
    Requires authentication
    """
    lgas = await LgaService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        region_id=region_id
    )
    
    # Get region names
    data = []
    for lga in lgas:
        region = session.get(Region, lga.regionid)
        data.append({
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "regionname": region.regionname if region else None,
            "createdat": lga.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/{lga_id}", response_model=ResponseModel)
async def get_lga(
    lga_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get LGA by ID
    
    Requires authentication
    """
    lga = await LgaService.get_by_id(lga_id, session)
    
    # Get region name
    region = session.get(Region, lga.regionid)
    
    return ResponseModel(
        success=True,
        data={
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "regionname": region.regionname if region else None,
            "createdat": lga.createdat,
            "updatedat": lga.updatedat,
            "deletedat": lga.deletedat,
            "version": lga.version
        },
        tag=1
    )


@router.get("/{lga_id}/stats", response_model=ResponseModel)
async def get_lga_stats(
    lga_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get LGA with statistics (farmer count, farm count, officer count)
    
    Requires authentication
    """
    data = await LgaService.get_with_stats(lga_id, session)
    
    return ResponseModel(
        success=True,
        data=data,
        tag=1
    )


@router.put("/{lga_id}", response_model=ResponseModel)
async def update_lga(
    lga_id: int,
    data: LgaUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update LGA
    
    Requires authentication
    """
    lga = await LgaService.update(lga_id, data, session)
    
    # Get region name
    region = session.get(Region, lga.regionid)
    
    return ResponseModel(
        success=True,
        message="LGA updated successfully",
        data={
            "lgaid": lga.lgaid,
            "lganame": lga.lganame,
            "regionid": lga.regionid,
            "regionname": region.regionname if region else None,
            "createdat": lga.createdat,
            "updatedat": lga.updatedat,
            "version": lga.version
        },
        tag=1
    )


@router.delete("/{lga_id}", response_model=ResponseModel)
async def delete_lga(
    lga_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete LGA (soft delete)
    
    Requires authentication
    """
    await LgaService.delete(lga_id, session)
    
    return ResponseModel(
        success=True,
        message="LGA deleted successfully",
        tag=1
    )