"""
FILE: src/farms/services.py
Business logic for Farm operations
"""
from sqlmodel import Session, select
from src.shared.models import (
    Farm, Address, Farmer, Farmtype, Lga,
    CropRegistry, LivestockRegistry, AgroAlliedRegistry
)
from src.farms.schemas import FarmCreate, FarmUpdate
from datetime import datetime
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FarmService:
    """Service class for Farm business logic"""
    
    @staticmethod
    async def create(data: FarmCreate, session: Session) -> Farm:
        """
        Create new farm with address
        
        Args:
            data: Farm creation data
            session: Database session
            
        Returns:
            Farm: Created farm
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate farmer exists
        farmer = session.get(Farmer, data.farmerid)
        if not farmer or farmer.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farmer with ID {data.farmerid} not found"
            )
        
        # Validate farm type exists
        farmtype = session.get(Farmtype, data.farmtypeid)
        if not farmtype or farmtype.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm type with ID {data.farmtypeid} not found"
            )
        
        # Validate LGA for address
        lga = session.get(Lga, data.address.lgaid)
        if not lga or lga.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LGA with ID {data.address.lgaid} not found"
            )
        
        # Create farm
        farm = Farm(
            farmerid=data.farmerid,
            farmtypeid=data.farmtypeid,
            farmsize=data.farmsize, # type: ignore
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        # Create address
        address = Address(
            farmid=farm.farmid,
            streetaddress=data.address.streetaddress,
            town=data.address.town,
            postalcode=data.address.postalcode,
            lgaid=data.address.lgaid,
            latitude=data.address.latitude, # type: ignore
            longitude=data.address.longitude, # type: ignore
            createdat=datetime.utcnow()
        )
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        logger.info(f"Created farm: {farm.farmid} for farmer {data.farmerid}")
        return farm
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        farmer_id: Optional[int] = None,
        farmtype_id: Optional[int] = None,
        lga_id: Optional[int] = None
    ) -> List[Farm]:
        """
        Get all active farms with pagination and filters
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            farmer_id: Filter by farmer
            farmtype_id: Filter by farm type
            lga_id: Filter by LGA
            
        Returns:
            List[Farm]: List of farms
        """
        statement = select(Farm).where(Farm.deletedat == None)
        
        if farmer_id:
            statement = statement.where(Farm.farmerid == farmer_id)
        
        if farmtype_id:
            statement = statement.where(Farm.farmtypeid == farmtype_id)
        
        if lga_id:
            # Filter by LGA through address with explicit join condition
            statement = statement.join(
                Address, 
                Farm.farmid == Address.farmid # type: ignore
            ).where(
                Address.lgaid == lga_id,
                Address.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(Farm.createdat.desc()) # type: ignore
        
        farms = session.exec(statement).all()
        return list(farms)
    
    @staticmethod
    async def get_by_id(farm_id: int, session: Session) -> Farm:
        """
        Get farm by ID
        
        Args:
            farm_id: Farm ID
            session: Database session
            
        Returns:
            Farm: Found farm
            
        Raises:
            HTTPException: If farm not found
        """
        farm = session.get(Farm, farm_id)
        
        if not farm or farm.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {farm_id} not found"
            )
        
        return farm
    
    @staticmethod
    def _get_farm_address(farm_id: int, session: Session) -> Optional[Address]:
        """Get farm's address"""
        statement = select(Address).where(
            Address.farmid == farm_id,
            Address.deletedat == None
        )
        return session.exec(statement).first()
    
    @staticmethod
    async def get_with_details(farm_id: int, session: Session) -> dict:
        """
        Get farm with full details including statistics
        
        Args:
            farm_id: Farm ID
            session: Database session
            
        Returns:
            dict: Farm with complete details
        """
        farm = await FarmService.get_by_id(farm_id, session)
        
        # Get address
        address = FarmService._get_farm_address(farm_id, session)
        
        # Get farmer name
        farmer = session.get(Farmer, farm.farmerid)
        farmer_name = f"{farmer.firstname} {farmer.lastname}" if farmer else "Unknown"
        
        # Get farm type name
        farmtype = session.get(Farmtype, farm.farmtypeid)
        farmtype_name = farmtype.typename if farmtype else "Unknown"
        
        # Get LGA name from address
        lga_name = None
        if address:
            lga = session.get(Lga, address.lgaid)
            if lga:
                lga_name = lga.lganame
        
        # Count registries
        crop_count = len(session.exec(
            select(CropRegistry).where(
                CropRegistry.farmid == farm_id,
                CropRegistry.deletedat == None
            )
        ).all())
        
        livestock_count = len(session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.farmid == farm_id,
                LivestockRegistry.deletedat == None
            )
        ).all())
        
        agroallied_count = len(session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.farmid == farm_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).all())
        
        result = {
            "farmid": farm.farmid,
            "farmerid": farm.farmerid,
            "farmer_name": farmer_name,
            "farmtypeid": farm.farmtypeid,
            "farmtype_name": farmtype_name,
            "farmsize": farm.farmsize,
            "crop_registry_count": crop_count,
            "livestock_registry_count": livestock_count,
            "agroallied_registry_count": agroallied_count,
            "total_registries": crop_count + livestock_count + agroallied_count,
            "createdat": farm.createdat,
            "updatedat": farm.updatedat,
            "version": farm.version
        }
        
        # Add address if exists
        if address:
            result["address"] = {
                "addressid": address.addressid,
                "streetaddress": address.streetaddress,
                "town": address.town,
                "postalcode": address.postalcode,
                "lgaid": address.lgaid,
                "lganame": lga_name,
                "latitude": address.latitude,
                "longitude": address.longitude
            }
        
        return result
    
    @staticmethod
    async def update(farm_id: int, data: FarmUpdate, session: Session) -> Farm:
        """
        Update farm
        
        Args:
            farm_id: Farm ID
            data: Update data
            session: Database session
            
        Returns:
            Farm: Updated farm
        """
        farm = await FarmService.get_by_id(farm_id, session)
        
        # Validate farmer if being updated
        if data.farmerid and data.farmerid != farm.farmerid:
            farmer = session.get(Farmer, data.farmerid)
            if not farmer or farmer.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Farmer with ID {data.farmerid} not found"
                )
            farm.farmerid = data.farmerid
        
        # Validate farm type if being updated
        if data.farmtypeid and data.farmtypeid != farm.farmtypeid:
            farmtype = session.get(Farmtype, data.farmtypeid)
            if not farmtype or farmtype.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Farm type with ID {data.farmtypeid} not found"
                )
            farm.farmtypeid = data.farmtypeid
        
        # Update farm size if provided
        if data.farmsize is not None:
            farm.farmsize = data.farmsize # type: ignore
        
        farm.updatedat = datetime.utcnow()
        farm.version = (farm.version or 0) + 1
        
        session.add(farm)
        
        # Update address if provided
        if data.address:
            # Validate LGA
            lga = session.get(Lga, data.address.lgaid)
            if not lga or lga.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LGA with ID {data.address.lgaid} not found"
                )
            
            # Get existing address
            address = FarmService._get_farm_address(farm_id, session)
            
            if address:
                # Update existing address
                address.streetaddress = data.address.streetaddress
                address.town = data.address.town
                address.postalcode = data.address.postalcode
                address.lgaid = data.address.lgaid
                address.latitude = data.address.latitude # type: ignore
                address.longitude = data.address.longitude # type: ignore
                address.updatedat = datetime.utcnow()
                session.add(address)
            else:
                # Create new address
                new_address = Address(
                    farmid=farm_id,
                    streetaddress=data.address.streetaddress,
                    town=data.address.town,
                    postalcode=data.address.postalcode,
                    lgaid=data.address.lgaid,
                    latitude=data.address.latitude, # type: ignore
                    longitude=data.address.longitude, # type: ignore
                    createdat=datetime.utcnow()
                )
                session.add(new_address)
        
        session.commit()
        session.refresh(farm)
        
        logger.info(f"Updated farm: {farm_id}")
        return farm
    
    @staticmethod
    async def delete(farm_id: int, session: Session) -> None:
        """
        Soft delete farm
        
        Args:
            farm_id: Farm ID
            session: Database session
            
        Raises:
            HTTPException: If farm not found or has registries
        """
        farm = await FarmService.get_by_id(farm_id, session)
        
        # Check if farm has crop registries
        crop_registries = session.exec(
            select(CropRegistry).where(
                CropRegistry.farmid == farm_id,
                CropRegistry.deletedat == None
            )
        ).first()
        
        if crop_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete farm with crop registries"
            )
        
        # Check if farm has livestock registries
        livestock_registries = session.exec(
            select(LivestockRegistry).where(
                LivestockRegistry.farmid == farm_id,
                LivestockRegistry.deletedat == None
            )
        ).first()
        
        if livestock_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete farm with livestock registries"
            )
        
        # Check if farm has agro-allied registries
        agroallied_registries = session.exec(
            select(AgroAlliedRegistry).where(
                AgroAlliedRegistry.farmid == farm_id,
                AgroAlliedRegistry.deletedat == None
            )
        ).first()
        
        if agroallied_registries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete farm with agro-allied registries"
            )
        
        farm.deletedat = datetime.utcnow()
        session.add(farm)
        
        # Soft delete address
        address = FarmService._get_farm_address(farm_id, session)
        if address:
            address.deletedat = datetime.utcnow()
            session.add(address)
        
        session.commit()
        
        logger.info(f"Deleted farm: {farm_id}")
    
    @staticmethod
    async def get_by_farmer(
        farmer_id: int,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Farm]:
        """
        Get all farms for a specific farmer
        
        Args:
            farmer_id: Farmer ID
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Farm]: Farms owned by farmer
        """
        # Verify farmer exists
        farmer = session.get(Farmer, farmer_id)
        if not farmer or farmer.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farmer with ID {farmer_id} not found"
            )
        
        statement = select(Farm).where(
            Farm.farmerid == farmer_id,
            Farm.deletedat == None
        ).offset(skip).limit(limit).order_by(Farm.createdat.desc()) # type: ignore
        
        farms = session.exec(statement).all()
        return list(farms)
    
    @staticmethod
    async def get_statistics(session: Session) -> dict:
        """
        Get overall farm statistics
        
        Args:
            session: Database session
            
        Returns:
            dict: Statistics summary
        """
        total_farms = len(session.exec(
            select(Farm).where(Farm.deletedat == None)
        ).all())
        
        # Calculate total farm size
        farms = session.exec(
            select(Farm).where(Farm.deletedat == None)
        ).all()
        total_farmsize = sum(farm.farmsize for farm in farms) # type: ignore
        average_farmsize = total_farmsize / total_farms if total_farms > 0 else 0
        
        # Count farms by type
        from sqlmodel import func
        farms_by_type = session.exec(
            select(Farmtype.typename, func.count(Farm.farmid)) # type: ignore
            .join(Farm, Farm.farmtypeid == Farmtype.farmtypeid) # type: ignore
            .where(Farm.deletedat == None, Farmtype.deletedat == None)
            .group_by(Farmtype.typename)
        ).all()
        
        # Count farms with registries
        farms_with_registries = len(session.exec(
            select(Farm).where(
                Farm.deletedat == None
            ).join(CropRegistry, isouter=True).where(
                CropRegistry.deletedat == None
            ).distinct()
        ).all())
        
        return {
            "total_farms": total_farms,
            "total_farmsize_hectares": round(total_farmsize, 2),
            "average_farmsize_hectares": round(average_farmsize, 2),
            "farms_by_type": [{"type": t, "count": c} for t, c in farms_by_type],
            "farms_with_registries": farms_with_registries
        }