"""
FILE: src/cropregistry/schemas.py
Pydantic schemas for CropRegistry endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class CropRegistryCreate(BaseModel):
    """Schema for creating crop registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    croptypeid: int = Field(..., gt=0)
    cropvariety: Optional[str] = Field(None, max_length=200)
    areaplanted: Optional[Decimal] = Field(None, gt=0, le=100000, description="Area in hectares")
    plantedquantity: Optional[Decimal] = Field(None, gt=0, description="Quantity of seeds/seedlings")
    plantingdate: Optional[date] = None
    harvestdate: Optional[date] = None
    areaharvested: Optional[Decimal] = Field(None, gt=0, le=100000)
    yieldquantity: Optional[Decimal] = Field(None, gt=0, description="Yield in kg/tons")
    
    @validator('harvestdate')
    def validate_harvest_date(cls, v, values):
        """Validate harvest date is after planting date"""
        if v and 'plantingdate' in values and values['plantingdate']:
            if v <= values['plantingdate']:
                raise ValueError('Harvest date must be after planting date')
        return v
    
    @validator('areaharvested')
    def validate_area_harvested(cls, v, values):
        """Validate area harvested doesn't exceed area planted"""
        if v and 'areaplanted' in values and values['areaplanted']:
            if v > values['areaplanted']:
                raise ValueError('Area harvested cannot exceed area planted')
        return v


class CropRegistryUpdate(BaseModel):
    """Schema for updating crop registry"""
    cropvariety: Optional[str] = Field(None, max_length=200)
    areaplanted: Optional[Decimal] = Field(None, gt=0, le=100000)
    plantedquantity: Optional[Decimal] = Field(None, gt=0)
    plantingdate: Optional[date] = None
    harvestdate: Optional[date] = None
    areaharvested: Optional[Decimal] = Field(None, gt=0, le=100000)
    yieldquantity: Optional[Decimal] = Field(None, gt=0)
    
    @validator('harvestdate')
    def validate_harvest_date(cls, v, values):
        if v and 'plantingdate' in values and values['plantingdate']:
            if v <= values['plantingdate']:
                raise ValueError('Harvest date must be after planting date')
        return v
    
    @validator('areaharvested')
    def validate_area_harvested(cls, v, values):
        if v and 'areaplanted' in values and values['areaplanted']:
            if v > values['areaplanted']:
                raise ValueError('Area harvested cannot exceed area planted')
        return v


class CropRegistryResponse(BaseModel):
    """Schema for crop registry response"""
    cropregistryid: int
    farmid: int
    farm_name: Optional[str] = None
    seasonid: int
    season_name: Optional[str] = None
    croptypeid: int
    crop_name: Optional[str] = None
    cropvariety: Optional[str]
    areaplanted: Optional[Decimal]
    plantedquantity: Optional[Decimal]
    plantingdate: Optional[date]
    harvestdate: Optional[date]
    areaharvested: Optional[Decimal]
    yieldquantity: Optional[Decimal]
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class CropRegistryListResponse(BaseModel):
    """Schema for crop registry list item"""
    cropregistryid: int
    farmid: int
    farmer_name: Optional[str] = None
    crop_name: str
    cropvariety: Optional[str]
    season_name: str
    areaplanted: Optional[Decimal]
    yieldquantity: Optional[Decimal]
    plantingdate: Optional[date]
    harvestdate: Optional[date]
    status: str  # "Planted", "Harvested", "Pending"
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True