from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base


class NotificationType(str, enum.Enum):
    """Type of notification"""
    STATUS_CHANGE = "status_change"
    TECH_NOTE = "tech_note"
    COMPLETED = "completed"
    MESSAGE = "message"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)
    type = Column(Enum(NotificationType))  # Use the enum
    title = Column(String)
    message = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="notifications")
    work_order = relationship("WorkOrder")