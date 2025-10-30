"""
Tests for messaging system API endpoints
Comprehensive tests for customer-technician communication
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.db.base_class import Base
from app.models.customer import Customer
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.message import Message, SenderType
from app.core.security import create_access_token

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_messages.db"
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
def test_technician(db):
    """Create a test technician"""
    tech = Customer(
        name="Tech Support",
        email="tech@example.com",
        phone="555-0200",
        password_hash="dummy_hash"
    )
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@pytest.fixture
def test_work_order(db, test_customer, test_technician):
    """Create a test work order"""
    work_order = WorkOrder(
        customer_id=test_customer.id,
        title="Screen Replacement",
        description="iPhone screen cracked, needs replacement",
        status=WorkOrderStatus.IN_PROGRESS,
        assigned_technician=test_technician.name,
        created_at=datetime.utcnow()
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    return work_order


@pytest.fixture
def test_messages(db, test_work_order, test_customer, test_technician):
    """Create test messages"""
    messages = [
        Message(
            work_order_id=test_work_order.id,
            sender_id=test_customer.id,
            sender_type=SenderType.CUSTOMER,
            message="When will my repair be done?",
            is_read=0,
            created_at=datetime.utcnow()
        ),
        Message(
            work_order_id=test_work_order.id,
            sender_id=test_technician.id,
            sender_type=SenderType.TECHNICIAN,
            message="Should be ready by tomorrow",
            is_read=0,
            created_at=datetime.utcnow()
        ),
        Message(
            work_order_id=test_work_order.id,
            sender_id=0,
            sender_type=SenderType.SYSTEM,
            message="Work order status changed to In Progress",
            is_read=1,
            created_at=datetime.utcnow()
        )
    ]
    for msg in messages:
        db.add(msg)
    db.commit()
    return messages


@pytest.fixture
def auth_token(test_customer):
    """Generate JWT token for test customer"""
    return create_access_token({"sub": test_customer.email, "customer_id": test_customer.id})


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


# ==================== TESTS ====================

def test_get_message_thread_success(client, auth_headers, test_work_order, test_messages):
    """Test getting messages for a work order"""
    response = client.get(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "messages" in data
    assert "work_order_id" in data
    assert "total_messages" in data
    assert "unread_count" in data
    
    assert data["work_order_id"] == test_work_order.id
    assert data["total_messages"] == 3
    assert len(data["messages"]) == 3
    
    # Check message content
    assert data["messages"][0]["message"] == "When will my repair be done?"
    assert data["messages"][0]["sender_type"] == "customer"
    assert data["messages"][1]["sender_type"] == "technician"
    assert data["messages"][2]["sender_type"] == "system"


def test_get_message_thread_unauthorized(client, test_work_order):
    """Test getting messages without authentication"""
    response = client.get(f"/api/customers/messages/work-order/{test_work_order.id}")
    assert response.status_code == 403


def test_get_message_thread_wrong_customer(client, db, test_work_order):
    """Test getting messages for someone else's work order"""
    # Create another customer
    other_customer = Customer(
        name="Other User",
        email="other@example.com",
        phone="555-9999",
        password_hash="dummy_hash"
    )
    db.add(other_customer)
    db.commit()
    
    # Create token for other customer
    other_token = create_access_token({
        "sub": other_customer.email,
        "customer_id": other_customer.id
    })
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    response = client.get(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=other_headers
    )
    
    assert response.status_code == 404


def test_send_message_success(client, auth_headers, test_work_order):
    """Test sending a new message"""
    response = client.post(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=auth_headers,
        json={"message": "Thanks for the update!"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["message"] == "Thanks for the update!"
    assert data["sender_type"] == "customer"
    assert "id" in data
    assert "created_at" in data
    assert data["is_read"] == False


def test_send_empty_message(client, auth_headers, test_work_order):
    """Test sending an empty message (should fail validation)"""
    response = client.post(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=auth_headers,
        json={"message": ""}
    )
    
    assert response.status_code == 422  # Validation error


def test_send_message_to_nonexistent_work_order(client, auth_headers):
    """Test sending message to work order that doesn't exist"""
    response = client.post(
        "/api/customers/messages/work-order/99999",
        headers=auth_headers,
        json={"message": "Test message"}
    )
    
    assert response.status_code == 404


def test_mark_messages_as_read(client, auth_headers, test_messages):
    """Test marking messages as read"""
    message_ids = [msg.id for msg in test_messages[:2]]
    
    response = client.put(
        "/api/customers/messages/mark-read",
        headers=auth_headers,
        json={"message_ids": message_ids}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "marked_count" in data
    assert data["marked_count"] == 2


def test_mark_read_empty_list(client, auth_headers):
    """Test marking messages with empty ID list"""
    response = client.put(
        "/api/customers/messages/mark-read",
        headers=auth_headers,
        json={"message_ids": []}
    )
    
    assert response.status_code == 400


def test_get_unread_count(client, auth_headers, test_messages):
    """Test getting unread message count"""
    response = client.get(
        "/api/customers/messages/unread-count",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "unread_count" in data
    # Should count only unread technician messages (1 in fixtures)
    assert data["unread_count"] == 1


def test_get_recent_messages(client, auth_headers, test_work_order, test_messages):
    """Test getting recent messages"""
    response = client.get(
        "/api/customers/messages/recent?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("work_order_id" in msg for msg in data)
    assert all("message" in msg for msg in data)


def test_message_ordering(client, auth_headers, test_work_order):
    """Test that messages are returned in chronological order"""
    # Send multiple messages
    messages_text = ["First message", "Second message", "Third message"]
    
    for text in messages_text:
        client.post(
            f"/api/customers/messages/work-order/{test_work_order.id}",
            headers=auth_headers,
            json={"message": text}
        )
    
    # Get messages
    response = client.get(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=auth_headers
    )
    
    data = response.json()
    messages = data["messages"]
    
    # Find our sent messages (should be last 3)
    sent_messages = [msg for msg in messages if msg["message"] in messages_text]
    assert len(sent_messages) == 3
    
    # Check chronological order
    assert sent_messages[0]["message"] == "First message"
    assert sent_messages[1]["message"] == "Second message"
    assert sent_messages[2]["message"] == "Third message"


def test_work_order_not_found(client, auth_headers):
    """Test getting messages for non-existent work order"""
    response = client.get(
        "/api/customers/messages/work-order/99999",
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_message_includes_sender_info(client, auth_headers, test_work_order, test_messages):
    """Test that messages include sender name and avatar fields"""
    response = client.get(
        f"/api/customers/messages/work-order/{test_work_order.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    for msg in data["messages"]:
        assert "sender_name" in msg
        assert "sender_avatar" in msg
        assert msg["sender_name"] is not None


def test_unread_count_only_counts_technician_messages(client, auth_headers, db, test_work_order, test_customer, test_technician):
    """Test that unread count only includes technician messages, not customer's own"""
    # Add customer message (unread)
    customer_msg = Message(
        work_order_id=test_work_order.id,
        sender_id=test_customer.id,
        sender_type=SenderType.CUSTOMER,
        message="Customer message",
        is_read=0
    )
    db.add(customer_msg)
    
    # Add technician message (unread)
    tech_msg = Message(
        work_order_id=test_work_order.id,
        sender_id=test_technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="Technician message",
        is_read=0
    )
    db.add(tech_msg)
    db.commit()
    
    response = client.get(
        "/api/customers/messages/unread-count",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only count the technician message
    assert data["unread_count"] == 1


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])