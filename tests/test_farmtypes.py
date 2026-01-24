"""
FILE: tests/test_farmtypes.py
Test cases for FarmType endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.farmtypes
@pytest.mark.integration
class TestFarmTypeCRUD:
    """Test FarmType CRUD operations"""
    
    def test_create_farmtype(self, client: TestClient, auth_headers: dict):
        """Test creating farm type"""
        response = client.post(
            "/api/v1/farmtypes/create",
            headers=auth_headers,
            json={
                "typename": "Crop Farming"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["typename"] == "Crop Farming"
    
    def test_create_duplicate_farmtype(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test creating duplicate farm type fails"""
        response = client.post(
            "/api/v1/farmtypes/create",
            headers=auth_headers,
            json={
                "typename": test_farmtype.typename
            }
        )
        
        assert response.status_code == 400
    
    def test_get_farmtypes(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test getting all farm types"""
        response = client.get(
            "/api/v1/farmtypes/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_farmtypes_with_counts(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test getting farm types with farm counts"""
        response = client.get(
            "/api/v1/farmtypes/with-counts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "farm_count" in data["data"][0]
    
    def test_get_farmtype_by_id(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test getting farm type by ID"""
        response = client.get(
            f"/api/v1/farmtypes/{test_farmtype.farmtypeid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["farmtypeid"] == test_farmtype.farmtypeid
    
    def test_update_farmtype(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test updating farm type"""
        response = client.put(
            f"/api/v1/farmtypes/{test_farmtype.farmtypeid}",
            headers=auth_headers,
            json={"typename": "Crop Farming New"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["typename"] == "Crop Farming New"
    
    def test_search_farmtypes(self, client: TestClient, auth_headers: dict, test_farmtype):
        """Test searching farm types"""
        response = client.get(
            "/api/v1/farmtypes/search?q=Mixed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True