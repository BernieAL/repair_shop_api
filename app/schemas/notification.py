from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    work_order_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    customer_id: int

class NotificationResponse(NotificationBase):
    id: int
    customer_id: int
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True