"""
FILE: src/farmers/router.py
Farmer CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount, Association, Lga
from src.shared.schemas import ResponseModel
from src.farmers.services import FarmerService
from src.farmers.schemas import FarmerCreate, FarmerUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.post("/create", response_model=ResponseModel)
async def create_farmer(
    data: FarmerCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Create new farmer with address"""
    farmer = await FarmerService.create(data, session, current_user)
    details = await FarmerService.get_with_details(farmer.farmerid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Farmer created successfully",
        data=details,
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_farmers(
    association_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get all farmers with filters"""
    farmers = await FarmerService.get_all(
        session, pagination["skip"], pagination["limit"],
        association_id, lga_id, user_id
    )
    
    data = []
    for farmer in farmers:
        address = FarmerService._get_farmer_address(farmer.farmerid, session) # type: ignore
        association_name = None
        if farmer.associationid:
            assoc = session.get(Association, farmer.associationid)
            if assoc:
                association_name = assoc.name
        
        lga_name = None
        if address:
            lga = session.get(Lga, address.lgaid)
            if lga:
                lga_name = lga.lganame
        
        from src.shared.models import Farm
        from sqlmodel import select
        farm_count = len(session.exec(
            select(Farm).where(Farm.farmerid == farmer.farmerid, Farm.deletedat == None)
        ).all())
        
        age = FarmerService._calculate_age(farmer.dateofbirth) # type: ignore
        fullname = f"{farmer.firstname} {farmer.middlename or ''} {farmer.lastname}".strip()
        
        data.append({
            "farmerid": farmer.farmerid,
            "firstname": farmer.firstname,
            "middlename": farmer.middlename,
            "lastname": farmer.lastname,
            "fullname": fullname,
            "gender": farmer.gender,
            "age": age,
            "phonenumber": farmer.phonenumber,
            "association_name": association_name,
            "lga": lga_name,
            "farm_count": farm_count,
            "createdat": farmer.createdat
        })
    
    return ResponseModel(success=True, data=data, total=len(data), tag=1)


@router.get("/statistics", response_model=ResponseModel)
async def get_farmer_statistics(
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get farmer statistics"""
    stats = await FarmerService.get_statistics(session)
    return ResponseModel(success=True, data=stats, tag=1)


@router.get("/search", response_model=ResponseModel)
async def search_farmers(
    q: str = Query(..., min_length=2),
    association_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Search farmers"""
    farmers = await FarmerService.search(
        q, session, pagination["skip"], pagination["limit"],
        association_id, lga_id
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "farmerid": f.farmerid,
            "firstname": f.firstname,
            "middlename": f.middlename,
            "lastname": f.lastname,
            "phonenumber": f.phonenumber,
            "email": f.email,
            "createdat": f.createdat
        } for f in farmers],
        total=len(farmers),
        tag=1
    )


@router.get("/{farmer_id}", response_model=ResponseModel)
async def get_farmer(
    farmer_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get farmer by ID"""
    details = await FarmerService.get_with_details(farmer_id, session)
    return ResponseModel(success=True, data=details, tag=1)


@router.put("/{farmer_id}", response_model=ResponseModel)
async def update_farmer(
    farmer_id: int,
    data: FarmerUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Update farmer"""
    farmer = await FarmerService.update(farmer_id, data, session)
    details = await FarmerService.get_with_details(farmer.farmerid, session) # type: ignore
    
    return ResponseModel(
        success=True,
        message="Farmer updated successfully",
        data=details,
        tag=1
    )


@router.delete("/{farmer_id}", response_model=ResponseModel)
async def delete_farmer(
    farmer_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Delete farmer"""
    await FarmerService.delete(farmer_id, session)
    return ResponseModel(success=True, message="Farmer deleted successfully", tag=1)