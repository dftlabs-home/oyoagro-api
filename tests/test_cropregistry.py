"""
Test cases for CropRegistry endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


@pytest.mark.integration
class TestCropRegistryCRUD:
    def test_create_crop_registry(self, client: TestClient, auth_headers: dict, test_farm, test_season, test_crop):
        """Test creating crop registry"""
        response = client.post(
            "/api/v1/cropregistry/create",
            headers=auth_headers,
            json={
                "farmid": test_farm.farmid,
                "seasonid": test_season.seasonid,
                "croptypeid": test_crop.croptypeid,
                "cropvariety": "Oba Super 2",
                "areaplanted": 5.5,
                "plantedquantity": 25.0,
                "plantingdate": str(test_season.startdate)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["crop_name"] == test_crop.name
    
    def test_create_with_harvest_before_planting_fails(self, client: TestClient, auth_headers: dict, test_farm, test_season, test_crop):
        """Test that harvest date before planting fails"""
        response = client.post(
            "/api/v1/cropregistry/create",
            headers=auth_headers,
            json={
                "farmid": test_farm.farmid,
                "seasonid": test_season.seasonid,
                "croptypeid": test_crop.croptypeid,
                "plantingdate": "2025-05-01",
                "harvestdate": "2025-04-01"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_registries(self, client: TestClient, auth_headers: dict):
        """Test getting all crop registries"""
        response = client.get("/api/v1/cropregistry/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_get_statistics(self, client: TestClient, auth_headers: dict):
        """Test getting statistics"""
        response = client.get("/api/v1/cropregistry/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_registries" in data["data"]
        assert "total_area_planted" in data["data"]
    
    def test_filter_by_season(self, client: TestClient, auth_headers: dict, test_season):
        """Test filtering by season"""
        response = client.get(
            f"/api/v1/cropregistry/?season_id={test_season.seasonid}",
            headers=auth_headers
        )
        assert response.status_code == 200