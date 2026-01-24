"""
FILE: tests/test_associations.py
Test cases for Association endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.associations
@pytest.mark.integration
class TestAssociationCRUD:
    """Test Association CRUD operations"""
    
    def test_create_association(self, client: TestClient, auth_headers: dict):
        """Test creating association"""
        response = client.post(
            "/api/v1/associations/create",
            headers=auth_headers,
            json={
                "name": "Test Farmers Association",
                "registrationno": "TFA-001"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Farmers Association"
        assert data["data"]["registrationno"] == "TFA-001"
    
    def test_create_duplicate_association(self, client: TestClient, auth_headers: dict, test_association):
        """Test creating duplicate association fails"""
        response = client.post(
            "/api/v1/associations/create",
            headers=auth_headers,
            json={
                "name": test_association.name,
                "registrationno": "DIFF-001"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_associations(self, client: TestClient, auth_headers: dict, test_association):
        """Test getting all associations"""
        response = client.get(
            "/api/v1/associations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_association_by_id(self, client: TestClient, auth_headers: dict, test_association):
        """Test getting association by ID"""
        response = client.get(
            f"/api/v1/associations/{test_association.associationid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["associationid"] == test_association.associationid
    
    def test_update_association(self, client: TestClient, auth_headers: dict, test_association):
        """Test updating association"""
        response = client.put(
            f"/api/v1/associations/{test_association.associationid}",
            headers=auth_headers,
            json={"name": "Updated Association Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Association Name"
    
    def test_search_associations(self, client: TestClient, auth_headers: dict, test_association):
        """Test searching associations"""
        response = client.get(
            "/api/v1/associations/search?q=Oyo",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_association_with_farmers_fails(self, client: TestClient, auth_headers: dict, test_association, test_farmer):
        """Test deleting association with farmers fails"""
        response = client.delete(
            f"/api/v1/associations/{test_association.associationid}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "farmers" in response.json()["detail"].lower()
    
    def test_unauthenticated_access_denied(self, client: TestClient):
        """Test unauthenticated access is denied"""
        response = client.get("/api/v1/associations/getassociations")
        # Should return 401 Unauthorized
        assert response.status_code == 401