import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestLivestockCRUD:
    def test_create_livestock(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/livestock/create",
            headers=auth_headers,
            json={"name": "Goats"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Goats"
    
    def test_get_livestock(self, client: TestClient, auth_headers: dict, test_livestock):
        response = client.get("/api/v1/livestock/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()["data"]) > 0
    
    def test_search_livestock(self, client: TestClient, auth_headers: dict, test_livestock):
        response = client.get(
            f"/api/v1/livestock/search?q={test_livestock.name[:3]}",
            headers=auth_headers
        )
        assert response.status_code == 200