import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestBusinessTypeCRUD:
    def test_create_businesstype(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/businesstypes/create",
            headers=auth_headers,
            json={"name": "Processing"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Processing"
    
    def test_get_businesstypes(self, client: TestClient, auth_headers: dict, test_businesstype):
        response = client.get("/api/v1/businesstypes/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()["data"]) > 0
    
    def test_get_with_counts(self, client: TestClient, auth_headers: dict, test_businesstype):
        response = client.get("/api/v1/businesstypes/with-counts", headers=auth_headers)
        assert response.status_code == 200
        assert "registry_count" in response.json()["data"][0]