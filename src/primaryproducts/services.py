"""
FILE: src/primaryproducts/services.py
Business logic for PrimaryProduct operations
"""
from sqlmodel import Session, select, func
from src.shared.models import PrimaryProduct, AgroAlliedRegistry
from src.primaryproducts.schemas import PrimaryProductCreate, PrimaryProductUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
import logging

logger = logging.getLogger(__name__)


class PrimaryProductService:
    """Service class for PrimaryProduct business logic"""
    
    @staticmethod
    async def create(data: PrimaryProductCreate, session: Session) -> PrimaryProduct:
        """Create new primary product"""
        # Check for duplicate name (case-insensitive)
        existing = session.exec(
            select(PrimaryProduct).where(
                func.lower(PrimaryProduct.name) == func.lower(data.name),
                PrimaryProduct.deletedat == None
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Primary product '{data.name}' already exists"
            )
        
        product = PrimaryProduct(name=data.name, createdat=datetime.utcnow())
        session.add(product)
        session.commit()
        session.refresh(product)
        
        logger.info(f"Created primary product: {product.primaryproducttypeid} - {product.name}")
        return product
    
    @staticmethod
    async def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[PrimaryProduct]:
        """Get all active primary products"""
        statement = select(PrimaryProduct).where(
            PrimaryProduct.deletedat == None
        ).offset(skip).limit(limit).order_by(PrimaryProduct.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_by_id(product_id: int, session: Session) -> PrimaryProduct:
        """Get primary product by ID"""
        product = session.get(PrimaryProduct, product_id)
        
        if not product or product.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Primary product with ID {product_id} not found"
            )
        
        return product
    
    @staticmethod
    async def get_with_stats(product_id: int, session: Session) -> dict:
        """Get primary product with statistics"""
        product = await PrimaryProductService.get_by_id(product_id, session)
        
        # Count registries
        registry_count = session.exec(
            select(func.count(AgroAlliedRegistry.agroalliedregistryid))
            .where(
                AgroAlliedRegistry.primaryproducttypeid == product_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first() or 0
        
        return {
            "primaryproducttypeid": product.primaryproducttypeid,
            "name": product.name,
            "registry_count": registry_count,
            "createdat": product.createdat,
            "updatedat": product.updatedat
        }
    
    @staticmethod
    async def update(product_id: int, data: PrimaryProductUpdate, session: Session) -> PrimaryProduct:
        """Update primary product"""
        product = await PrimaryProductService.get_by_id(product_id, session)
        
        if data.name and data.name != product.name:
            existing = session.exec(
                select(PrimaryProduct).where(
                    func.lower(PrimaryProduct.name) == func.lower(data.name),
                    PrimaryProduct.deletedat == None,
                    PrimaryProduct.primaryproducttypeid != product_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Primary product '{data.name}' already exists"
                )
            
            product.name = data.name
        
        product.updatedat = datetime.utcnow()
        session.add(product)
        session.commit()
        session.refresh(product)
        
        logger.info(f"Updated primary product: {product_id}")
        return product
    
    @staticmethod
    async def delete(product_id: int, session: Session) -> None:
        """Soft delete primary product"""
        product = await PrimaryProductService.get_by_id(product_id, session)
        
        # Check if has registries
        registries = session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.primaryproducttypeid == product_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first()
        
        if registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete primary product with existing registries"
            )
        
        product.deletedat = datetime.utcnow()
        session.add(product)
        session.commit()
        
        logger.info(f"Deleted primary product: {product_id}")
    
    @staticmethod
    async def search(query: str, session: Session, skip: int = 0, limit: int = 100) -> List[PrimaryProduct]:
        """Search primary products by name"""
        statement = select(PrimaryProduct).where(
            PrimaryProduct.deletedat == None,
            PrimaryProduct.name.ilike(f"%{query}%")
        ).offset(skip).limit(limit).order_by(PrimaryProduct.name)
        
        return list(session.exec(statement).all())
    
    @staticmethod
    async def get_all_with_counts(session: Session, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all primary products with registry counts"""
        products = await PrimaryProductService.get_all(session, skip, limit)
        
        result = []
        for product in products:
            count = session.exec(
                select(func.count(AgroAlliedRegistry.agroalliedregistryid))
                .where(
                    AgroAlliedRegistry.primaryproducttypeid == product.primaryproducttypeid,
                    AgroAlliedRegistry.deletedat == None
                )
            ).first() or 0
            
            result.append({
                "primaryproducttypeid": product.primaryproducttypeid,
                "name": product.name,
                "registry_count": count,
                "createdat": product.createdat
            })
        
        return result