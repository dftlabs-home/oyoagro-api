"""
FILE: src/farms/router.py
Farm CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount, Farmer, Farmtype, Lga
from src.shared.schemas import ResponseModel
from src.farms.services import FarmService
from src.farms.schemas import FarmCreate, FarmUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("/create", response_model=ResponseModel)
async def create_farm(
    data: FarmCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new farm with address
    
    Requires authentication
    """
    farm = await FarmService.create(data, session)
    details = await FarmService.get_with_details(farm.farmid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Farm created successfully",
        data=details,
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_farms(
    farmer_id: Optional[int] = Query(None, description="Filter by farmer"),
    farmtype_id: Optional[int] = Query(None, description="Filter by farm type"),
    lga_id: Optional[int] = Query(None, description="Filter by LGA"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all farms with pagination and filters
    
    Requires authentication
    """
    farms = await FarmService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        farmer_id=farmer_id,
        farmtype_id=farmtype_id,
        lga_id=lga_id
    )
    
    # Build response with additional info
    data = []
    for farm in farms:
        # Get address
        address = FarmService._get_farm_address(farm.farmid, session) # type: ignore
        
        # Get farmer name
        farmer = session.get(Farmer, farm.farmerid)
        farmer_name = f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown"
        
        # Get farm type name
        farmtype = session.get(Farmtype, farm.farmtypeid)
        farmtype_name = farmtype.typename if farmtype else "Unknown"
        
        # Get LGA name
        lga_name = None
        if address:
            lga = session.get(Lga, address.lgaid)
            if lga:
                lga_name = lga.lganame
        
        # Count registries
        from src.shared.models import CropRegistry, LivestockRegistry, AgroAlliedRegistry
        from sqlmodel import select
        
        registry_count = 0
        registry_count += len(session.exec(
            select(CropRegistry).where(
                CropRegistry.farmid == farm.farmid,
                CropRegistry.deletedat == None
            )
        ).all())
        registry_count += len(session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.farmid == farm.farmid,
                LivestockRegistry.deletedat == None
            )
        ).all())
        registry_count += len(session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.farmid == farm.farmid,
                AgroAlliedRegistry.deletedat == None
            )
        ).all())
        
        data.append({
            "farmid": farm.farmid,
            "farmerid": farm.farmerid,
            "farmer_name": farmer_name,
            "farmtypeid": farm.farmtypeid,
            "farmtype_name": farmtype_name,
            "farmsize": farm.farmsize,
            "lga": lga_name,
            "registry_count": registry_count,
            "createdat": farm.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/statistics", response_model=ResponseModel)
async def get_farm_statistics(
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get farm statistics
    
    Requires authentication
    """
    stats = await FarmService.get_statistics(session)
    
    return ResponseModel(
        success=True,
        data=stats,
        tag=1
    )


@router.get("/by-farmer/{farmer_id}", response_model=ResponseModel)
async def get_farms_by_farmer(
    farmer_id: int,
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all farms for a specific farmer
    
    Requires authentication
    """
    farms = await FarmService.get_by_farmer(
        farmer_id,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    # Get details for each farm
    data = []
    for farm in farms:
        farmtype = session.get(Farmtype, farm.farmtypeid)
        farmtype_name = farmtype.typename if farmtype else "Unknown"
        
        data.append({
            "farmid": farm.farmid,
            "farmtypeid": farm.farmtypeid,
            "farmtype_name": farmtype_name,
            "farmsize": farm.farmsize,
            "createdat": farm.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/{farm_id}", response_model=ResponseModel)
async def get_farm(
    farm_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get farm by ID with full details
    
    Requires authentication
    """
    details = await FarmService.get_with_details(farm_id, session)
    
    return ResponseModel(
        success=True,
        data=details,
        tag=1
    )


@router.put("/{farm_id}", response_model=ResponseModel)
async def update_farm(
    farm_id: int,
    data: FarmUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update farm
    
    Requires authentication
    """
    farm = await FarmService.update(farm_id, data, session)
    
    # Get full details for response
    details = await FarmService.get_with_details(farm.farmid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Farm updated successfully",
        data=details,
        tag=1
    )


@router.delete("/{farm_id}", response_model=ResponseModel)
async def delete_farm(
    farm_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete farm (soft delete)
    
    Requires authentication
    """
    await FarmService.delete(farm_id, session)
    
    return ResponseModel(
        success=True,
        message="Farm deleted successfully",
        tag=1
    )