from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base_class import Base

# Import all models so they're registered with Base
from app.models.customer import Customer
from app.models.device import Device
from app.models.work_order import WorkOrder

def init_db():
    """Initialize database with tables and seed data"""
    print("🔧 Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables: {', '.join(tables)}")
    
    # Seed database with test data
    print("🌱 Seeding database...")
    db = SessionLocal()
    try:
        # Import seed from app.db package
        from app.db.seed import seed_database
        
        seed_database(db)
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"⚠️  Seed error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()