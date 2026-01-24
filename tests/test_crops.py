"""
FILE: tests/test_crops.py
Test cases for Crop endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestCropCRUD:
    """Test Crop CRUD operations"""
    
    def test_create_crop(self, client: TestClient, auth_headers: dict):
        """Test creating crop"""
        response = client.post(
            "/api/v1/crops/create",
            headers=auth_headers,
            json={"name": "Maize"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Maize"
    
    def test_create_duplicate_crop(self, client: TestClient, auth_headers: dict, test_crop):
        """Test creating duplicate crop fails"""
        response = client.post(
            "/api/v1/crops/create",
            headers=auth_headers,
            json={"name": test_crop.name}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_crops(self, client: TestClient, auth_headers: dict, test_crop):
        """Test getting all crops"""
        response = client.get(
            "/api/v1/crops/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
    
    def test_get_crops_with_counts(self, client: TestClient, auth_headers: dict, test_crop):
        """Test getting crops with registry counts"""
        response = client.get(
            "/api/v1/crops/with-counts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "registry_count" in data["data"][0]
    
    def test_get_crop_by_id(self, client: TestClient, auth_headers: dict, test_crop):
        """Test getting crop by ID"""
        response = client.get(
            f"/api/v1/crops/{test_crop.croptypeid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["croptypeid"] == test_crop.croptypeid
    
    def test_get_crop_stats(self, client: TestClient, auth_headers: dict, test_crop):
        """Test getting crop statistics"""
        response = client.get(
            f"/api/v1/crops/{test_crop.croptypeid}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "registry_count" in data["data"]
        assert "total_area_planted" in data["data"]
    
    def test_search_crops(self, client: TestClient, auth_headers: dict, test_crop):
        """Test searching crops"""
        response = client.get(
            f"/api/v1/crops/search?q={test_crop.name[:3]}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_crop(self, client: TestClient, auth_headers: dict, test_crop):
        """Test updating crop"""
        response = client.put(
            f"/api/v1/crops/{test_crop.croptypeid}",
            headers=auth_headers,
            json={"name": "Updated Crop Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Crop Name"
    
    def test_delete_crop_without_registries(self, client: TestClient, auth_headers: dict, session):
        """Test deleting crop without registries"""
        from src.shared.models import Crop
        from datetime import datetime
        
        # Create a crop directly
        crop = Crop(name="Deletable Crop", createdat=datetime.utcnow())
        session.add(crop)
        session.commit()
        session.refresh(crop)
        
        response = client.delete(
            f"/api/v1/crops/{crop.croptypeid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_unauthenticated_access(self, client: TestClient):
        """Test unauthenticated access is denied"""
        response = client.get("/api/v1/crops/")
        assert response.status_code == 401