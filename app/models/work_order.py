from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base_class import Base

class WorkOrderStatus(str, Enum):
    PENDING = "pending"
    DIAGNOSED = "diagnosed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING)
    cost = Column(Float, nullable=True)
    technician_notes = Column(String, nullable=True)
    assigned_technician = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
   # Relationships
    customer = relationship("Customer", back_populates="work_orders")  
    device = relationship("Device", back_populates="work_orders")
    messages = relationship(
        "Message",
        back_populates="work_order",
        cascade="all, delete-orphan",
        lazy="select"
    )

    customer = relationship("User", back_populates="work_orders") 
    device = relationship("Device", back_populates="work_orders")
    messages = relationship("Message",
        back_populates="work_order",
        cascade="all, delete-orphan",
        lazy="select"
    )
    notifications = relationship("Notification", back_populates="work_order", cascade="all, delete-orphan")

