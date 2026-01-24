"""
FILE: src/dashboard/router.py
Dashboard & Reporting endpoints
"""
import datetime
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Optional, Literal
from src.core.database import get_session
from src.core.dependencies import get_current_user, pagination_params
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.dashboard.services import DashboardService
from src.dashboard.schemas import DashboardReportFilters
import logging
import csv
import io
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/DashboardReporting", tags=["Dashboard & Reporting"])


@router.get("/GetReport", response_model=ResponseModel)
async def get_dashboard_report(
    enterprise_type: Optional[Literal["CROP", "LIVESTOCK", "AGRO_ALLIED"]] = Query(None),
    region_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    season_id: Optional[int] = Query(None),
    officer_userid: Optional[int] = Query(None),
    association_id: Optional[int] = Query(None),
    item_type_id: Optional[int] = Query(None),
    business_type_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    pagination: dict = Depends(pagination_params),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get dashboard report from view with flexible filtering
    
    **Query Parameters:**
    - enterprise_type: Filter by CROP, LIVESTOCK, or AGRO_ALLIED
    - region_id: Filter by region
    - lga_id: Filter by LGA
    - season_id: Filter by season
    - officer_userid: Filter by extension officer
    - association_id: Filter by farmers association
    - item_type_id: Filter by crop/livestock type
    - business_type_id: Filter by business type (agro-allied)
    - start_date: Filter by planting start date
    - end_date: Filter by planting end date
    - skip: Pagination offset (default: 0)
    - limit: Results limit (default: 100, max: 1000)
    
    **Returns:** Comprehensive report data from vw_dashboard_reporting_base
    """
    filters = DashboardReportFilters(
        enterprise_type=enterprise_type,
        region_id=region_id,
        lga_id=lga_id,
        season_id=season_id,
        officer_userid=officer_userid,
        association_id=association_id,
        item_type_id=item_type_id,
        business_type_id=business_type_id,
        start_date=start_date,
        end_date=end_date
    )
    
    records = await DashboardService.get_report(
        filters,
        session,
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
    
    return ResponseModel(
        success=True,
        data=records,
        total=len(records),
        message="Dashboard report retrieved successfully",
        tag=1
    )


@router.get("/Summary", response_model=ResponseModel)
async def get_dashboard_summary(
    enterprise_type: Optional[Literal["CROP", "LIVESTOCK", "AGRO_ALLIED"]] = Query(None),
    region_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    season_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get dashboard summary statistics
    
    **Returns:**
    - Total farmers, farms, registries
    - Enterprise type breakdown
    - Area planted/harvested, yield statistics
    - Gender distribution
    - Top crops, livestock, business types
    """
    filters = DashboardReportFilters(
        enterprise_type=enterprise_type,
        region_id=region_id,
        lga_id=lga_id,
        season_id=season_id
    )
    
    summary = await DashboardService.get_summary(filters, session)
    
    return ResponseModel(
        success=True,
        data=summary.dict(),
        message="Dashboard summary retrieved successfully",
        tag=1
    )


@router.get("/RegionalBreakdown", response_model=ResponseModel)
async def get_regional_breakdown(
    season_id: Optional[int] = Query(None),
    enterprise_type: Optional[Literal["CROP", "LIVESTOCK", "AGRO_ALLIED"]] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get breakdown by region
    
    **Returns:** Statistics grouped by region
    """
    filters = DashboardReportFilters(
        season_id=season_id,
        enterprise_type=enterprise_type
    )
    
    breakdown = await DashboardService.get_regional_breakdown(filters, session)
    
    return ResponseModel(
        success=True,
        data=[b.dict() for b in breakdown],
        total=len(breakdown),
        message="Regional breakdown retrieved successfully",
        tag=1
    )


@router.get("/LGABreakdown", response_model=ResponseModel)
async def get_lga_breakdown(
    region_id: Optional[int] = Query(None),
    season_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get breakdown by LGA
    
    **Returns:** Statistics grouped by LGA
    """
    filters = DashboardReportFilters(
        region_id=region_id,
        season_id=season_id
    )
    
    breakdown = await DashboardService.get_lga_breakdown(filters, session)
    
    return ResponseModel(
        success=True,
        data=[b.dict() for b in breakdown],
        total=len(breakdown),
        message="LGA breakdown retrieved successfully",
        tag=1
    )


@router.get("/SeasonBreakdown", response_model=ResponseModel)
async def get_season_breakdown(
    region_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get breakdown by season
    
    **Returns:** Statistics grouped by season
    """
    filters = DashboardReportFilters(
        region_id=region_id,
        lga_id=lga_id
    )
    
    breakdown = await DashboardService.get_season_breakdown(filters, session)
    
    return ResponseModel(
        success=True,
        data=[b.dict() for b in breakdown],
        total=len(breakdown),
        message="Season breakdown retrieved successfully",
        tag=1
    )


@router.get("/OfficerPerformance", response_model=ResponseModel)
async def get_officer_performance(
    region_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    season_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get extension officer performance metrics
    
    **Returns:**
    - Officers ranked by number of registrations
    - Farmers and farms registered
    - LGA assignments
    """
    filters = DashboardReportFilters(
        region_id=region_id,
        lga_id=lga_id,
        season_id=season_id
    )
    
    performance = await DashboardService.get_officer_performance(filters, session)
    
    return ResponseModel(
        success=True,
        data=[p.dict() for p in performance],
        total=len(performance),
        message="Officer performance retrieved successfully",
        tag=1
    )


@router.get("/Export")
async def export_dashboard_report(
    format: Literal["csv", "json"] = Query("csv", description="Export format"),
    enterprise_type: Optional[Literal["CROP", "LIVESTOCK", "AGRO_ALLIED"]] = Query(None),
    region_id: Optional[int] = Query(None),
    lga_id: Optional[int] = Query(None),
    season_id: Optional[int] = Query(None),
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Export dashboard report
    
    **Query Parameters:**
    - format: Export format (csv or json)
    - All other filters same as GetReport
    
    **Returns:** File download
    """
    filters = DashboardReportFilters(
        enterprise_type=enterprise_type,
        region_id=region_id,
        lga_id=lga_id,
        season_id=season_id
    )
    
    # Get all records (no pagination for export)
    records = await DashboardService.get_report(
        filters,
        session,
        skip=0,
        limit=10000  # Max export limit
    )
    
    if format == "csv":
        # Create CSV
        output = io.StringIO()
        
        if records:
            fieldnames = records[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        
        # Return as downloadable file
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=dashboard_report_{date.today()}.csv"
            }
        )
    
    else:  # json
        import json
        
        # Convert datetime/date objects to strings
        def json_serial(obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        json_data = json.dumps(records, default=json_serial, indent=2)
        
        return StreamingResponse(
            iter([json_data]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=dashboard_report_{date.today()}.json"
            }
        )


@router.get("/QuickStats", response_model=ResponseModel)
async def get_quick_stats(
    session: Session = Depends(get_session),
    current_user: Useraccount = Depends(get_current_user)
):
    """
    Get quick statistics for dashboard cards
    
    **Returns:** Key metrics for dashboard overview
    """
    filters = DashboardReportFilters()
    summary = await DashboardService.get_summary(filters, session)
    
    # Quick stats format
    quick_stats = {
        "total_farmers": summary.total_farmers,
        "total_farms": summary.total_farms,
        "total_registries": summary.total_registries,
        "total_farm_size_hectares": summary.total_farm_size,
        "enterprise_breakdown": {
            "crops": summary.crop_registries,
            "livestock": summary.livestock_registries,
            "agro_allied": summary.agroallied_registries
        },
        "gender_distribution": {
            "male": summary.male_farmers,
            "female": summary.female_farmers,
            "male_percentage": round((summary.male_farmers / summary.total_farmers * 100) if summary.total_farmers > 0 else 0, 1),
            "female_percentage": round((summary.female_farmers / summary.total_farmers * 100) if summary.total_farmers > 0 else 0, 1)
        },
        "crop_statistics": {
            "total_area_planted": summary.total_area_planted,
            "total_area_harvested": summary.total_area_harvested,
            "total_yield": summary.total_yield,
            "avg_yield_per_hectare": summary.avg_yield_per_hectare
        }
    }
    
    return ResponseModel(
        success=True,
        data=quick_stats,
        message="Quick statistics retrieved successfully",
        tag=1
    )