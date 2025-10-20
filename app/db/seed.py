from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.customer import Customer, UserRole
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
    
    # Create test users with different roles
    admin = Customer(
        name="Admin User",
        email="admin@repairshop.com",
        phone="555-0001",
        password_hash=pwd_context.hash("admin123"),
        role=UserRole.ADMIN
    )
    
    technician = Customer(
        name="Tech Smith",
        email="tech@repairshop.com",
        phone="555-0002",
        password_hash=pwd_context.hash("tech123"),
        role=UserRole.TECHNICIAN
    )
    
    customer1 = Customer(
        name="John Doe",
        email="john@test.com",
        phone="555-1234",
        password_hash=pwd_context.hash("password123"),
        role=UserRole.CUSTOMER
    )
    
    customer2 = Customer(
        name="Jane Smith",
        email="jane@test.com",
        phone="555-5678",
        password_hash=pwd_context.hash("password123"),
        role=UserRole.CUSTOMER
    )
    
    db.add_all([admin, technician, customer1, customer2])
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)
    
    print(f"✅ Created users with roles")
    
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
    
    db.add_all([device1, device2, device3])
    db.commit()
    db.refresh(device1)
    db.refresh(device2)
    db.refresh(device3)
    
    print(f"✅ Created {db.query(Device).count()} devices")
    
    # Create test work orders
    work_order1 = WorkOrder(
        device_id=device1.id,
        title="Screen Replacement",
        description="Cracked display - needs full screen replacement",
        status="in_progress",
        cost=299.99
    )
    work_order2 = WorkOrder(
        device_id=device2.id,
        title="Battery Replacement",
        description="Battery health below 80%, customer requested replacement",
        status="completed",
        cost=89.99
    )
    work_order3 = WorkOrder(
        device_id=device3.id,
        title="Water Damage Repair",
        description="Device exposed to water, needs internal cleaning and inspection",
        status="pending",
        cost=199.99
    )
    
    db.add_all([work_order1, work_order2, work_order3])
    db.commit()
    
    print(f"✅ Created {db.query(WorkOrder).count()} work orders")
    print("✅ Database seeded successfully!")
    print("\n📋 Test users:")
    print("  Admin:      admin@repairshop.com / admin123")
    print("  Technician: tech@repairshop.com / tech123")
    print("  Customer:   john@test.com / password123")
    print("  Customer:   jane@test.com / password123")


    