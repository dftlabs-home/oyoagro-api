import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestPrimaryProductCRUD:
    def test_create_primaryproduct(self, client: TestClient, auth_headers: dict):
        response = client.post(
            "/api/v1/primaryproducts/create",
            headers=auth_headers,
            json={"name": "Cassava Flour"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Cassava Flour"
    
    def test_get_primaryproducts(self, client: TestClient, auth_headers: dict, test_primaryproduct):
        response = client.get("/api/v1/primaryproducts/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()["data"]) > 0
    
    def test_search_primaryproducts(self, client: TestClient, auth_headers: dict, test_primaryproduct):
        response = client.get(
            f"/api/v1/primaryproducts/search?q={test_primaryproduct.name[:3]}",
            headers=auth_headers
        )
        assert response.status_code == 200