"""
Tests for notification system API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.db.base_class import Base
from app.models.user import Customer
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.notification import Notification, NotificationType
from app.core.security import create_access_token

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_notifications.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_customer(db):
    """Create a test customer"""
    customer = Customer(
        name="John Test",
        email="test@example.com",
        phone="555-0100",
        password_hash="dummy_hash"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def test_work_order(db, test_customer):
    """Create a test work order"""
    work_order = WorkOrder(
        customer_id=test_customer.id,
        title="Screen Replacement",
        description="iPhone screen cracked",
        status=WorkOrderStatus.IN_PROGRESS,
        created_at=datetime.utcnow()
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order


@pytest.fixture
def test_notifications(db, test_customer, test_work_order):
    """Create test notifications"""
    notifications = [
        Notification(
            customer_id=test_customer.id,
            work_order_id=test_work_order.id,
            type=NotificationType.MESSAGE,
            title="New message from technician",
            message="Your repair is being processed",
            read=False,
            created_at=datetime.utcnow()
        ),
        Notification(
            customer_id=test_customer.id,
            work_order_id=test_work_order.id,
            type=NotificationType.STATUS_CHANGE,
            title="Status updated",
            message="Your repair status changed to In Progress",
            read=False,
            created_at=datetime.utcnow()
        ),
        Notification(
            customer_id=test_customer.id,
            work_order_id=test_work_order.id,
            type=NotificationType.COMPLETED,
            title="Repair completed",
            message="Your device is ready for pickup",
            read=True,
            created_at=datetime.utcnow()
        ),
    ]
    for notif in notifications:
        db.add(notif)
    db.commit()
    return notifications


@pytest.fixture
def auth_token(test_customer):
    """Generate JWT token for test customer"""
    return create_access_token({"sub": test_customer.email, "customer_id": test_customer.id})


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


# ==================== TESTS ====================

def test_get_all_notifications(client, auth_headers, test_notifications):
    """Test getting all notifications"""
    response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 3
    assert all("id" in notif for notif in data)
    assert all("type" in notif for notif in data)
    assert all("title" in notif for notif in data)


def test_get_notifications_unread_only(client, auth_headers, test_notifications):
    """Test getting only unread notifications"""
    response = client.get(
        "/api/customers/notifications/?unread_only=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2  # Only 2 unread notifications
    assert all(not notif["read"] for notif in data)


def test_get_notifications_pagination(client, auth_headers, test_notifications):
    """Test notification pagination"""
    response = client.get(
        "/api/customers/notifications/?skip=1&limit=1",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1


def test_get_notifications_unauthorized(client):
    """Test getting notifications without authentication"""
    response = client.get("/api/customers/notifications/")
    assert response.status_code == 403


def test_mark_notification_as_read(client, auth_headers, test_notifications):
    """Test marking a notification as read"""
    unread_notif = test_notifications[0]
    
    response = client.put(
        f"/api/customers/notifications/{unread_notif.id}/read",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Verify it was marked as read
    get_response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    notifications = get_response.json()
    marked_notif = next(n for n in notifications if n["id"] == unread_notif.id)
    assert marked_notif["read"] == True


def test_mark_nonexistent_notification_as_read(client, auth_headers):
    """Test marking non-existent notification as read"""
    response = client.put(
        "/api/customers/notifications/99999/read",
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_mark_other_users_notification_as_read(client, db, test_notifications):
    """Test that user cannot mark another user's notification as read"""
    # Create another user
    other_user = Customer(
        name="Other User",
        email="other@example.com",
        phone="555-9999",
        password_hash="dummy_hash"
    )
    db.add(other_user)
    db.commit()
    
    other_token = create_access_token({
        "sub": other_user.email,
        "customer_id": other_user.id
    })
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to mark first user's notification as read
    response = client.put(
        f"/api/customers/notifications/{test_notifications[0].id}/read",
        headers=other_headers
    )
    
    assert response.status_code == 404


def test_mark_all_notifications_as_read(client, auth_headers, test_notifications):
    """Test marking all notifications as read"""
    response = client.put(
        "/api/customers/notifications/read-all",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Verify all are marked as read
    get_response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    notifications = get_response.json()
    assert all(notif["read"] for notif in notifications)


def test_get_unread_count(client, auth_headers, test_notifications):
    """Test getting unread notification count"""
    response = client.get(
        "/api/customers/notifications/unread-count",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "unread_count" in data
    assert data["unread_count"] == 2  # 2 unread notifications in fixture


def test_unread_count_after_marking_read(client, auth_headers, test_notifications):
    """Test unread count decreases after marking as read"""
    # Mark one as read
    client.put(
        f"/api/customers/notifications/{test_notifications[0].id}/read",
        headers=auth_headers
    )
    
    # Check unread count
    response = client.get(
        "/api/customers/notifications/unread-count",
        headers=auth_headers
    )
    
    data = response.json()
    assert data["unread_count"] == 1  # Should be 1 now


def test_notification_ordering(client, auth_headers, db, test_customer):
    """Test that notifications are ordered by creation time (newest first)"""
    # Create notifications with different timestamps
    import time
    
    old_notif = Notification(
        customer_id=test_customer.id,
        type=NotificationType.MESSAGE,
        title="Old notification",
        message="This is old",
        read=False,
        created_at=datetime(2024, 1, 1)
    )
    db.add(old_notif)
    db.commit()
    
    time.sleep(0.1)
    
    new_notif = Notification(
        customer_id=test_customer.id,
        type=NotificationType.MESSAGE,
        title="New notification",
        message="This is new",
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(new_notif)
    db.commit()
    
    # Get notifications
    response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    
    notifications = response.json()
    assert len(notifications) >= 2
    
    # Newest should be first
    assert notifications[0]["title"] == "New notification"


def test_notification_includes_work_order_id(client, auth_headers, test_notifications):
    """Test that notifications include work_order_id when present"""
    response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    
    notifications = response.json()
    
    # Check that work_order_id is present
    assert all("work_order_id" in notif for notif in notifications)
    assert notifications[0]["work_order_id"] is not None


def test_notification_types_are_valid(client, auth_headers, test_notifications):
    """Test that notification types match the enum"""
    response = client.get(
        "/api/customers/notifications/",
        headers=auth_headers
    )
    
    notifications = response.json()
    valid_types = ["status_change", "tech_note", "completed", "message"]

    
    for notif in notifications:
        assert notif["type"] in valid_types


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])