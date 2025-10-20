import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db

# Import all models so they're registered with Base
from app.models.customer import Customer
from app.models.device import Device
from app.models.work_order import WorkOrder

from app.models.customer import Customer, UserRole
from app.core.security import get_password_hash

# Use SQLite in-memory database for tests (no PostgreSQL needed!)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database session for each test.
    Creates all tables before the test and drops them after.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with the test database.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client, db):
    """Create an admin user and return auth token"""
    # Create admin user
    admin = Customer(
        name="Admin Test",
        email="admin@test.com",
        phone="555-0000",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    
    # Login and get token
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return response.json()["access_token"]


@pytest.fixture
def customer_token(client, db):
    """Create a customer user and return auth token"""
    # Create customer user
    customer = Customer(
        name="Customer Test",
        email="customer@test.com",
        phone="555-0001",
        password_hash=get_password_hash("customer123"),
        role=UserRole.CUSTOMER
    )
    db.add(customer)
    db.commit()
    
    # Login and get token
    response = client.post("/api/auth/login", json={
        "email": "customer@test.com",
        "password": "customer123"
    })
    return response.json()["access_token"]