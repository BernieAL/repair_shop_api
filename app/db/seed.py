from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.customer import Customer
from app.models.device import Device
from app.models.work_order import WorkOrder

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database(db: Session):
    """Seed database with test data"""
    
    # Check if data already exists
    existing = db.query(Customer).first()
    if existing:
        print("⚠️  Database already seeded - found existing customer:", existing.email)
        return
    
    print("📝 No existing data found, inserting seed data...")
    
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
    
    print(f"✅ Created customers: {customer1.email}, {customer2.email}")
    
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
    device3 = Device(
        device_type="Tablet",
        brand="Apple",
        model="iPad Pro",
        serial_number="DMPH2LL/A",
        customer_id=customer2.id
    )
    
    db.add(device1)
    db.add(device2)
    db.add(device3)
    db.commit()
    db.refresh(device1)
    db.refresh(device2)
    db.refresh(device3)
    
    print(f"✅ Created {db.query(Device).count()} devices")
    
    # Create test work orders
    work_order1 = WorkOrder(
        device_id=device1.id,
        title="Screen Replacement",  # ← ADD THIS
        description="Cracked display - needs full screen replacement",
        status="in_progress",
        cost=299.99
    )
    work_order2 = WorkOrder(
        device_id=device2.id,
        title="Battery Replacement",  # ← ADD THIS
        description="Battery health below 80%, customer requested replacement",
        status="completed",
        cost=89.99
    )
    work_order3 = WorkOrder(
        device_id=device3.id,
        title="Water Damage Repair",  # ← ADD THIS
        description="Device exposed to water, needs internal cleaning and inspection",
        status="pending",
        cost=199.99
    )
    
    db.add(work_order1)
    db.add(work_order2)
    db.add(work_order3)
    db.commit()
    
    print(f"✅ Created {db.query(WorkOrder).count()} work orders")
    print("✅ Database seeded successfully!")
    print("\nTest users:")
    print("  - john@test.com / password123")
    print("  - jane@test.com / password123")