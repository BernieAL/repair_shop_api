from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.models.user import User  # Changed from UserRole
from app.models.user_role import UserRole  # Import the enum separately
from app.models.device import Device
from app.models.work_order import WorkOrder
from app.models.message import Message, SenderType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database(db: Session):
    """Seed database with test data"""
    # Check if data already exists
    existing = db.query(User).first()  # Changed from UserRole
    if existing:
        print("⚠️  Database already seeded - found existing user:", existing.email)
        return
    
    print("📝 No existing data found, inserting seed data...")
    
    # Create test users with different roles
    admin = User(  # Changed from UserRole
        name="Admin User",
        email="admin@repairshop.com",
        phone="555-0001",
        password_hash=pwd_context.hash("admin123"),
        role=UserRole.ADMIN
    )
    
    technician = User(  # Changed from UserRole
        name="Tech Smith",
        email="tech@repairshop.com",
        phone="555-0002",
        password_hash=pwd_context.hash("tech123"),
        role=UserRole.TECHNICIAN
    )
    
    customer1 = User(  # Changed from UserRole
        name="John Doe",
        email="john@test.com",
        phone="555-1234",
        password_hash=pwd_context.hash("password123"),
        role=UserRole.USER  # Changed from CUSTOMER
    )
    
    customer2 = User(  # Changed from UserRole
        name="Jane Smith",
        email="jane@test.com",
        phone="555-5678",
        password_hash=pwd_context.hash("password123"),
        role=UserRole.USER  # Changed from CUSTOMER
    )
    
    db.add_all([admin, technician, customer1, customer2])
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)
    db.refresh(technician)
    print(f"✅ Created users with roles")
    
    # Create test devices
    device1 = Device(
        device_type="Laptop",
        brand="Apple",
        model="MacBook Pro 16",
        serial_number="C02XG0FDH7JY",
        owner_id=customer1.id  # Changed from customer_id
    )
    
    device2 = Device(
        device_type="Phone",
        brand="Samsung",
        model="Galaxy S23",
        serial_number="SM-S911U",
        owner_id=customer1.id  # Changed from customer_id
    )
    
    device3 = Device(
        device_type="Tablet",
        brand="Apple",
        model="iPad Pro",
        serial_number="DMPH2LL/A",
        owner_id=customer2.id  # Changed from customer_id
    )
    
    device4 = Device(
        device_type="Laptop",
        brand="Dell",
        model="XPS 13",
        serial_number="DL123456",
        owner_id=customer1.id  # Changed from customer_id
    )
    
    device5 = Device(
        device_type="Phone",
        brand="Apple",
        model="iPhone 14 Pro",
        serial_number="APPL789",
        owner_id=customer1.id  # Changed from customer_id
    )
    
    db.add_all([device1, device2, device3, device4, device5])
    db.commit()
    db.refresh(device1)
    db.refresh(device2)
    db.refresh(device3)
    db.refresh(device4)
    db.refresh(device5)
    print(f"✅ Created {db.query(Device).count()} devices")
    
    # Create test work orders
    work_order1 = WorkOrder(
        customer_id=customer1.id,
        device_id=device1.id,
        title="Screen Replacement",
        description="Cracked display - needs full screen replacement",
        status="in_progress",
        cost=299.99
    )
    
    work_order2 = WorkOrder(
        customer_id=customer1.id,
        device_id=device2.id,
        title="Battery Replacement",
        description="Battery health below 80%, customer requested replacement",
        status="completed",
        cost=89.99
    )
    
    work_order3 = WorkOrder(
        customer_id=customer2.id,
        device_id=device3.id,
        title="Water Damage Repair",
        description="Device exposed to water, needs internal cleaning and inspection",
        status="pending",
        cost=199.99
    )
    
    # Additional pending repairs for John
    work_order4 = WorkOrder(
        customer_id=customer1.id,
        device_id=device4.id,
        title="Keyboard Not Working",
        description="Several keys on keyboard not responding. Possible liquid damage.",
        status="pending",
        cost=150.00
    )
    
    work_order5 = WorkOrder(
        customer_id=customer1.id,
        device_id=device5.id,
        title="Camera Lens Cracked",
        description="Rear camera lens is cracked, affecting photo quality",
        status="pending",
        cost=129.99
    )
    
    work_order6 = WorkOrder(
        customer_id=customer1.id,
        device_id=device2.id,
        title="Charging Port Loose",
        description="USB-C port is loose and doesn't hold cable properly",
        status="pending",
        cost=75.00
    )
    
    db.add_all([work_order1, work_order2, work_order3, work_order4, work_order5, work_order6])
    db.commit()
    db.refresh(work_order1)
    db.refresh(work_order2)
    db.refresh(work_order3)
    db.refresh(work_order4)
    db.refresh(work_order5)
    db.refresh(work_order6)
    print(f"✅ Created {db.query(WorkOrder).count()} work orders")
    
    # Create test messages
    now = datetime.utcnow()
    
    # Messages for work_order1 (Screen Replacement - in progress)
    message1 = Message(
        work_order_id=work_order1.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="Hi! Just wondering when my MacBook screen replacement will be ready?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=3)
    )
    
    message2 = Message(
        work_order_id=work_order1.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="Hi John! We've received your MacBook and are currently working on the screen replacement. The new display has arrived and we're installing it now.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(hours=2)
    )
    
    message3 = Message(
        work_order_id=work_order1.id,
        sender_id=None,  # Changed from 0
        sender_type=SenderType.SYSTEM,
        message="Repair status updated to: In Progress",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=2, minutes=30)
    )
    
    message4 = Message(
        work_order_id=work_order1.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="Good news! The screen replacement is complete. We're now running quality tests and should have it ready for pickup by end of day.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(minutes=45)
    )
    
    message5 = Message(
        work_order_id=work_order1.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="That's great! Thank you for the update. What time can I pick it up?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(minutes=30)
    )
    
    # Messages for work_order2 (Battery Replacement - completed)
    message6 = Message(
        work_order_id=work_order2.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="My phone's battery drains really fast. Can you check it?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(days=2)
    )
    
    message7 = Message(
        work_order_id=work_order2.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="We've run diagnostics and your battery health is at 76%. We recommend a replacement. Cost will be $89.99.",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(days=1, hours=20)
    )
    
    message8 = Message(
        work_order_id=work_order2.id,
        sender_id=None,  # Changed from 0
        sender_type=SenderType.SYSTEM,
        message="Repair status updated to: Completed",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(days=1)
    )
    
    message9 = Message(
        work_order_id=work_order2.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="Your Galaxy S23 battery replacement is complete! Ready for pickup anytime during business hours.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(days=1)
    )
    
    # Messages for work_order3 (Water Damage - Jane's repair)
    message10 = Message(
        work_order_id=work_order3.id,
        sender_id=customer2.id,
        sender_type=SenderType.CUSTOMER,
        message="I accidentally spilled water on my iPad. It's not turning on. Can you help?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=5)
    )
    
    message11 = Message(
        work_order_id=work_order3.id,
        sender_id=None,  # Changed from 0
        sender_type=SenderType.SYSTEM,
        message="Work order created. A technician will review your device soon.",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=5)
    )
    
    message12 = Message(
        work_order_id=work_order3.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="We've received your iPad. We'll open it up for inspection and cleaning. I'll update you within 2 hours with a full diagnosis.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(hours=4)
    )
    
    # Messages for work_order4 (Keyboard Not Working - pending)
    message13 = Message(
        work_order_id=work_order4.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="Several keys on my Dell XPS aren't working. I think I may have spilled coffee on it last week.",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=6)
    )
    
    message14 = Message(
        work_order_id=work_order4.id,
        sender_id=None,  # Changed from 0
        sender_type=SenderType.SYSTEM,
        message="Work order received. We'll inspect your device shortly.",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=6)
    )
    
    # Messages for work_order5 (Camera Lens - pending)
    message15 = Message(
        work_order_id=work_order5.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="I dropped my iPhone and now the camera lens is cracked. Can you replace just the lens?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=8)
    )
    
    message16 = Message(
        work_order_id=work_order5.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="Yes, we can replace just the camera lens. It should be ready in 1-2 business days. We'll update you once we start the repair.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(hours=7)
    )
    
    # Messages for work_order6 (Charging Port - pending)
    message17 = Message(
        work_order_id=work_order6.id,
        sender_id=customer1.id,
        sender_type=SenderType.CUSTOMER,
        message="The charging cable keeps falling out of my Samsung phone. Is this fixable?",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=10)
    )
    
    message18 = Message(
        work_order_id=work_order6.id,
        sender_id=None,  # Changed from 0
        sender_type=SenderType.SYSTEM,
        message="Work order created successfully.",
        is_read=True,  # Changed from 1
        created_at=now - timedelta(hours=10)
    )
    
    message19 = Message(
        work_order_id=work_order6.id,
        sender_id=technician.id,
        sender_type=SenderType.TECHNICIAN,
        message="This is a common issue. We'll need to replace the charging port. Estimated cost is $75. We have the part in stock.",
        is_read=False,  # Changed from 0
        created_at=now - timedelta(hours=9)
    )
    
    db.add_all([
        message1, message2, message3, message4, message5,
        message6, message7, message8, message9,
        message10, message11, message12,
        message13, message14, message15, message16,
        message17, message18, message19
    ])
    db.commit()
    print(f"✅ Created {db.query(Message).count()} messages")
    
    print("✅ Database seeded successfully!")
    print("\n📋 Test users:")
    print("  Admin:      admin@repairshop.com / admin123")
    print("  Technician: tech@repairshop.com / tech123")
    print("  User:       john@test.com / password123 (6 work orders)")  # Changed from Customer
    print("  User:       jane@test.com / password123 (1 work order)")  # Changed from Customer
    print("\n💬 Message threads created:")
    print("  - Work Order 1 (Screen Replacement - In Progress): 5 messages")
    print("  - Work Order 2 (Battery Replacement - Completed): 4 messages")
    print("  - Work Order 3 (Water Damage - Pending): 3 messages")
    print("  - Work Order 4 (Keyboard Not Working - Pending): 2 messages")
    print("  - Work Order 5 (Camera Lens - Pending): 2 messages")
    print("  - Work Order 6 (Charging Port - Pending): 3 messages")