from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.db.base_class import Base
from app.models.user_role import UserRole




class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    password_hash = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER) 
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    devices = relationship("Device", back_populates="owner")
    work_orders = relationship("WorkOrder", back_populates="customer")
    notifications = relationship("Notification", back_populates="user")