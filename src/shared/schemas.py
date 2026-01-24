"""
FILE: src/shared/schemas.py
Pydantic schemas for requests/responses
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Any, List
from datetime import date, datetime
from decimal import Decimal


class ResponseModel(BaseModel):
    """Standard response wrapper"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    tag: int = 1
    total: Optional[int] = None


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    newPassword: str = Field(..., min_length=6)
    confirmPassword: str = Field(..., min_length=1)
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values):
        if 'newPassword' in values and v != values['newPassword']:
            raise ValueError('Passwords do not match')
        return v


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    """Schema for creating new user (officer registration)"""
    firstname: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    middlename: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    emailAddress: EmailStr
    phonenumber: str = Field(..., pattern="^[0-9]{11}$")
    lgaid: int = Field(..., gt=0)
    regionid: int = Field(..., gt=0)
    streetaddress: str = Field(..., min_length=5, max_length=500)
    town: str = Field(..., min_length=2, max_length=100)
    postalcode: str = Field(..., min_length=3, max_length=20)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)


class UserResponse(BaseModel):
    """Schema for user details response"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    tag: int = 1


class UserListResponse(BaseModel):
    """Schema for user list response"""
    success: bool
    message: Optional[str] = None
    data: Optional[List[dict]] = None
    tag: int = 1
    total: Optional[int] = None


# ============================================================================
# FARMER SCHEMAS
# ============================================================================

class FarmerCreate(BaseModel):
    """Schema for creating new farmer"""
    firstname: str = Field(..., min_length=2, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    middlename: Optional[str] = Field(None, max_length=100)
    gender: str = Field(..., pattern="^(Male|Female)$")
    dateofbirth: date
    email: EmailStr
    phonenumber: str = Field(..., pattern="^[0-9]{11}$")
    associationid: int = Field(..., gt=0)
    householdsize: Optional[int] = Field(None, ge=1)
    availablelabor: Optional[int] = Field(None, ge=0)
    photourl: Optional[str] = None
    streetaddress: str = Field(..., min_length=5, max_length=500)
    town: str = Field(..., min_length=2, max_length=100)
    postalcode: str = Field(..., min_length=3, max_length=20)
    lgaid: int = Field(..., gt=0)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    
    @validator('dateofbirth')
    def validate_age(cls, v):
        """Ensure farmer is at least 16 years old"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 16:
            raise ValueError('Farmer must be at least 16 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v


class FarmerUpdate(BaseModel):
    """Schema for updating farmer"""
    farmerid: int = Field(..., gt=0)
    firstname: Optional[str] = Field(None, min_length=2, max_length=100)
    lastname: Optional[str] = Field(None, min_length=2, max_length=100)
    middlename: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(Male|Female)$")
    dateofbirth: Optional[date] = None
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = Field(None, pattern="^[0-9]{11}$")
    associationid: Optional[int] = Field(None, gt=0)
    householdsize: Optional[int] = Field(None, ge=1)
    availablelabor: Optional[int] = Field(None, ge=0)
    photourl: Optional[str] = None


# ============================================================================
# FARM SCHEMAS
# ============================================================================

class FarmCreate(BaseModel):
    """Schema for creating new farm"""
    farmerid: int = Field(..., gt=0)
    farmtypeid: int = Field(..., gt=0)
    farmsize: Decimal = Field(..., gt=0, decimal_places=2)
    streetaddress: str = Field(..., min_length=5, max_length=500)
    town: str = Field(..., min_length=2, max_length=100)
    postalcode: str = Field(..., min_length=3, max_length=20)
    lgaid: int = Field(..., gt=0)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)


class FarmUpdate(BaseModel):
    """Schema for updating farm"""
    farmid: int = Field(..., gt=0)
    farmerid: Optional[int] = Field(None, gt=0)
    farmtypeid: Optional[int] = Field(None, gt=0)
    farmsize: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


# ============================================================================
# CROP REGISTRY SCHEMAS
# ============================================================================

