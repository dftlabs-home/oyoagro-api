"""
FILE: src/dashboard/services.py
Business logic for Dashboard & Reporting operations
"""
from sqlmodel import Session, select, text, func
from src.dashboard.schemas import (
    DashboardReportFilters, DashboardSummary, 
    RegionalBreakdown, LGABreakdown, SeasonBreakdown,
    OfficerPerformance
)
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """Service class for Dashboard & Reporting business logic"""
    
    @staticmethod
    async def get_report(
        filters: DashboardReportFilters,
        session: Session,
        skip: int = 0,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get dashboard report from view with filters
        
        Args:
            filters: Report filters
            session: Database session
            skip: Pagination offset
            limit: Maximum records
            
        Returns:
            List[Dict]: Report records
        """
        # Build dynamic WHERE clause
        where_clauses = []
        params = {}
        
        if filters.enterprise_type:
            where_clauses.append("enterprise_type = :enterprise_type")
            params["enterprise_type"] = filters.enterprise_type
        
        if filters.region_id:
            where_clauses.append("regionid = :region_id")
            params["region_id"] = filters.region_id
        
        if filters.lga_id:
            where_clauses.append("lgaid = :lga_id")
            params["lga_id"] = filters.lga_id
        
        if filters.season_id:
            where_clauses.append("seasonid = :season_id")
            params["season_id"] = filters.season_id
        
        if filters.officer_userid:
            where_clauses.append("officer_userid = :officer_userid")
            params["officer_userid"] = filters.officer_userid
        
        if filters.association_id:
            where_clauses.append("associationid = :association_id")
            params["association_id"] = filters.association_id
        
        if filters.item_type_id:
            where_clauses.append("item_type_id = :item_type_id")
            params["item_type_id"] = filters.item_type_id
        
        if filters.business_type_id:
            where_clauses.append("business_type_id = :business_type_id")
            params["business_type_id"] = filters.business_type_id
        
        if filters.start_date:
            where_clauses.append("plantingdate >= :start_date")
            params["start_date"] = filters.start_date
        
        if filters.end_date:
            where_clauses.append("plantingdate <= :end_date")
            params["end_date"] = filters.end_date
        
        # Build SQL query
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = text(f"""
            SELECT *
            FROM vw_dashboard_reporting_base
            WHERE {where_sql}
            ORDER BY "Createdat" DESC
            LIMIT :limit OFFSET :skip
        """)
        
        params["limit"] = limit
        params["skip"] = skip
        
        # Execute query
        result = session.execute(query, params)
        
        # Convert to list of dicts
        columns = result.keys()
        records = []
        for row in result:
            record = dict(zip(columns, row))
            records.append(record)
        
        logger.info(f"Retrieved {len(records)} dashboard records")
        return records
    
    @staticmethod
    async def get_summary(
        filters: DashboardReportFilters,
        session: Session
    ) -> DashboardSummary:
        """
        Get dashboard summary statistics
        
        Args:
            filters: Report filters
            session: Database session
            
        Returns:
            DashboardSummary: Aggregated statistics
        """
        # Build WHERE clause for filtering
        where_clauses = []
        params = {}
        
        if filters.enterprise_type:
            where_clauses.append("enterprise_type = :enterprise_type")
            params["enterprise_type"] = filters.enterprise_type
        
        if filters.region_id:
            where_clauses.append("regionid = :region_id")
            params["region_id"] = filters.region_id
        
        if filters.lga_id:
            where_clauses.append("lgaid = :lga_id")
            params["lga_id"] = filters.lga_id
        
        if filters.season_id:
            where_clauses.append("seasonid = :season_id")
            params["season_id"] = filters.season_id
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Main summary query
        summary_query = text(f"""
            SELECT
                COUNT(DISTINCT farmerid) as total_farmers,
                COUNT(DISTINCT farmid) as total_farms,
                COUNT(*) as total_registries,
                COALESCE(SUM(farmsize), 0) as total_farm_size,
                
                -- Enterprise breakdown
                SUM(CASE WHEN enterprise_type = 'CROP' THEN 1 ELSE 0 END) as crop_registries,
                SUM(CASE WHEN enterprise_type = 'LIVESTOCK' THEN 1 ELSE 0 END) as livestock_registries,
                SUM(CASE WHEN enterprise_type = 'AGRO_ALLIED' THEN 1 ELSE 0 END) as agroallied_registries,
                
                -- Crop specific
                COALESCE(SUM(CASE WHEN enterprise_type = 'CROP' THEN areaplanted ELSE 0 END), 0) as total_area_planted,
                COALESCE(SUM(CASE WHEN enterprise_type = 'CROP' THEN areaharvested ELSE 0 END), 0) as total_area_harvested,
                COALESCE(SUM(CASE WHEN enterprise_type = 'CROP' THEN output_quantity ELSE 0 END), 0) as total_yield,
                
                -- Livestock specific
                COALESCE(SUM(CASE WHEN enterprise_type = 'LIVESTOCK' THEN input_quantity ELSE 0 END), 0) as total_livestock_quantity,
                
                -- Agro-allied specific
                COALESCE(SUM(CASE WHEN enterprise_type = 'AGRO_ALLIED' THEN input_quantity ELSE 0 END), 0) as total_production_capacity,
                
                -- Gender breakdown
                COUNT(DISTINCT CASE WHEN gender = 'Male' THEN farmerid END) as male_farmers,
                COUNT(DISTINCT CASE WHEN gender = 'Female' THEN farmerid END) as female_farmers
                
            FROM vw_dashboard_reporting_base
            WHERE {where_sql}
        """)
        
        result = session.exec(summary_query, params).first() # type: ignore
        
        # Calculate average yield per hectare
        avg_yield = 0.0
        if result.total_area_harvested and result.total_area_harvested > 0:
            avg_yield = float(result.total_yield) / float(result.total_area_harvested)
        
        # Get top crops
        top_crops_query = text(f"""
            SELECT item_type_name, COUNT(*) as count
            FROM vw_dashboard_reporting_base
            WHERE enterprise_type = 'CROP' AND {where_sql}
            GROUP BY item_type_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_crops = [
            {"name": row.item_type_name, "count": row.count}
            for row in session.exec(top_crops_query, params) # type: ignore
        ]
        
        # Get top livestock
        top_livestock_query = text(f"""
            SELECT item_type_name, COUNT(*) as count
            FROM vw_dashboard_reporting_base
            WHERE enterprise_type = 'LIVESTOCK' AND {where_sql}
            GROUP BY item_type_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_livestock = [
            {"name": row.item_type_name, "count": row.count}
            for row in session.exec(top_livestock_query, params) # type: ignore
        ]
        
        # Get top business types
        top_business_query = text(f"""
            SELECT business_type_name, COUNT(*) as count
            FROM vw_dashboard_reporting_base
            WHERE enterprise_type = 'AGRO_ALLIED' AND {where_sql}
            GROUP BY business_type_name
            ORDER BY count DESC
            LIMIT 10
        """)
        top_business = [
            {"name": row.business_type_name, "count": row.count}
            for row in session.exec(top_business_query, params) # type: ignore
        ]
        
        return DashboardSummary(
            total_farmers=result.total_farmers,
            total_farms=result.total_farms,
            total_registries=result.total_registries,
            total_farm_size=float(result.total_farm_size),
            crop_registries=result.crop_registries,
            livestock_registries=result.livestock_registries,
            agroallied_registries=result.agroallied_registries,
            total_area_planted=float(result.total_area_planted),
            total_area_harvested=float(result.total_area_harvested),
            total_yield=float(result.total_yield),
            avg_yield_per_hectare=round(avg_yield, 2),
            total_livestock_quantity=int(result.total_livestock_quantity),
            total_production_capacity=float(result.total_production_capacity),
            male_farmers=result.male_farmers,
            female_farmers=result.female_farmers,
            top_crops=top_crops,
            top_livestock=top_livestock,
            top_business_types=top_business
        )
    
    @staticmethod
    async def get_regional_breakdown(
        filters: DashboardReportFilters,
        session: Session
    ) -> List[RegionalBreakdown]:
        """Get breakdown by region"""
        where_clauses = []
        params = {}
        
        if filters.season_id:
            where_clauses.append("seasonid = :season_id")
            params["season_id"] = filters.season_id
        
        if filters.enterprise_type:
            where_clauses.append("enterprise_type = :enterprise_type")
            params["enterprise_type"] = filters.enterprise_type
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = text(f"""
            SELECT
                regionid,
                regionname,
                COUNT(DISTINCT farmerid) as total_farmers,
                COUNT(DISTINCT farmid) as total_farms,
                COUNT(*) as total_registries,
                SUM(CASE WHEN enterprise_type = 'CROP' THEN 1 ELSE 0 END) as crop_registries,
                SUM(CASE WHEN enterprise_type = 'LIVESTOCK' THEN 1 ELSE 0 END) as livestock_registries,
                SUM(CASE WHEN enterprise_type = 'AGRO_ALLIED' THEN 1 ELSE 0 END) as agroallied_registries
            FROM vw_dashboard_reporting_base
            WHERE {where_sql}
            GROUP BY regionid, regionname
            ORDER BY total_registries DESC
        """)
        
        results = session.execute(query, params)
        
        return [
            RegionalBreakdown(
                regionid=row.regionid,
                regionname=row.regionname,
                total_farmers=row.total_farmers,
                total_farms=row.total_farms,
                total_registries=row.total_registries,
                crop_registries=row.crop_registries,
                livestock_registries=row.livestock_registries,
                agroallied_registries=row.agroallied_registries
            )
            for row in results
        ]
    
    @staticmethod
    async def get_lga_breakdown(
        filters: DashboardReportFilters,
        session: Session
    ) -> List[LGABreakdown]:
        """Get breakdown by LGA"""
        where_clauses = []
        params = {}
        
        if filters.region_id:
            where_clauses.append("regionid = :region_id")
            params["region_id"] = filters.region_id
        
        if filters.season_id:
            where_clauses.append("seasonid = :season_id")
            params["season_id"] = filters.season_id
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = text(f"""
            SELECT
                lgaid,
                lganame,
                regionid,
                regionname,
                COUNT(DISTINCT farmerid) as total_farmers,
                COUNT(DISTINCT farmid) as total_farms,
                COUNT(*) as total_registries,
                SUM(CASE WHEN enterprise_type = 'CROP' THEN 1 ELSE 0 END) as crop_registries,
                SUM(CASE WHEN enterprise_type = 'LIVESTOCK' THEN 1 ELSE 0 END) as livestock_registries,
                SUM(CASE WHEN enterprise_type = 'AGRO_ALLIED' THEN 1 ELSE 0 END) as agroallied_registries
            FROM vw_dashboard_reporting_base
            WHERE {where_sql}
            GROUP BY lgaid, lganame, regionid, regionname
            ORDER BY total_registries DESC
        """)
        
        results = session.execute(query, params)
        
        return [
            LGABreakdown(
                lgaid=row.lgaid,
                lganame=row.lganame,
                regionid=row.regionid,
                regionname=row.regionname,
                total_farmers=row.total_farmers,
                total_farms=row.total_farms,
                total_registries=row.total_registries,
                crop_registries=row.crop_registries,
                livestock_registries=row.livestock_registries,
                agroallied_registries=row.agroallied_registries
            )
            for row in results
        ]
    
    @staticmethod
    async def get_season_breakdown(
        filters: DashboardReportFilters,
        session: Session
    ) -> List[SeasonBreakdown]:
        """Get breakdown by season"""
        where_clauses = []
        params = {}
        
        if filters.region_id:
            where_clauses.append("regionid = :region_id")
            params["region_id"] = filters.region_id
        
        if filters.lga_id:
            where_clauses.append("lgaid = :lga_id")
            params["lga_id"] = filters.lga_id
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = text(f"""
            SELECT
                seasonid,
                season_name,
                season_year,
                COUNT(*) as total_registries,
                SUM(CASE WHEN enterprise_type = 'CROP' THEN 1 ELSE 0 END) as crop_registries,
                SUM(CASE WHEN enterprise_type = 'LIVESTOCK' THEN 1 ELSE 0 END) as livestock_registries,
                SUM(CASE WHEN enterprise_type = 'AGRO_ALLIED' THEN 1 ELSE 0 END) as agroallied_registries,
                COALESCE(SUM(CASE WHEN enterprise_type = 'CROP' THEN areaplanted ELSE 0 END), 0) as total_area_planted,
                COALESCE(SUM(CASE WHEN enterprise_type = 'CROP' THEN output_quantity ELSE 0 END), 0) as total_yield
            FROM vw_dashboard_reporting_base
            WHERE {where_sql}
            GROUP BY seasonid, season_name, season_year
            ORDER BY season_year DESC, seasonid DESC
        """)
        
        results = session.execute(query, params)
        
        return [
            SeasonBreakdown(
                seasonid=row.seasonid,
                season_name=row.season_name,
                season_year=row.season_year,
                total_registries=row.total_registries,
                crop_registries=row.crop_registries,
                livestock_registries=row.livestock_registries,
                agroallied_registries=row.agroallied_registries,
                total_area_planted=float(row.total_area_planted),
                total_yield=float(row.total_yield)
            )
            for row in results
        ]
    
    @staticmethod
    async def get_officer_performance(
        filters: DashboardReportFilters,
        session: Session
    ) -> List[OfficerPerformance]:
        """Get extension officer performance metrics"""
        where_clauses = []
        params = {}
        
        if filters.region_id:
            where_clauses.append("regionid = :region_id")
            params["region_id"] = filters.region_id
        
        if filters.lga_id:
            where_clauses.append("lgaid = :lga_id")
            params["lga_id"] = filters.lga_id
        
        if filters.season_id:
            where_clauses.append("seasonid = :season_id")
            params["season_id"] = filters.season_id
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = text(f"""
            SELECT
                officer_userid,
                officer_name,
                lgaid,
                lganame,
                COUNT(DISTINCT farmerid) as total_farmers_registered,
                COUNT(DISTINCT farmid) as total_farms_registered,
                COUNT(*) as total_registries
            FROM vw_dashboard_reporting_base
            WHERE {where_sql} AND officer_userid IS NOT NULL
            GROUP BY officer_userid, officer_name, lgaid, lganame
            ORDER BY total_registries DESC
        """)
        
        results = session.execute(query, params)
        
        return [
            OfficerPerformance(
                officer_userid=row.officer_userid,
                officer_name=row.officer_name,
                total_farmers_registered=row.total_farmers_registered,
                total_farms_registered=row.total_farms_registered,
                total_registries=row.total_registries,
                lgaid=row.lgaid,
                lganame=row.lganame
            )
            for row in results
        ]