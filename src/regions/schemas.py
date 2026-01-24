"""
FILE: src/regions/schemas.py
Pydantic schemas for Region endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RegionCreate(BaseModel):
    """Schema for creating region"""
    regionname: str = Field(..., min_length=2, max_length=200)


class RegionUpdate(BaseModel):
    """Schema for updating region"""
    regionname: Optional[str] = Field(None, min_length=2, max_length=200)


class RegionResponse(BaseModel):
    """Schema for region response"""
    regionid: int
    regionname: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class RegionWithLgasResponse(BaseModel):
    """Schema for region with LGAs"""
    regionid: int
    regionname: str
    lga_count: int
    lgas: Optional[list] = []
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True