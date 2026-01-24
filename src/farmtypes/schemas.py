"""
FILE: src/farmtypes/schemas.py
Pydantic schemas for FarmType endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FarmTypeCreate(BaseModel):
    """Schema for creating farm type"""
    typename: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class FarmTypeUpdate(BaseModel):
    """Schema for updating farm type"""
    typename: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class FarmTypeResponse(BaseModel):
    """Schema for farm type response"""
    farmtypeid: int
    typename: str
    description: Optional[str] = None
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class FarmTypeWithStatsResponse(BaseModel):
    """Schema for farm type with statistics"""
    farmtypeid: int
    typename: str
    description: Optional[str] = None
    farm_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True