"""
FILE: tests/test_seasons.py
Test cases for Season endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


@pytest.mark.seasons
@pytest.mark.integration
class TestSeasonCRUD:
    """Test Season CRUD operations"""
    
    def test_create_season(self, client: TestClient, auth_headers: dict):
        """Test creating season"""
        response = client.post(
            "/api/v1/seasons/create",
            headers=auth_headers,
            json={
                "name": "2026 Dry Season",
                "year": 2026,
                "startdate": "2026-01-01",
                "enddate": "2026-06-30"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "2026 Dry Season"
    
    def test_create_season_invalid_dates(self, client: TestClient, auth_headers: dict):
        """Test creating season with end date before start date fails"""
        response = client.post(
            "/api/v1/seasons/create",
            headers=auth_headers,
            json={
                "name": "Invalid Season",
                "year": 2026,
                "startdate": "2026-06-30",
                "enddate": "2026-01-01"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_seasons(self, client: TestClient, auth_headers: dict, test_season):
        """Test getting all seasons"""
        response = client.get(
            "/api/v1/seasons/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_active_season(self, client: TestClient, auth_headers: dict):
        """Test getting active season"""
        response = client.get(
            "/api/v1/seasons/active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_seasons_by_year(self, client: TestClient, auth_headers: dict, test_season):
        """Test getting seasons by year"""
        response = client.get(
            f"/api/v1/seasons/year/{test_season.year}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_season_with_stats(self, client: TestClient, auth_headers: dict, test_season):
        """Test getting season with statistics"""
        response = client.get(
            f"/api/v1/seasons/{test_season.seasonid}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "crop_registry_count" in data["data"]
    
    def test_update_season(self, client: TestClient, auth_headers: dict, test_season):
        """Test updating season"""
        response = client.put(
            f"/api/v1/seasons/{test_season.seasonid}",
            headers=auth_headers,
            json={"name": "Updated Season Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Season Name"