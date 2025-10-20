import pytest
from fastapi.testclient import TestClient

def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Repair Shop API is running"} 

def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

def test_create_customer(client, db):
    """Test creating a customer"""
    customer_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0123"
    }
    response = client.post("/api/customers", json=customer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == customer_data["email"]
    assert data["name"] == customer_data["name"]
    assert "id" in data

def test_get_customers(client, db):
    """Test getting all customers"""
    # Create a test customer first
    customer_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0123"
    }
    client.post("/api/customers", json=customer_data)
    
    # Get all customers
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1