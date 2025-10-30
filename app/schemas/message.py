"""
Pydantic schemas for Message endpoints
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class SenderType(str, Enum):
    """Type of message sender"""
    CUSTOMER = "customer"
    TECHNICIAN = "technician"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """Base message schema"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    pass


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    work_order_id: int
    sender_id: int
    sender_type: SenderType
    message: str
    is_read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Additional fields for display
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None

    class Config:
        from_attributes = True


class MessageThread(BaseModel):
    """Schema for a complete message thread"""
    work_order_id: int
    total_messages: int
    unread_count: int
    messages: list[MessageResponse]


class MessageMarkRead(BaseModel):
    """Schema for marking message as read"""
    message_ids: list[int] = Field(..., description="List of message IDs to mark as read")