from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base_class import Base

class WorkOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_PARTS = "waiting_parts"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)  # ADD THIS
    device_id = Column(Integer, ForeignKey("devices.id"))
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING)
    cost = Column(Numeric(10, 2), nullable=True)
    technician_notes = Column(String, nullable=True)
    assigned_technician = Column(String, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
   # Relationships
    customer = relationship("Customer", back_populates="work_orders")  # ADD THIS
    device = relationship("Device", back_populates="work_orders")
    messages = relationship(
        "Message",
        back_populates="work_order",
        cascade="all, delete-orphan",
        lazy="select"
    )


