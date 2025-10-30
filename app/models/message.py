"""
Message model for repair shop communication threads
Each work order has its own message thread between customer and technician
"""


from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base



class SenderType(str, enum.Enum):
    """Type of message sender"""
    CUSTOMER = "customer"
    TECHNICIAN = "technician"
    SYSTEM = "system"


class Message(Base):
    """Message in a work order communication thread"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, nullable=False, index=True)  # customer_id or technician_id
    sender_type = Column(Enum(SenderType), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, work_order_id={self.work_order_id}, sender_type={self.sender_type})>"

    def to_dict(self):
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "work_order_id": self.work_order_id,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type.value,
            "message": self.message,
            "is_read": bool(self.is_read),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }