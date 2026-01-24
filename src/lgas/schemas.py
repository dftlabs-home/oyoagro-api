"""
FILE: src/lgas/schemas.py
Pydantic schemas for LGA endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LgaCreate(BaseModel):
    """Schema for creating LGA"""
    lganame: str = Field(..., min_length=2, max_length=200)
    regionid: int = Field(..., gt=0)


class LgaUpdate(BaseModel):
    """Schema for updating LGA"""
    lganame: Optional[str] = Field(None, min_length=2, max_length=200)
    regionid: Optional[int] = Field(None, gt=0)


class LgaResponse(BaseModel):
    """Schema for LGA response"""
    lgaid: int
    lganame: str
    regionid: int
    regionname: Optional[str] = None
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    version: Optional[int]
    
    class Config:
        from_attributes = True


class LgaWithStatsResponse(BaseModel):
    """Schema for LGA with statistics"""
    lgaid: int
    lganame: str
    regionid: int
    regionname: Optional[str]
    farmer_count: int = 0
    farm_count: int = 0
    officer_count: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True