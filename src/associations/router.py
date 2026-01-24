"""
FILE: src/associations/router.py
Association CRUD endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.associations.services import AssociationService
from src.associations.schemas import AssociationCreate, AssociationUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/associations", tags=["Associations"])


@router.post("/create", response_model=ResponseModel)
async def create_association(
    data: AssociationCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Create new association
    
    Requires authentication
    """
    association = await AssociationService.create(data, session)
    
    return ResponseModel(
        success=True,
        message="Association created successfully",
        data={
            "associationid": association.associationid,
            "name": association.name,
            "registrationno": association.registrationno,
            "createdat": association.createdat,
            "updatedat": association.updatedat,
            "deletedat": association.deletedat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_associations(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get all associations with pagination
    
    Requires authentication
    """
    associations = await AssociationService.get_all(
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "associationid": a.associationid,
            "name": a.name,
            "registrationno": a.registrationno,
            "createdat": a.createdat,
            "updatedat": a.updatedat,
            "deletedat": a.deletedat,
            "version": a.version
        } for a in associations],
        total=len(associations),
        tag=1
    )


@router.get("/search", response_model=ResponseModel)
async def search_associations(
    q: str = Query(..., min_length=2, description="Search query"),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Search associations by name or registration number
    
    Requires authentication
    """
    associations = await AssociationService.search(
        q,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "associationid": a.associationid,
            "name": a.name,
            "registrationno": a.registrationno,
            "createdat": a.createdat
        } for a in associations],
        total=len(associations),
        tag=1
    )


@router.get("/{association_id}", response_model=ResponseModel)
async def get_association(
    association_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get association by ID
    
    Requires authentication
    """
    association = await AssociationService.get_by_id(association_id, session)
    
    return ResponseModel(
        success=True,
        data={
            "associationid": association.associationid,
            "name": association.name,
            "registrationno": association.registrationno,
            "createdat": association.createdat,
            "updatedat": association.updatedat,
            "deletedat": association.deletedat,
            "version": association.version
        },
        tag=1
    )


@router.put("/{association_id}", response_model=ResponseModel)
async def update_association(
    association_id: int,
    data: AssociationUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Update association
    
    Requires authentication
    """
    association = await AssociationService.update(association_id, data, session)
    
    return ResponseModel(
        success=True,
        message="Association updated successfully",
        data={
            "associationid": association.associationid,
            "name": association.name,
            "registrationno": association.registrationno,
            "createdat": association.createdat,
            "updatedat": association.updatedat,
            "version": association.version
        },
        tag=1
    )


@router.delete("/{association_id}", response_model=ResponseModel)
async def delete_association(
    association_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Delete association (soft delete)
    
    Requires authentication
    """
    await AssociationService.delete(association_id, session)
    
    return ResponseModel(
        success=True,
        message="Association deleted successfully",
        tag=1
    )