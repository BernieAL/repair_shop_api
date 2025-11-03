from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    device_type = Column(String)  # "Laptop", "Desktop", etc.
    brand = Column(String)
    model = Column(String)
    serial_number = Column(String, unique=True, index=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="devices")
    work_orders = relationship("WorkOrder", back_populates="device")