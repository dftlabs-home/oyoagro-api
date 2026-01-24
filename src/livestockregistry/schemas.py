"""
FILE: src/livestockregistry/schemas.py
Pydantic schemas for LivestockRegistry endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date


class LivestockRegistryCreate(BaseModel):
    """Schema for creating livestock registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    livestocktypeid: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, description="Number of animals")
    startdate: Optional[date] = None
    enddate: Optional[date] = None
    
    @validator('enddate')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        if v and 'startdate' in values and values['startdate']:
            if v <= values['startdate']:
                raise ValueError('End date must be after start date')
        return v


class LivestockRegistryUpdate(BaseModel):
    """Schema for updating livestock registry"""
    quantity: Optional[int] = Field(None, gt=0)
    startdate: Optional[date] = None
    enddate: Optional[date] = None
    
    @validator('enddate')
    def validate_end_date(cls, v, values):
        if v and 'startdate' in values and values['startdate']:
            if v <= values['startdate']:
                raise ValueError('End date must be after start date')
        return v


class LivestockRegistryResponse(BaseModel):
    """Schema for livestock registry response"""
    livestockregistryid: int
    farmid: int
    farm_name: Optional[str] = None
    seasonid: int
    season_name: Optional[str] = None
    livestocktypeid: int
    livestock_name: Optional[str] = None
    quantity: int
    startdate: Optional[date]
    enddate: Optional[date]
    status: str  # "Active", "Completed"
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True
