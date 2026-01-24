from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LivestockCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)


class LivestockUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)


class LivestockResponse(BaseModel):
    livestocktypeid: int
    name: str
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    
    class Config:
        from_attributes = True


class LivestockWithStatsResponse(BaseModel):
    livestocktypeid: int
    name: str
    registry_count: int = 0
    total_quantity: int = 0
    createdat: Optional[datetime]
    
    class Config:
        from_attributes = True