"""
FILE: src/farmers/services.py
Business logic for Farmer operations
"""
from sqlmodel import Session, select
from src.shared.models import (
    Farmer, Address, Association, Lga, Farm, AgroAlliedRegistry, Useraccount, CropRegistry, LivestockRegistry, 
)
from src.farmers.schemas import FarmerCreate, FarmerUpdate
from datetime import datetime, date
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FarmerService:
    """Service class for Farmer business logic"""
    
    @staticmethod
    async def create(
        data: FarmerCreate, 
        session: Session,
        current_user: Optional[Useraccount] = None
    ) -> Farmer:
        """
        Create new farmer with address
        
        Args:
            data: Farmer creation data
            session: Database session
            current_user: Current authenticated user
            
        Returns:
            Farmer: Created farmer
            
        Raises:
            HTTPException: If validation fails or duplicates exist
        """
        # Validate association if provided
        if data.associationid:
            association = session.get(Association, data.associationid)
            if not association or association.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Association with ID {data.associationid} not found"
                )
        
        # Validate LGA for address
        lga = session.get(Lga, data.address.lgaid)
        if not lga or lga.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LGA with ID {data.address.lgaid} not found"
            )
        
        # Check for duplicate phone number
        existing_phone = session.exec(
            select(Farmer).where(
                Farmer.phonenumber == data.phonenumber,
                Farmer.deletedat == None
            )
        ).first()
        
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Farmer with phone number {data.phonenumber} already exists"
            )
        
        # Check for duplicate email if provided
        if data.email:
            existing_email = session.exec(
                select(Farmer).where(
                    Farmer.email == data.email,
                    Farmer.deletedat == None
                )
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Farmer with email {data.email} already exists"
                )
        
        # Create farmer
        farmer = Farmer(
            firstname=data.firstname,
            middlename=data.middlename,
            lastname=data.lastname,
            gender=data.gender.capitalize(),
            dateofbirth=data.dateofbirth,
            email=data.email,
            phonenumber=data.phonenumber,
            associationid=data.associationid,
            householdsize=data.householdsize,
            availablelabor=data.availablelabor,
            photourl=data.photourl,
            userid=current_user.userid if current_user else None,
            createdat=datetime.utcnow(),
            version=1
        )
        
        session.add(farmer)
        session.commit()
        session.refresh(farmer)
        
        # Create address
        address = Address(
            farmerid=farmer.farmerid,
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
        
        logger.info(f"Created farmer: {farmer.farmerid} - {farmer.firstname} {farmer.lastname}")
        return farmer
    
    @staticmethod
    async def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        association_id: Optional[int] = None,
        lga_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Farmer]:
        """
        Get all active farmers with pagination and filters
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            association_id: Filter by association
            lga_id: Filter by LGA
            user_id: Filter by user (extension officer)
            
        Returns:
            List[Farmer]: List of farmers
        """
        statement = select(Farmer).where(Farmer.deletedat == None)
        
        if association_id:
            statement = statement.where(Farmer.associationid == association_id)
        
        if user_id:
            statement = statement.where(Farmer.userid == user_id)
        
        if lga_id:
            # Filter by LGA through address
            statement = statement.join(Address).where(
                Address.lgaid == lga_id,
                Address.farmerid != None,
                Address.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(
            Farmer.firstname, Farmer.lastname # type: ignore
        )
        
        farmers = session.exec(statement).all()
        return list(farmers)
    
    @staticmethod
    async def get_by_id(farmer_id: int, session: Session) -> Farmer:
        """
        Get farmer by ID
        
        Args:
            farmer_id: Farmer ID
            session: Database session
            
        Returns:
            Farmer: Found farmer
            
        Raises:
            HTTPException: If farmer not found
        """
        farmer = session.get(Farmer, farmer_id)
        
        if not farmer or farmer.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farmer with ID {farmer_id} not found"
            )
        
        return farmer
    
    @staticmethod
    def _get_farmer_address(farmer_id: int, session: Session) -> Optional[Address]:
        """Get farmer's address"""
        statement = select(Address).where(
            Address.farmerid == farmer_id,
            Address.deletedat == None
        )
        return session.exec(statement).first()
    
    @staticmethod
    def _calculate_age(birthdate: date) -> int:
        """Calculate age from birthdate"""
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    @staticmethod
    async def get_with_details(farmer_id: int, session: Session) -> dict:
        """
        Get farmer with full details including address and statistics
        
        Args:
            farmer_id: Farmer ID
            session: Database session
            
        Returns:
            dict: Farmer with complete details
        """
        farmer = await FarmerService.get_by_id(farmer_id, session)
        
        # Get address
        address = FarmerService._get_farmer_address(farmer_id, session)
        
        # Get association name
        association_name = None
        if farmer.associationid:
            association = session.get(Association, farmer.associationid)
            if association:
                association_name = association.name
        
        # Get LGA name from address
        lga_name = None
        if address:
            lga = session.get(Lga, address.lgaid)
            if lga:
                lga_name = lga.lganame
        
        # Count farms
        farm_count = len(session.exec(
            select(Farm).where(
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        ).all())
        
        # Count crop registries
        crop_count = 0
        livestock_count = 0
        agroallied_count = 0
        
        # Get all farms for this farmer
        farms = session.exec(
            select(Farm).where(
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        ).all()
        
        for farm in farms:
            crop_count += len(session.exec(
                select(CropRegistry).where(
                    CropRegistry.farmid == farm.farmid,
                    CropRegistry.deletedat == None
                )
            ).all())
            
            livestock_count += len(session.exec(
                select(LivestockRegistry).where(
                    LivestockRegistry.farmid == farm.farmid,
                    LivestockRegistry.deletedat == None
                )
            ).all())
            
            agroallied_count += len(session.exec(
                select(AgroAlliedRegistry).where(
                    AgroAlliedRegistry.farmid == farm.farmid,
                    AgroAlliedRegistry.deletedat == None
                )
            ).all())
        
        age = FarmerService._calculate_age(farmer.dateofbirth) # type: ignore
        fullname = f"{farmer.firstname} {farmer.middlename or ''} {farmer.lastname}".strip()
        
        result = {
            "farmerid": farmer.farmerid,
            "firstname": farmer.firstname,
            "middlename": farmer.middlename,
            "lastname": farmer.lastname,
            "fullname": fullname,
            "gender": farmer.gender,
            "dateofbirth": farmer.dateofbirth,
            "age": age,
            "email": farmer.email,
            "phonenumber": farmer.phonenumber,
            "associationid": farmer.associationid,
            "association_name": association_name,
            "householdsize": farmer.householdsize,
            "availablelabor": farmer.availablelabor,
            "photourl": farmer.photourl,
            "userid": farmer.userid,
            "farm_count": farm_count,
            "crop_registry_count": crop_count,
            "livestock_registry_count": livestock_count,
            "agroallied_registry_count": agroallied_count,
            "createdat": farmer.createdat,
            "updatedat": farmer.updatedat,
            "version": farmer.version
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
    async def update(
        farmer_id: int,
        data: FarmerUpdate,
        session: Session
    ) -> Farmer:
        """
        Update farmer
        
        Args:
            farmer_id: Farmer ID
            data: Update data
            session: Database session
            
        Returns:
            Farmer: Updated farmer
        """
        farmer = await FarmerService.get_by_id(farmer_id, session)
        
        # Check for duplicate phone if being updated
        if data.phonenumber and data.phonenumber != farmer.phonenumber:
            existing_phone = session.exec(
                select(Farmer).where(
                    Farmer.phonenumber == data.phonenumber,
                    Farmer.deletedat == None,
                    Farmer.farmerid != farmer_id
                )
            ).first()
            
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Phone number {data.phonenumber} already exists"
                )
        
        # Check for duplicate email if being updated
        if data.email and data.email != farmer.email:
            existing_email = session.exec(
                select(Farmer).where(
                    Farmer.email == data.email,
                    Farmer.deletedat == None,
                    Farmer.farmerid != farmer_id
                )
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {data.email} already exists"
                )
        
        # Validate association if being updated
        if data.associationid:
            association = session.get(Association, data.associationid)
            if not association or association.deletedat is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Association with ID {data.associationid} not found"
                )
        
        # Update farmer fields
        if data.firstname:
            farmer.firstname = data.firstname
        if data.middlename is not None:
            farmer.middlename = data.middlename
        if data.lastname:
            farmer.lastname = data.lastname
        if data.gender:
            farmer.gender = data.gender.capitalize()
        if data.dateofbirth:
            # Validate age
            age = FarmerService._calculate_age(data.dateofbirth)
            if age < 18 or age > 120:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date of birth"
                )
            farmer.dateofbirth = data.dateofbirth
        if data.email is not None:
            farmer.email = data.email
        if data.phonenumber:
            farmer.phonenumber = data.phonenumber
        if data.associationid is not None:
            farmer.associationid = data.associationid
        if data.householdsize:
            farmer.householdsize = data.householdsize
        if data.availablelabor is not None:
            # Validate labor <= household size
            household = data.householdsize if data.householdsize else farmer.householdsize
            if data.availablelabor > household: # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Available labor cannot exceed household size"
                )
            farmer.availablelabor = data.availablelabor
        if data.photourl is not None:
            farmer.photourl = data.photourl
        
        farmer.updatedat = datetime.utcnow()
        farmer.version = (farmer.version or 0) + 1
        
        session.add(farmer)
        
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
            address = FarmerService._get_farmer_address(farmer_id, session)
            
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
                    farmerid=farmer_id,
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
        session.refresh(farmer)
        
        logger.info(f"Updated farmer: {farmer_id}")
        return farmer
    
    @staticmethod
    async def delete(farmer_id: int, session: Session) -> None:
        """
        Soft delete farmer
        
        Args:
            farmer_id: Farmer ID
            session: Database session
            
        Raises:
            HTTPException: If farmer not found or has farms
        """
        farmer = await FarmerService.get_by_id(farmer_id, session)
        
        # Check if farmer has farms
        farms = session.exec(
            select(Farm).where(
                Farm.farmerid == farmer_id,
                Farm.deletedat == None
            )
        ).first()
        
        if farms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete farmer with registered farms"
            )
        
        farmer.deletedat = datetime.utcnow()
        session.add(farmer)
        
        # Soft delete address
        address = FarmerService._get_farmer_address(farmer_id, session)
        if address:
            address.deletedat = datetime.utcnow()
            session.add(address)
        
        session.commit()
        
        logger.info(f"Deleted farmer: {farmer_id}")
    
    @staticmethod
    async def search(
        query: str,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        association_id: Optional[int] = None,
        lga_id: Optional[int] = None
    ) -> List[Farmer]:
        """
        Search farmers by name, phone, or email
        
        Args:
            query: Search query
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            association_id: Filter by association
            lga_id: Filter by LGA
            
        Returns:
            List[Farmer]: Matching farmers
        """
        statement = select(Farmer).where(
            Farmer.deletedat == None,
            (Farmer.firstname.ilike(f"%{query}%")) | # type: ignore
            (Farmer.lastname.ilike(f"%{query}%")) | # type: ignore 
            (Farmer.phonenumber.ilike(f"%{query}%")) | # type: ignore
            (Farmer.email.ilike(f"%{query}%")) # type: ignore
        )
        
        if association_id:
            statement = statement.where(Farmer.associationid == association_id)
        
        if lga_id:
            statement = statement.join(Address).where(
                Address.lgaid == lga_id,
                Address.farmerid != None,
                Address.deletedat == None
            )
        
        statement = statement.offset(skip).limit(limit).order_by(
            Farmer.firstname, Farmer.lastname # type: ignore
        )
        
        farmers = session.exec(statement).all()
        return list(farmers)
    
    @staticmethod
    async def get_by_association(
        association_id: int,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Farmer]:
        """
        Get all farmers in an association
        
        Args:
            association_id: Association ID
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Farmer]: Farmers in association
        """
        # Verify association exists
        association = session.get(Association, association_id)
        if not association or association.deletedat is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Association with ID {association_id} not found"
            )
        
        statement = select(Farmer).where(
            Farmer.associationid == association_id,
            Farmer.deletedat == None
        ).offset(skip).limit(limit).order_by(Farmer.firstname, Farmer.lastname) # type: ignore
        
        farmers = session.exec(statement).all()
        return list(farmers)
    
    @staticmethod
    async def get_by_officer(
        user_id: int,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Farmer]:
        """
        Get all farmers registered by a specific officer
        
        Args:
            user_id: User ID (extension officer)
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Farmer]: Farmers registered by officer
        """
        statement = select(Farmer).where(
            Farmer.userid == user_id,
            Farmer.deletedat == None
        ).offset(skip).limit(limit).order_by(Farmer.createdat.desc()) # type: ignore
        
        farmers = session.exec(statement).all()
        return list(farmers)
    
    @staticmethod
    async def get_statistics(session: Session) -> dict:
        """
        Get overall farmer statistics
        
        Args:
            session: Database session
            
        Returns:
            dict: Statistics summary
        """
        total_farmers = len(session.exec(
            select(Farmer).where(Farmer.deletedat == None)
        ).all())
        
        male_farmers = len(session.exec(
            select(Farmer).where(
                Farmer.deletedat == None,
                Farmer.gender == "Male"
            )
        ).all())
        
        female_farmers = len(session.exec(
            select(Farmer).where(
                Farmer.deletedat == None,
                Farmer.gender == "Female"
            )
        ).all())
        
        # Count farmers with farms
        farmers_with_farms = len(session.exec(
            select(Farmer).join(Farm).where(
                Farmer.deletedat == None,
                Farm.deletedat == None
            ).distinct()
        ).all())
        
        return {
            "total_farmers": total_farmers,
            "male_farmers": male_farmers,
            "female_farmers": female_farmers,
            "farmers_with_farms": farmers_with_farms,
            "farmers_without_farms": total_farmers - farmers_with_farms
        }