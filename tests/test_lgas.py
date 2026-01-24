"""
FILE: tests/test_lgas.py
Test cases for LGA endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.lgas
@pytest.mark.integration
class TestLgaCRUD:
    """Test LGA CRUD operations"""
    
    def test_create_lga(self, client: TestClient, auth_headers: dict, test_region):
        """Test creating LGA"""
        response = client.post(
            "/api/v1/lgas/create",
            headers=auth_headers,
            json={
                "lganame": "Ibadan South",
                "regionid": test_region.regionid
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["lganame"] == "Ibadan South"
    
    def test_create_lga_invalid_region(self, client: TestClient, auth_headers: dict):
        """Test creating LGA with invalid region fails"""
        response = client.post(
            "/api/v1/lgas/create",
            headers=auth_headers,
            json={
                "lganame": "Test LGA",
                "regionid": 9999
            }
        )
        
        assert response.status_code == 404
    
    def test_get_lgas(self, client: TestClient, auth_headers: dict, test_lga):
        """Test getting all LGAs"""
        response = client.get(
            "/api/v1/lgas/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_lgas_by_region(self, client: TestClient, auth_headers: dict, test_region, test_lga):
        """Test getting LGAs by region"""
        response = client.get(
            f"/api/v1/lgas/by-region/{test_region.regionid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_lga_with_stats(self, client: TestClient, auth_headers: dict, test_lga):
        """Test getting LGA with statistics"""
        response = client.get(
            f"/api/v1/lgas/{test_lga.lgaid}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "farmer_count" in data["data"]
    
    def test_update_lga(self, client: TestClient, auth_headers: dict, test_lga):
        """Test updating LGA"""
        response = client.put(
            f"/api/v1/lgas/{test_lga.lgaid}",
            headers=auth_headers,
            json={"lganame": "Updated LGA Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["lganame"] == "Updated LGA Name"