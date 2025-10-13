from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.work_order import WorkOrderStatus

class WorkOrderBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    technician_notes: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class WorkOrderCreate(WorkOrderBase):
    device_id: int

class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkOrderStatus] = None
    technician_notes: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class WorkOrderResponse(WorkOrderBase):
    id: int
    device_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
