from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base_class import Base

class NotificationType(str, Enum):
    MESSAGE = "message"
    STATUS_CHANGE = "status_change"
    TECH_NOTE = "tech_note"
    COMPLETED = "completed"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")  
    work_order = relationship("WorkOrder", back_populates="notifications")