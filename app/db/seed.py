from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.customer import Customer
from app.models.device import Device
from app.models.work_order import WorkOrder

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database(db: Session):
    # Check if data already exists
    if db.query(Customer).first():
        print("Database already seeded")
        return
    
    # Create test customers
    customer1 = Customer(
        name="John Doe",
        email="john@test.com",
        phone="555-1234",
        password_hash=pwd_context.hash("password123")
    )
    customer2 = Customer(
        name="Jane Smith",
        email="jane@test.com",
        phone="555-5678",
        password_hash=pwd_context.hash("password123")
    )
    
    db.add(customer1)
    db.add(customer2)
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)
    
    # Create test devices
    device1 = Device(
        device_type="Laptop",
        brand="Apple",
        model="MacBook Pro 16",
        serial_number="C02XG0FDH7JY",
        customer_id=customer1.id
    )
    device2 = Device(
        device_type="Phone",
        brand="Samsung",
        model="Galaxy S23",
        serial_number="SM-S911U",
        customer_id=customer1.id
    )
    
    db.add(device1)
    db.add(device2)
    db.commit()
    db.refresh(device1)
    db.refresh(device2)
    
    # Create test work orders
    work_order1 = WorkOrder(
        device_id=device1.id,
        description="Screen replacement - cracked display",
        status="in-progress",
        cost=299.99
    )
    work_order2 = WorkOrder(
        device_id=device2.id,
        description="Battery replacement",
        status="completed",
        cost=89.99
    )
    
    db.add(work_order1)
    db.add(work_order2)
    db.commit()
    
    print("✅ Database seeded successfully!")
    print("Test users:")
    print("  - john@test.com / password123")
    print("  - jane@test.com / password123")