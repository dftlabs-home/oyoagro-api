from sqlmodel import Session, select, func
from src.shared.models import Livestock, LivestockRegistry
from src.livestock.schemas import LivestockCreate, LivestockUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class LivestockService:
    
    @staticmethod
    async def create(data: LivestockCreate, session: Session) -> Livestock:
        existing = session.exec(
            select(Livestock).where(
                func.lower(Livestock.name) == func.lower(data.name),
                Livestock.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Livestock '{data.name}' already exists"
            )
        
        livestock = Livestock(name=data.name, createdat=datetime.utcnow())
        session.add(livestock)
        session.commit()
        session.refresh(livestock)
        
        logger.info(f"Created livestock: {livestock.livestocktypeid} - {livestock.name}")
        return livestock
    
    @staticmethod
    async def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Livestock]:
        statement = select(Livestock).where(
            Livestock.deletedat == None
        ).offset(skip).limit(limit).order_by(Livestock.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(livestock_id: int, session: Session) -> Livestock:
        livestock = session.get(Livestock, livestock_id)
        
        if not livestock or livestock.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Livestock with ID {livestock_id} not found"
            )
        
        return livestock
    
    @staticmethod
    async def get_with_stats(livestock_id: int, session: Session) -> dict:
        livestock = await LivestockService.get_by_id(livestock_id, session)
        
        registry_count = session.exec(
            select(func.count(LivestockRegistry.livestockregistryid)) # type: ignore
            .where(
                LivestockRegistry.livestocktypeid == livestock_id,
                LivestockRegistry.deletedat == None
            )
        ).first() or 0
        
        total_quantity = session.exec(
            select(func.sum(LivestockRegistry.quantity))
            .where(
                LivestockRegistry.livestocktypeid == livestock_id,
                LivestockRegistry.deletedat == None
            )
        ).first() or 0
        
        return {
            "livestocktypeid": livestock.livestocktypeid,
            "name": livestock.name,
            "registry_count": registry_count,
            "total_quantity": int(total_quantity) if total_quantity else 0,
            "createdat": livestock.createdat,
            "updatedat": livestock.updatedat
        }
    
    @staticmethod
    async def update(livestock_id: int, data: LivestockUpdate, session: Session) -> Livestock:
        livestock = await LivestockService.get_by_id(livestock_id, session)
        
        if data.name and data.name != livestock.name:
            existing = session.exec(
                select(Livestock).where(
                    func.lower(Livestock.name) == func.lower(data.name),
                    Livestock.deletedat == None,
                    Livestock.livestocktypeid != livestock_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Livestock '{data.name}' already exists"
                )
            
            livestock.name = data.name
        
        livestock.updatedat = datetime.utcnow()
        session.add(livestock)
        session.commit()
        session.refresh(livestock)
        
        logger.info(f"Updated livestock: {livestock_id}")
        return livestock
    
    @staticmethod
    async def delete(livestock_id: int, session: Session) -> None:
        livestock = await LivestockService.get_by_id(livestock_id, session)
        
        registries = session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.livestocktypeid == livestock_id,
                LivestockRegistry.deletedat == None
            )
        ).first()
        
        if registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete livestock type with existing registries"
            )
        
        livestock.deletedat = datetime.utcnow()
        session.add(livestock)
        session.commit()
        
        logger.info(f"Deleted livestock: {livestock_id}")
    
    @staticmethod
    async def search(query: str, session: Session, skip: int = 0, limit: int = 100) -> List[Livestock]:
        statement = select(Livestock).where(
            Livestock.deletedat == None,
            Livestock.name.ilike(f"%{query}%") # type: ignore
        ).offset(skip).limit(limit).order_by(Livestock.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_all_with_counts(session: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        livestocks = await LivestockService.get_all(session, skip, limit)
        
        result = []
        for livestock in livestocks:
            count = session.exec(
                select(func.count(LivestockRegistry.livestockregistryid)) # type: ignore
                .where(
                    LivestockRegistry.livestocktypeid == livestock.livestocktypeid,
                    LivestockRegistry.deletedat == None
                )
            ).first() or 0
            
            result.append({
                "livestocktypeid": livestock.livestocktypeid,
                "name": livestock.name,
                "registry_count": count,
                "createdat": livestock.createdat
            })
        
        return result