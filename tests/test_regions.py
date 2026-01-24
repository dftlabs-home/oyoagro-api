"""
FILE: tests/test_regions.py
Test cases for Region endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.regions
@pytest.mark.integration
class TestRegionCRUD:
    """Test Region CRUD operations"""
    
    def test_create_region(self, client: TestClient, auth_headers: dict):
        """Test creating region"""
        response = client.post(
            "/api/v1/regions/create",
            headers=auth_headers,
            json={"regionname": "Ogbomoso Zone"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["regionname"] == "Ogbomoso Zone"
    
    def test_create_duplicate_region(self, client: TestClient, auth_headers: dict, test_region):
        """Test creating duplicate region fails"""
        response = client.post(
            "/api/v1/regions/create",
            headers=auth_headers,
            json={"regionname": test_region.regionname}
        )
        
        assert response.status_code == 400
    
    def test_get_regions(self, client: TestClient, auth_headers: dict, test_region):
        """Test getting all regions"""
        response = client.get(
            "/api/v1/regions/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_region_with_lgas(self, client: TestClient, auth_headers: dict, test_region, test_lga):
        """Test getting region with LGAs"""
        response = client.get(
            f"/api/v1/regions/{test_region.regionid}/lgas",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["lga_count"] > 0
    
    def test_update_region(self, client: TestClient, auth_headers: dict, test_region):
        """Test updating region"""
        response = client.put(
            f"/api/v1/regions/{test_region.regionid}",
            headers=auth_headers,
            json={"regionname": "Updated Zone"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["regionname"] == "Updated Zone"
    
    def test_delete_region_with_lgas_fails(self, client: TestClient, auth_headers: dict, test_region, test_lga):
        """Test deleting region with LGAs fails"""
        response = client.delete(
            f"/api/v1/regions/{test_region.regionid}",
            headers=auth_headers
        )
        
        assert response.status_code == 400