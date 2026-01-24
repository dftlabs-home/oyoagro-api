"""
FILE: src/dashboard/schemas.py
Pydantic schemas for Dashboard & Reporting endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date
from decimal import Decimal


class DashboardReportFilters(BaseModel):
    """Filters for dashboard report"""
    enterprise_type: Optional[Literal["CROP", "LIVESTOCK", "AGRO_ALLIED"]] = None
    region_id: Optional[int] = None
    lga_id: Optional[int] = None
    season_id: Optional[int] = None
    officer_userid: Optional[int] = None
    association_id: Optional[int] = None
    item_type_id: Optional[int] = None
    business_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class DashboardReportItem(BaseModel):
    """Single report record from view"""
    enterprise_type: str
    farmid: int
    farmerid: int
    farmer_full_name: str
    gender: Optional[str]
    dateofbirth: Optional[date]
    farmer_email: Optional[str]
    farmer_phone: Optional[str]
    householdsize: Optional[int]
    availablelabor: Optional[int]
    associationid: Optional[int]
    association_name: Optional[str]
    town: Optional[str]
    officer_userid: Optional[int]
    officer_name: Optional[str]
    lgaid: Optional[int]
    lganame: Optional[str]
    regionid: Optional[int]
    regionname: Optional[str]
    seasonid: Optional[int]
    season_name: Optional[str]
    season_year: Optional[int]
    season_start_date: Optional[date]
    season_end_date: Optional[date]
    item_type_id: Optional[int]
    item_type_name: Optional[str]
    business_type_id: Optional[int]
    business_type_name: Optional[str]
    primary_product_id: Optional[int]
    primary_product_name: Optional[str]
    farmsize: Optional[Decimal]
    areaplanted: Optional[Decimal]
    areaharvested: Optional[Decimal]
    input_quantity: Optional[Decimal]
    output_quantity: Optional[Decimal]
    harvest_percentage: Optional[Decimal]
    yield_per_area: Optional[Decimal]
    plantingdate: Optional[date]
    harvestdate: Optional[date]
    farmer_created_at: Optional[datetime]
    farmer_updated_at: Optional[datetime]
    createdat: Optional[datetime]
    updatedat: Optional[datetime]
    deletedat: Optional[datetime]
    record_count: int
    
    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    total_farmers: int
    total_farms: int
    total_registries: int
    total_farm_size: float
    
    # Enterprise type breakdown
    crop_registries: int
    livestock_registries: int
    agroallied_registries: int
    
    # Crop specific
    total_area_planted: float
    total_area_harvested: float
    total_yield: float
    avg_yield_per_hectare: float
    
    # Livestock specific
    total_livestock_quantity: int
    
    # Agro-allied specific
    total_production_capacity: float
    
    # Gender breakdown
    male_farmers: int
    female_farmers: int
    
    # Top items
    top_crops: List[dict] = []
    top_livestock: List[dict] = []
    top_business_types: List[dict] = []


class RegionalBreakdown(BaseModel):
    """Regional breakdown statistics"""
    regionid: int
    regionname: str
    total_farmers: int
    total_farms: int
    total_registries: int
    crop_registries: int
    livestock_registries: int
    agroallied_registries: int


class LGABreakdown(BaseModel):
    """LGA breakdown statistics"""
    lgaid: int
    lganame: str
    regionid: int
    regionname: str
    total_farmers: int
    total_farms: int
    total_registries: int
    crop_registries: int
    livestock_registries: int
    agroallied_registries: int


class SeasonBreakdown(BaseModel):
    """Season breakdown statistics"""
    seasonid: int
    season_name: str
    season_year: int
    total_registries: int
    crop_registries: int
    livestock_registries: int
    agroallied_registries: int
    total_area_planted: float
    total_yield: float


class OfficerPerformance(BaseModel):
    """Extension officer performance"""
    officer_userid: int
    officer_name: str
    total_farmers_registered: int
    total_farms_registered: int
    total_registries: int
    lgaid: Optional[int]
    lganame: Optional[str]


class ExportFormat(BaseModel):
    """Export format options"""
    format: Literal["csv", "excel", "json"] = "csv"
    include_deleted: bool = False


class DashboardMetrics(BaseModel):
    """Key dashboard metrics"""
    metric_name: str
    metric_value: int
    metric_date: datetime
    entity_id: Optional[int]
    entity_type: Optional[str]