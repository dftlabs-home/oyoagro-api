"""
FILE: src/farms/schemas.py
Pydantic schemas for Farm endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class FarmAddressCreate(BaseModel):
    """Schema for creating farm address"""
    streetaddress: Optional[str] = Field(None, max_length=500)
    town: Optional[str] = Field(None, max_length=200)
    postalcode: Optional[str] = Field(None, max_length=20)
    lgaid: int = Field(..., gt=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class FarmCreate(BaseModel):
    """Schema for creating farm"""
    farmerid: int = Field(..., gt=0)
    farmtypeid: int = Field(..., gt=0)
    farmsize: float = Field(..., gt=0, le=100000, description="Farm size in hectares")
    
    # Address information
    address: FarmAddressCreate
    
    @validator('farmsize')
    def validate_farmsize(cls, v):
        """Validate farm size is reasonable"""
        if v <= 0:
            raise ValueError('Farm size must be greater than 0')
        if v > 100000:
            raise ValueError('Farm size exceeds maximum allowed (100,000 hectares)')
        # Round to 2 decimal places
        return round(v, 2)


class FarmUpdate(BaseModel):
    """Schema for updating farm"""
    farmerid: Optional[int] = Field(None, gt=0)
    farmtypeid: Optional[int] = Field(None, gt=0)
    farmsize: Optional[float] = Field(None, gt=0, le=100000)
    
    # Address update (optional)
    address: Optional[FarmAddressCreate] = None
    
    @validator('farmsize')
    def validate_farmsize(cls, v):
        """Validate farm size is reasonable"""
        if v is not None:
            if v <= 0:
                raise ValueError('Farm size must be greater than 0')
            if v > 100000:
                raise ValueError('Farm size exceeds maximum allowed (100,000 hectares)')
            return round(v, 2)
        return v


class FarmAddressResponse(BaseModel):
    """Schema for farm address response"""
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


class FarmResponse(BaseModel):
    """Schema for farm response"""
    farmid: int
    farmerid: int
    farmer_name: Optional[str] = None
    farmtypeid: int
    farmtype_name: Optional[str] = None
    farmsize: float
    address: Optional[FarmAddressResponse] = None
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class FarmWithStatsResponse(BaseModel):
    """Schema for farm with statistics"""
    farmid: int
    farmerid: int
    farmer_name: str
    farmtypeid: int
    farmtype_name: str
    farmsize: float
    address: Optional[FarmAddressResponse]
    crop_registry_count: int = 0
    livestock_registry_count: int = 0
    agroallied_registry_count: int = 0
    total_registries: int = 0
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    
    class Config:
        from_attributes = True


class FarmListResponse(BaseModel):
    """Schema for farm list item"""
    farmid: int
    farmerid: int
    farmer_name: str
    farmtypeid: int
    farmtype_name: str
    farmsize: float
    lga: Optional[str]
    registry_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True