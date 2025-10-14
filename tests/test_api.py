from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Repair Shop API is running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"

def test_create_customer():
    response = client.post(
        "/customers",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "555-0123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_customers():
    response = client.get("/customers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_customer_invalid_email():
    response = client.post(
        "/customers",
        json={
            "name": "Test User",
            "email": "invalid-email",  # Invalid email
            "phone": "555-0123"
        }
    )
    assert response.status_code == 422  # Validation error