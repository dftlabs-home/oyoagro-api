"""
Test cases for LivestockRegistry endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestLivestockRegistryCRUD:
    def test_create_livestock_registry(self, client: TestClient, auth_headers: dict, test_farm, test_season, test_livestock):
        """Test creating livestock registry"""
        response = client.post(
            "/api/v1/livestockregistry/create",
            headers=auth_headers,
            json={
                "farmid": test_farm.farmid,
                "seasonid": test_season.seasonid,
                "livestocktypeid": test_livestock.livestocktypeid,
                "quantity": 50,
                "startdate": str(test_season.startdate)
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["quantity"] == 50
    
    def test_create_with_end_before_start_fails(self, client: TestClient, auth_headers: dict, test_farm, test_season, test_livestock):
        """Test that end date before start fails"""
        response = client.post(
            "/api/v1/livestockregistry/create",
            headers=auth_headers,
            json={
                "farmid": test_farm.farmid,
                "seasonid": test_season.seasonid,
                "livestocktypeid": test_livestock.livestocktypeid,
                "quantity": 50,
                "startdate": "2025-05-01",
                "enddate": "2025-04-01"
            }
        )
        
        assert response.status_code == 422
    
    def test_get_registries(self, client: TestClient, auth_headers: dict):
        """Test getting all livestock registries"""
        response = client.get("/api/v1/livestockregistry/", headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_statistics(self, client: TestClient, auth_headers: dict):
        """Test getting statistics"""
        response = client.get("/api/v1/livestockregistry/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_quantity" in data["data"]