"""
FILE: tests/test_farms.py
Test cases for Farm endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.farms
@pytest.mark.integration
class TestFarmCRUD:
    """Test Farm CRUD operations"""
    
    def test_create_farm(self, client: TestClient, auth_headers: dict, test_farmer, test_farmtype, test_lga):
        """Test creating farm"""
        response = client.post(
            "/api/v1/farms/create",
            headers=auth_headers,
            json={
                "farmerid": test_farmer.farmerid,
                "farmtypeid": test_farmtype.farmtypeid,
                "farmsize": 10.5,
                "address": {
                    "streetaddress": "Farm Location",
                    "town": "Ibadan",
                    "postalcode": "200003",
                    "lgaid": test_lga.lgaid,
                    "latitude": 7.4000,
                    "longitude": 3.9600
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert float(data["data"]["farmsize"]) == 10.5
        assert data["data"]["address"] is not None
    
    def test_create_farm_invalid_farmer(self, client: TestClient, auth_headers: dict, test_farmtype, test_lga):
        """Test creating farm with invalid farmer fails"""
        response = client.post(
            "/api/v1/farms/create",
            headers=auth_headers,
            json={
                "farmerid": 9999,
                "farmtypeid": test_farmtype.farmtypeid,
                "farmsize": 5.0,
                "address": {
                    "lgaid": test_lga.lgaid
                }
            }
        )
        
        assert response.status_code == 404
    
    def test_create_farm_invalid_farmsize(self, client: TestClient, auth_headers: dict, test_farmer, test_farmtype, test_lga):
        """Test creating farm with invalid size fails"""
        response = client.post(
            "/api/v1/farms/create",
            headers=auth_headers,
            json={
                "farmerid": test_farmer.farmerid,
                "farmtypeid": test_farmtype.farmtypeid,
                "farmsize": -5.0,  # Invalid
                "address": {
                    "lgaid": test_lga.lgaid
                }
            }
        )
        
        assert response.status_code == 422
    
    def test_get_farms(self, client: TestClient, auth_headers: dict, test_farm):
        """Test getting all farms"""
        response = client.get(
            "/api/v1/farms/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_farms_by_farmer(self, client: TestClient, auth_headers: dict, test_farmer, test_farm):
        """Test getting farms by farmer"""
        response = client.get(
            f"/api/v1/farms/by-farmer/{test_farmer.farmerid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_farm_by_id(self, client: TestClient, auth_headers: dict, test_farm):
        """Test getting farm by ID"""
        response = client.get(
            f"/api/v1/farms/{test_farm.farmid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["farmid"] == test_farm.farmid
        assert data["data"]["address"] is not None
    
    def test_get_farm_statistics(self, client: TestClient, auth_headers: dict, test_farm):
        """Test getting farm statistics"""
        response = client.get(
            "/api/v1/farms/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_farms" in data["data"]
        assert "total_farmsize_hectares" in data["data"]
    
    def test_update_farm(self, client: TestClient, auth_headers: dict, test_farm):
        """Test updating farm"""
        response = client.put(
            f"/api/v1/farms/{test_farm.farmid}",
            headers=auth_headers,
            json={"farmsize": 7.5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["data"]["farmsize"]) == 7.5
    
    def test_filter_farms_by_lga(self, client: TestClient, auth_headers: dict, test_farm, test_lga):
        """Test filtering farms by LGA"""
        response = client.get(
            f"/api/v1/farms/?lga_id={test_lga.lgaid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_filter_farms_by_farmtype(self, client: TestClient, auth_headers: dict, test_farm, test_farmtype):
        """Test filtering farms by farm type"""
        response = client.get(
            f"/api/v1/farms/?farmtype_id={test_farmtype.farmtypeid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True