"""
FILE: src/associations/schemas.py
Pydantic schemas for Association endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AssociationCreate(BaseModel):
    """Schema for creating association"""
    name: str = Field(..., min_length=2, max_length=200)
    registrationno: str = Field(..., min_length=2, max_length=100)


class AssociationUpdate(BaseModel):
    """Schema for updating association"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    registrationno: Optional[str] = Field(None, min_length=2, max_length=100)


class AssociationResponse(BaseModel):
    """Schema for association response"""
    associationid: int
    name: str
    registrationno: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True