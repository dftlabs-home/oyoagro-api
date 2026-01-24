"""
Test cases for AgroAlliedRegistry endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAgroAlliedRegistryCRUD:
    def test_create_agroallied_registry(self, client: TestClient, auth_headers: dict, test_farm, test_season, test_businesstype, test_primaryproduct):
        """Test creating agro-allied registry"""
        response = client.post(
            "/api/v1/agroalliedregistry/create",
            headers=auth_headers,
            json={
                "farmid": test_farm.farmid,
                "seasonid": test_season.seasonid,
                "businesstypeid": test_businesstype.businesstypeid,
                "primaryproducttypeid": test_primaryproduct.primaryproducttypeid,
                "productioncapacity": 1000.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert float(data["data"]["productioncapacity"]) == 1000.0
    
    def test_get_registries(self, client: TestClient, auth_headers: dict):
        """Test getting all agro-allied registries"""
        response = client.get("/api/v1/agroalliedregistry/", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_statistics(self, client: TestClient, auth_headers: dict):
        """Test getting statistics"""
        response = client.get("/api/v1/agroalliedregistry/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_production_capacity" in data["data"]
        assert "by_business_type" in data["data"]
    
    def test_filter_by_business_type(self, client: TestClient, auth_headers: dict, test_businesstype):
        """Test filtering by business type"""
        response = client.get(
            f"/api/v1/agroalliedregistry/?businesstype_id={test_businesstype.businesstypeid}",
            headers=auth_headers
        )
        assert response.status_code == 200