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


def test_register_and_login(client, db):
    """Test user registration and login flow"""
    # Register a new user
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0123",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Login with same credentials
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, db):
    """Test getting current user info"""
    # Register and get token
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0123",
        "password": "testpassword123"
    }
    
    response = client.post("/api/auth/register", json=register_data)
    token = response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert data["role"] == "customer"  # Default role


def test_authentication_required(client, db):
    """Test that protected endpoints require authentication"""
    # Try to access protected endpoint without token
    response = client.get("/api/customers")
    assert response.status_code == 403  # Forbidden (no auth header)


def test_admin_can_get_customers(client, db, admin_token):
    """Test that admin can access customer list"""
    response = client.get(
        "/api/customers",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least the admin user
    assert len(data) >= 1


def test_customer_cannot_get_all_customers(client, db, customer_token):
    """Test that regular customer cannot access customer list"""
    response = client.get(
        "/api/customers",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_customer_can_get_own_devices(client, db, customer_token):
    """Test that customer can see their own devices"""
    response = client.get(
        "/api/devices",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)