class CropRegistryCreate(BaseModel):
    """Schema for creating crop registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    croptypeid: int = Field(..., gt=0)
    cropvariety: Optional[str] = Field(None, max_length=200)
    areaplanted: Decimal = Field(..., gt=0, decimal_places=2)
    plantedquantity: Decimal = Field(..., gt=0, decimal_places=2)
    plantingdate: date
    harvestdate: Optional[date] = None
    areaharvested: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    yieldquantity: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    
    @validator('harvestdate')
    def validate_harvest_date(cls, v, values):
        """Ensure harvest date is after planting date"""
        if v and 'plantingdate' in values and values['plantingdate']:
            if v < values['plantingdate']:
                raise ValueError('Harvest date must be after planting date')
        return v


class CropRegistryUpdate(BaseModel):
    """Schema for updating crop registry"""
    cropregistryid: int = Field(..., gt=0)
    cropvariety: Optional[str] = Field(None, max_length=200)
    areaplanted: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    plantedquantity: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    plantingdate: Optional[date] = None
    harvestdate: Optional[date] = None
    areaharvested: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    yieldquantity: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


# ============================================================================
# LIVESTOCK REGISTRY SCHEMAS
# ============================================================================

class LivestockRegistryCreate(BaseModel):
    """Schema for creating livestock registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    livestocktypeid: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    startdate: date
    enddate: Optional[date] = None
    
    @validator('enddate')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date"""
        if v and 'startdate' in values and values['startdate']:
            if v < values['startdate']:
                raise ValueError('End date must be after start date')
        return v


# ============================================================================
# AGRO-ALLIED REGISTRY SCHEMAS
# ============================================================================

class AgroAlliedRegistryCreate(BaseModel):
    """Schema for creating agro-allied registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    businesstypeid: int = Field(..., gt=0)
    primaryproducttypeid: int = Field(..., gt=0)
    productioncapacity: Decimal = Field(..., gt=0, decimal_places=2)


# ============================================================================
# REFERENCE DATA SCHEMAS
# ============================================================================

class AssociationCreate(BaseModel):
    """Schema for creating association"""
    name: str = Field(..., min_length=2, max_length=200)
    registrationno: str = Field(..., min_length=2, max_length=100)


class SeasonCreate(BaseModel):
    """Schema for creating season"""
    name: str = Field(..., min_length=2, max_length=100)
    year: int = Field(..., ge=2000, le=2100)
    startdate: date
    enddate: date
    
    @validator('enddate')
    def validate_season_dates(cls, v, values):
        """Ensure end date is after start date"""
        if 'startdate' in values and values['startdate']:
            if v <= values['startdate']:
                raise ValueError('End date must be after start date')
        return v


class RegionCreate(BaseModel):
    """Schema for creating region"""
    regionname: str = Field(..., min_length=2, max_length=200)


class LgaCreate(BaseModel):
    """Schema for creating LGA"""
    lganame: str = Field(..., min_length=2, max_length=200)
    regionid: int = Field(..., gt=0)


class CropCreate(BaseModel):
    """Schema for creating crop type"""
    name: str = Field(..., min_length=2, max_length=200)


class LivestockCreate(BaseModel):
    """Schema for creating livestock type"""
    name: str = Field(..., min_length=2, max_length=200)


class FarmTypeCreate(BaseModel):
    """Schema for creating farm type"""
    typename: str = Field(..., min_length=2, max_length=200)


class BusinessTypeCreate(BaseModel):
    """Schema for creating business type"""
    name: str = Field(..., min_length=2, max_length=200)


class PrimaryProductCreate(BaseModel):
    """Schema for creating primary product"""
    name: str = Field(..., min_length=2, max_length=200)


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationCreate(BaseModel):
    """Schema for creating notification"""
    title: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10)
    targetRegions: Optional[List[int]] = None
    targetLgas: Optional[List[int]] = None
    targetUsers: Optional[List[int]] = None