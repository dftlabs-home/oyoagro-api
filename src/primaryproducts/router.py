"""
FILE: src/primaryproducts/router.py
PrimaryProduct CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.primaryproducts.services import PrimaryProductService
from src.primaryproducts.schemas import PrimaryProductCreate, PrimaryProductUpdate

router = APIRouter(prefix="/primaryproducts", tags=["Primary Products"])


@router.post("/", response_model=ResponseModel)
async def create_primaryproduct(
    data: PrimaryProductCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Create new primary product"""
    product = await PrimaryProductService.create(data, session)
    return ResponseModel(
        success=True,
        message="Primary product created successfully",
        data={
            "primaryproducttypeid": product.primaryproducttypeid,
            "name": product.name,
            "createdat": product.createdat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_primaryproducts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get all primary products"""
    products = await PrimaryProductService.get_all(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "primaryproducttypeid": p.primaryproducttypeid,
            "name": p.name,
            "createdat": p.createdat
        } for p in products],
        total=len(products),
        tag=1
    )


@router.get("/with-counts", response_model=ResponseModel)
async def get_primaryproducts_with_counts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get primary products with registry counts"""
    products = await PrimaryProductService.get_all_with_counts(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(success=True, data=products, total=len(products), tag=1)


@router.get("/search", response_model=ResponseModel)
async def search_primaryproducts(
    q: str = Query(..., min_length=2),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Search primary products"""
    products = await PrimaryProductService.search(
        q, session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{"primaryproducttypeid": p.primaryproducttypeid, "name": p.name} for p in products],
        total=len(products),
        tag=1
    )


@router.get("/{product_id}", response_model=ResponseModel)
async def get_primaryproduct(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get primary product by ID"""
    product = await PrimaryProductService.get_by_id(product_id, session)
    return ResponseModel(
        success=True,
        data={"primaryproducttypeid": product.primaryproducttypeid, "name": product.name},
        tag=1
    )


@router.get("/{product_id}/stats", response_model=ResponseModel)
async def get_primaryproduct_stats(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Get primary product with statistics"""
    data = await PrimaryProductService.get_with_stats(product_id, session)
    return ResponseModel(success=True, data=data, tag=1)


@router.put("/{product_id}", response_model=ResponseModel)
async def update_primaryproduct(
    product_id: int,
    data: PrimaryProductUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Update primary product"""
    product = await PrimaryProductService.update(product_id, data, session)
    return ResponseModel(
        success=True,
        message="Primary product updated successfully",
        data={"primaryproducttypeid": product.primaryproducttypeid, "name": product.name},
        tag=1
    )


@router.delete("/{product_id}", response_model=ResponseModel)
async def delete_primaryproduct(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """Delete primary product"""
    await PrimaryProductService.delete(product_id, session)
    return ResponseModel(success=True, message="Primary product deleted successfully", tag=1)
