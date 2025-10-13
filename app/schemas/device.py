from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    device_type: str
    brand: str
    model: str
    serial_number: str
    notes: Optional[str] = None

class DeviceCreate(DeviceBase):
    customer_id: int  # Need to link to a customer

class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    notes: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    customer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True