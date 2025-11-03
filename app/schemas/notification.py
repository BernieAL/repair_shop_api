from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    user_id: int  # Changed from customer_id
    work_order_id: int
    type: NotificationType
    title: str
    message: str
    read: bool = False


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None


class NotificationResponse(NotificationBase):  # Changed from Notification
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)