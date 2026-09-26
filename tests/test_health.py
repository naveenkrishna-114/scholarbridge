import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the /api/health endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "Personalized Scholarship Recommendation System"
    assert "version" in data

def test_index_route(client):
    """Test that root route responds with 200 and json message when requested."""
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["health_endpoint"] == "/api/health"
