"""
FILE: tests/test_farmers.py
Test cases for Farmer endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.farmers
@pytest.mark.integration
class TestFarmerCRUD:
    """Test Farmer CRUD operations"""
    
    def test_create_farmer(self, client: TestClient, auth_headers: dict, test_association, test_lga):
        """Test creating farmer"""
        response = client.post(
            "/api/v1/farmers/create",
            headers=auth_headers,
            json={
                "firstname": "Jane",
                "lastname": "Doe",
                "gender": "Female",
                "dateofbirth": "1990-03-15",
                "phonenumber": "08098765432",
                "email": "jane.doe@example.com",
                "associationid": test_association.associationid,
                "householdsize": 4,
                "availablelabor": 2,
                "address": {
                    "streetaddress": "456 Village Road",
                    "town": "Ibadan",
                    "postalcode": "200002",
                    "lgaid": test_lga.lgaid,
                    "latitude": 7.3800,
                    "longitude": 3.9500
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["firstname"] == "Jane"
        assert data["data"]["address"] is not None
    
    def test_create_farmer_invalid_phone(self, client: TestClient, auth_headers: dict, test_association, test_lga):
        """Test creating farmer with invalid phone fails"""
        response = client.post(
            "/api/v1/farmers/create",
            headers=auth_headers,
            json={
                "firstname": "Test",
                "lastname": "User",
                "gender": "Male",
                "dateofbirth": "1990-01-01",
                "phonenumber": "12345",  # Invalid
                "householdsize": 4,
                "availablelabor": 2,
                "address": {
                    "lgaid": test_lga.lgaid
                }
            }
        )
        
        assert response.status_code == 422
    
    def test_create_farmer_duplicate_phone(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test creating farmer with duplicate phone fails"""
        response = client.post(
            "/api/v1/farmers/create",
            headers=auth_headers,
            json={
                "firstname": "Another",
                "lastname": "Farmer",
                "gender": "Male",
                "dateofbirth": "1990-01-01",
                "phonenumber": test_farmer.phonenumber,
                "householdsize": 4,
                "availablelabor": 2,
                "address": {
                    "lgaid": 1
                }
            }
        )
        
        assert response.status_code == 400
    
    def test_get_farmers(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test getting all farmers"""
        response = client.get(
            "/api/v1/farmers/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_farmer_by_id(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test getting farmer by ID"""
        response = client.get(
            f"/api/v1/farmers/{test_farmer.farmerid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["farmerid"] == test_farmer.farmerid
        assert data["data"]["address"] is not None
    
    def test_get_farmer_statistics(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test getting farmer statistics"""
        response = client.get(
            "/api/v1/farmers/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_farmers" in data["data"]
        assert "male_farmers" in data["data"]
    
    def test_search_farmers(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test searching farmers"""
        response = client.get(
            f"/api/v1/farmers/search?q={test_farmer.firstname}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_farmer(self, client: TestClient, auth_headers: dict, test_farmer):
        """Test updating farmer"""
        response = client.put(
            f"/api/v1/farmers/{test_farmer.farmerid}",
            headers=auth_headers,
            json={"householdsize": 6}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["householdsize"] == 6
    
    def test_delete_farmer_with_farms_fails(self, client: TestClient, auth_headers: dict, test_farmer, test_farm):
        """Test deleting farmer with farms fails"""
        response = client.delete(
            f"/api/v1/farmers/{test_farmer.farmerid}",
            headers=auth_headers
        )
        
        assert response.status_code == 400