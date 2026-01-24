"""
FILE: src/farmers/schemas.py
Pydantic schemas for Farmer endpoints
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime, date
import re


class AddressCreate(BaseModel):
    """Schema for creating address"""
    streetaddress: Optional[str] = Field(None, max_length=500)
    town: Optional[str] = Field(None, max_length=200)
    postalcode: Optional[str] = Field(None, max_length=20)
    lgaid: int = Field(..., gt=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class FarmerCreate(BaseModel):
    """Schema for creating farmer"""
    firstname: str = Field(..., min_length=2, max_length=100)
    middlename: Optional[str] = Field(None, max_length=100)
    lastname: str = Field(..., min_length=2, max_length=100)
    gender: str = Field(..., pattern="^(Male|Female|male|female|Unknown|unknown)$") # type: ignore
    dateofbirth: date
    email: Optional[EmailStr] = None
    phonenumber: str = Field(..., min_length=11, max_length=11)
    associationid: Optional[int] = Field(None, gt=0)
    householdsize: int = Field(..., ge=1, le=100)
    availablelabor: int = Field(..., ge=0, le=100)
    photourl: Optional[str] = Field(None, max_length=500)
    
    # Address information
    address: AddressCreate
    
    @validator('phonenumber')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if not re.match(r'^0\d{10}$', v):
            raise ValueError('Phone number must be 11 digits starting with 0')
        return v
    
    @validator('dateofbirth')
    def validate_age(cls, v):
        """Validate farmer age (must be at least 18)"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Farmer must be at least 18 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v
    
    @validator('availablelabor')
    def validate_labor(cls, v, values):
        """Validate available labor <= household size"""
        if 'householdsize' in values and v > values['householdsize']:
            raise ValueError('Available labor cannot exceed household size')
        return v


class FarmerUpdate(BaseModel):
    """Schema for updating farmer"""
    firstname: Optional[str] = Field(None, min_length=2, max_length=100)
    middlename: Optional[str] = Field(None, max_length=100)
    lastname: Optional[str] = Field(None, min_length=2, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|male|female|Unknown|unknown)$") # type: ignore
    dateofbirth: Optional[date] = None
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = Field(None, min_length=11, max_length=11)
    associationid: Optional[int] = Field(None, gt=0)
    householdsize: Optional[int] = Field(None, ge=1, le=100)
    availablelabor: Optional[int] = Field(None, ge=0, le=100)
    photourl: Optional[str] = Field(None, max_length=500)
    
    # Address update (optional)
    address: Optional[AddressCreate] = None
    
    @validator('phonenumber')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not re.match(r'^0\d{10}$', v):
            raise ValueError('Phone number must be 11 digits starting with 0')
        return v


class AddressResponse(BaseModel):
    """Schema for address response"""
    addressid: int
    streetaddress: Optional[str]
    town: Optional[str]
    postalcode: Optional[str]
    lgaid: int
    lganame: Optional[str] = None
    latitude: Optional[float]
    longitude: Optional[float]
    
    class Config:
        from_attributes = True


class FarmerResponse(BaseModel):
    """Schema for farmer response"""
    farmerid: int
    firstname: str
    middlename: Optional[str]
    lastname: str
    gender: str
    dateofbirth: date
    email: Optional[str]
    phonenumber: str
    associationid: Optional[int]
    association_name: Optional[str] = None
    householdsize: int
    availablelabor: int
    photourl: Optional[str]
    userid: Optional[int]
    address: Optional[AddressResponse] = None
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class FarmerWithStatsResponse(BaseModel):
    """Schema for farmer with statistics"""
    farmerid: int
    firstname: str
    middlename: Optional[str]
    lastname: str
    fullname: str
    gender: str
    dateofbirth: date
    age: int
    email: Optional[str]
    phonenumber: str
    associationid: Optional[int]
    association_name: Optional[str]
    householdsize: int
    availablelabor: int
    photourl: Optional[str]
    address: Optional[AddressResponse]
    farm_count: int = 0
    crop_registry_count: int = 0
    livestock_registry_count: int = 0
    agroallied_registry_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True


class FarmerListResponse(BaseModel):
    """Schema for farmer list item"""
    farmerid: int
    firstname: str
    middlename: Optional[str]
    lastname: str
    fullname: str
    gender: str
    age: int
    phonenumber: str
    association_name: Optional[str]
    lga: Optional[str]
    farm_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True