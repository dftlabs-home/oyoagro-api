"""
FILE: src/seasons/schemas.py
Pydantic schemas for Season endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date


class SeasonCreate(BaseModel):
    """Schema for creating season"""
    name: str = Field(..., min_length=2, max_length=200)
    year: int = Field(..., ge=2020, le=2100)
    startdate: date
    enddate: date
    
    @validator('enddate')
    def validate_dates(cls, v, values):
        """Validate that end date is after start date"""
        if 'startdate' in values and v <= values['startdate']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('year')
    def validate_year_matches_dates(cls, v, values):
        """Validate that year matches the dates"""
        if 'startdate' in values:
            if values['startdate'].year != v and values['startdate'].year != v - 1:
                raise ValueError('Year must match the start date year or be within season range')
        return v


class SeasonUpdate(BaseModel):
    """Schema for updating season"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    year: Optional[int] = Field(None, ge=2020, le=2100)
    startdate: Optional[date] = None
    enddate: Optional[date] = None
    
    @validator('enddate')
    def validate_dates(cls, v, values):
        """Validate that end date is after start date"""
        if v and 'startdate' in values and values['startdate']:
            if v <= values['startdate']:
                raise ValueError('End date must be after start date')
        return v


class SeasonResponse(BaseModel):
    """Schema for season response"""
    seasonid: int
    name: str
    year: int
    startdate: date
    enddate: date
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class SeasonWithStatsResponse(BaseModel):
    """Schema for season with statistics"""
    seasonid: int
    name: str
    year: int
    startdate: date
    enddate: date
    is_active: bool
    crop_registry_count: int = 0
    livestock_registry_count: int = 0
    agroallied_registry_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True


class ActiveSeasonResponse(BaseModel):
    """Schema for active season check"""
    seasonid: Optional[int]
    name: Optional[str]
    year: Optional[int]
    startdate: Optional[date]
    enddate: Optional[date]
    is_active: bool
    days_remaining: Optional[int] = None
    
    class Config:
        from_attributes = True