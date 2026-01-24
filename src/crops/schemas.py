"""
FILE: src/crops/schemas.py
Pydantic schemas for Crop endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CropCreate(BaseModel):
    """Schema for creating crop type"""
    name: str = Field(..., min_length=2, max_length=200)


class CropUpdate(BaseModel):
    """Schema for updating crop type"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)


class CropResponse(BaseModel):
    """Schema for crop response"""
    croptypeid: int
    name: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True


class CropWithStatsResponse(BaseModel):
    """Schema for crop with statistics"""
    croptypeid: int
    name: str
    registry_count: int = 0
    total_area_planted: float = 0.0
    total_yield: float = 0.0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True