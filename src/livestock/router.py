from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.livestock.services import LivestockService
from src.livestock.schemas import LivestockCreate, LivestockUpdate

router = APIRouter(prefix="/livestock", tags=["Livestock"])


@router.post("/create", response_model=ResponseModel)
async def create_livestock(
    data: LivestockCreate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestock = await LivestockService.create(data, session)
    return ResponseModel(
        success=True,
        message="Livestock created successfully",
        data={
            "livestocktypeid": livestock.livestocktypeid,
            "name": livestock.name,
            "createdat": livestock.createdat
        },
        tag=1
    )


@router.get("/", response_model=ResponseModel)
async def get_livestock(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestocks = await LivestockService.get_all(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{
            "livestocktypeid": l.livestocktypeid,
            "name": l.name,
            "createdat": l.createdat
        } for l in livestocks],
        total=len(livestocks),
        tag=1
    )


@router.get("/with-counts", response_model=ResponseModel)
async def get_livestock_with_counts(
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestocks = await LivestockService.get_all_with_counts(
        session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(success=True, data=livestocks, total=len(livestocks), tag=1)


@router.get("/search", response_model=ResponseModel)
async def search_livestock(
    q: str = Query(..., min_length=2),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestocks = await LivestockService.search(
        q, session, skip=pagination["skip"], limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=[{"livestocktypeid": l.livestocktypeid, "name": l.name} for l in livestocks],
        total=len(livestocks),
        tag=1
    )


@router.get("/{livestock_id}", response_model=ResponseModel)
async def get_livestock_by_id(
    livestock_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestock = await LivestockService.get_by_id(livestock_id, session)
    return ResponseModel(
        success=True,
        data={"livestocktypeid": livestock.livestocktypeid, "name": livestock.name},
        tag=1
    )


@router.get("/{livestock_id}/stats", response_model=ResponseModel)
async def get_livestock_stats(
    livestock_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    data = await LivestockService.get_with_stats(livestock_id, session)
    return ResponseModel(success=True, data=data, tag=1)


@router.put("/{livestock_id}", response_model=ResponseModel)
async def update_livestock(
    livestock_id: int,
    data: LivestockUpdate,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    livestock = await LivestockService.update(livestock_id, data, session)
    return ResponseModel(
        success=True,
        message="Livestock updated successfully",
        data={"livestocktypeid": livestock.livestocktypeid, "name": livestock.name},
        tag=1
    )


@router.delete("/{livestock_id}", response_model=ResponseModel)
async def delete_livestock(
    livestock_id: int,
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    await LivestockService.delete(livestock_id, session)
    return ResponseModel(success=True, message="Livestock deleted successfully", tag=1)