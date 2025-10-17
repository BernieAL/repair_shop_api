from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String, nullable=True)  # Add this line
    # Relationships
    devices = relationship("Device", back_populates="customer")