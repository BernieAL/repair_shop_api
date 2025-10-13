DB

    sqlalchemy lets us write python classes, and then 
    converts them to SQL

    BASE CLASS defined
        base is factory function that creates special parent
        class

        any class that inhertis from Base - becomes a SQLalchemy mode

        its like a registry that tracks all the defined models

        Base.metadata.create_all(bind=engine)
        this line tels Base to look at all the classes that 
        inherited from it and create tables for them in the DB

        w/o base - SQLAlchemy wouldnt know which classes are DB models vs regular python classes

-----------------------------------

DB class definition - breakdown

    class Customer(Base):
        __tablename__ = "customers"
        
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, nullable=False)
        email = Column(String, unique=True, index=True)
        phone = Column(String)
        notes = Column(String, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        devices = relationship("Device", back_populates="customer")


        breakdown:
            __tablename__ = "customers" → Names the actual table in the database
            Column(Integer, primary_key=True) → Defines a column, its type, and constraints
            index=True → Creates a database index for faster lookups (important for emails you'll search often)
            nullable=False → This field is required (NOT NULL in SQL)
            default=datetime.utcnow → Auto-fills timestamp when created
            relationship("Device", ...) → This is NOT a database column! It's a Python convenience for accessing related data

    Relationship explained:
        devices = relationship("Device", back_populates="customer")

        this lets you write python code like:
            customer = db.query(Customer).first()
            print(customer.devices)  # Gets all devices for this customer   

        w/o the devices line - we would have to manually query
            ex. devices = db.query(Device).filter(Device.customer_id == customer.id).all()


        back_populates="customer" -- creates a two-way link.
        we can go customer -> devices or vice-versa
-----------------------------------
DB SESSION Explained


    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


    breakdown:
        engine - actual connectin to the DB (like opening a file handle)
        
        SessionLocal - factory that creates db sessions (like transactions)

        get_db() - dependency function that FastAPI will use

        try/finally:
            opens db connection
            lets you do the work
            always closes the connection even if theres an error
            and prevents connection leaks (running of db connections)

    questions:
        whats a factory?



------------------------------------

ENUM usage for Status


    removes having to hardcode statuses each time we need them
    we specify them in a single place - properly spelled, typesafe, definitively defined
    - meaning we cant insert any other statuses that arent define here

    Ex. usage

    order.status = WorkOrderStatus.PENDING  # ✅ Valid
    order.status = "pendign"  # ❌ Error!


------------------------------------


DB config

    class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./repair_shop.db"
    SECRET_KEY: str = "your-secret-key-change-this"
    
    class Config:
        env_file = ".env"

    settings = Settings()


    breakdown:
        this reads from .env file
        provides defaults if .env doesnt have a value
        type checking -> database_url must be a string


---------------------------

CREATING TABLES:


    Base.metadata.create_all(bind=engine)

    Base.metadata -> contains info about all the models that inherited from Base
    .create_all() looks at registered models and runs CREATE TABLE

    bind=engine - tells which db to create tables in


    Checks if tables exist
    If not, creates them with proper columns, types, foreign keys
    If they do exist, does nothing


--------------------------

Full FLOW when app is started

    import models -> classes inherit from Base, SQLAlchemy registers them

    create engine -> connects to a db

    Base.metadata.create_all() -> creates tables for all registered models

    FastAPI starts -> ready to handle requests


    Base = The contract that says "I'm a database table"
    Models = The blueprint for each table
    Engine = The actual database connection
    Session = A conversation with the database
    Config = The settings for different environments