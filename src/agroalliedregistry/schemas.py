"""
FILE: src/agroalliedregistry/schemas.py
Pydantic schemas for AgroAlliedRegistry endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AgroAlliedRegistryCreate(BaseModel):
    """Schema for creating agro-allied registry"""
    farmid: int = Field(..., gt=0)
    seasonid: int = Field(..., gt=0)
    businesstypeid: int = Field(..., gt=0)
    primaryproducttypeid: int = Field(..., gt=0)
    productioncapacity: Optional[Decimal] = Field(None, gt=0, description="Production capacity")


class AgroAlliedRegistryUpdate(BaseModel):
    """Schema for updating agro-allied registry"""
    productioncapacity: Optional[Decimal] = Field(None, gt=0)


class AgroAlliedRegistryResponse(BaseModel):
    """Schema for agro-allied registry response"""
    agroalliedregistryid: int
    farmid: int
    farm_name: Optional[str] = None
    seasonid: int
    season_name: Optional[str] = None
    businesstypeid: int
    business_type_name: Optional[str] = None
    primaryproducttypeid: int
    primary_product_name: Optional[str] = None
    productioncapacity: Optional[Decimal]
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True
