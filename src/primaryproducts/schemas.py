"""
FILE: src/primaryproducts/schemas.py
Pydantic schemas for PrimaryProduct endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PrimaryProductCreate(BaseModel):
    """Schema for creating primary product"""
    name: str = Field(..., min_length=2, max_length=200)


class PrimaryProductUpdate(BaseModel):
    """Schema for updating primary product"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)


class PrimaryProductResponse(BaseModel):
    """Schema for primary product response"""
    primaryproducttypeid: int
    name: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True


class PrimaryProductWithStatsResponse(BaseModel):
    """Schema for primary product with statistics"""
    primaryproducttypeid: int
    name: str
    registry_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True
