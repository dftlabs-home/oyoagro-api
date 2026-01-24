"""
FILE: src/businesstypes/schemas.py
Pydantic schemas for BusinessType endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BusinessTypeCreate(BaseModel):
    """Schema for creating business type"""
    name: str = Field(..., min_length=2, max_length=200)


class BusinessTypeUpdate(BaseModel):
    """Schema for updating business type"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)


class BusinessTypeResponse(BaseModel):
    """Schema for business type response"""
    businesstypeid: int
    name: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True


class BusinessTypeWithStatsResponse(BaseModel):
    """Schema for business type with statistics"""
    businesstypeid: int
    name: str
    registry_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True