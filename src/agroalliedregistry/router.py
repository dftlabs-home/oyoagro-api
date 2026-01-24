"""
FILE: src/agroalliedregistry/router.py
AgroAlliedRegistry CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.agroalliedregistry.services import AgroAlliedRegistryService
from src.agroalliedregistry.schemas import AgroAlliedRegistryCreate, AgroAlliedRegistryUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agroalliedregistry", tags=["Agro-Allied Registry"])


@router.post("/create", response_model=ResponseModel)
async def create_agroallied_registry(
    data: AgroAlliedRegistryCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Create new agro-allied registry"""
    registry = await AgroAlliedRegistryService.create(data, session)
    details = await AgroAlliedRegistryService.get_with_details(registry.agroalliedregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Agro-allied registry created successfully",
        data=details,
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_agroallied_registries(
    farm_id: Optional[int] = Query(None, description="Filter by farm"),
    season_id: Optional[int] = Query(None, description="Filter by season"),
    businesstype_id: Optional[int] = Query(None, description="Filter by business type"),
    product_id: Optional[int] = Query(None, description="Filter by primary product"),
    farmer_id: Optional[int] = Query(None, description="Filter by farmer"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get all agro-allied registries with filters"""
    registries = await AgroAlliedRegistryService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"],
        farm_id=farm_id,
        season_id=season_id,
        businesstype_id=businesstype_id,
        product_id=product_id,
        farmer_id=farmer_id
    )
    
    # Build response with details
    from src.shared.models import Farm, Season, BusinessType, PrimaryProduct, Farmer
    
    data = []
    for registry in registries:
        farm = session.get(Farm, registry.farmid)
        farmer = session.get(Farmer, farm.farmerid) if farm else None
        season = session.get(Season, registry.seasonid)
        businesstype = session.get(BusinessType, registry.businesstypeid)
        product = session.get(PrimaryProduct, registry.primaryproducttypeid)
        
        data.append({
            "agroalliedregistryid": registry.agroalliedregistryid,
            "farmid": registry.farmid,
            "farmer_name": f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown",
            "season_name": season.name if season else "Unknown",
            "business_type_name": businesstype.name if businesstype else "Unknown",
            "primary_product_name": product.name if product else "Unknown",
            "productioncapacity": registry.productioncapacity,
            "createdat": registry.createdat
        })
    
    return ResponseModel(
        success=True,
        data=data,
        total=len(data),
        tag=1
    )


@router.get("/statistics", response_model=ResponseModel)
async def get_agroallied_registry_statistics(
    season_id: Optional[int] = Query(None, description="Filter by season"),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get agro-allied registry statistics"""
    stats = await AgroAlliedRegistryService.get_statistics(session, season_id=season_id)
    
    return ResponseModel(
        success=True,
        data=stats,
        tag=1
    )


@router.get("/{registry_id}", response_model=ResponseModel)
async def get_agroallied_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get agro-allied registry by ID with full details"""
    details = await AgroAlliedRegistryService.get_with_details(registry_id, session)
    
    return ResponseModel(
        success=True,
        data=details,
        tag=1
    )


@router.put("/{registry_id}", response_model=ResponseModel)
async def update_agroallied_registry(
    registry_id: int,
    data: AgroAlliedRegistryUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Update agro-allied registry"""
    registry = await AgroAlliedRegistryService.update(registry_id, data, session)
    details = await AgroAlliedRegistryService.get_with_details(registry.agroalliedregistryid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Agro-allied registry updated successfully",
        data=details,
        tag=1
    )


@router.delete("/{registry_id}", response_model=ResponseModel)
async def delete_agroallied_registry(
    registry_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Delete agro-allied registry (soft delete)"""
    await AgroAlliedRegistryService.delete(registry_id, session)
    
    return ResponseModel(
        success=True,
        message="Agro-allied registry deleted successfully",
        tag=1
    )
