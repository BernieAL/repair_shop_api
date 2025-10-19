from app.db.session import engine
from app.db.base_class import Base

# Import all models so they're registered with Base
from app.models.customer import Customer
from app.models.device import Device
from app.models.work_order import WorkOrder

def create_tables():
    """Create all database tables"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {', '.join(tables)}")

if __name__ == "__main__":
    create_tables()
