from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    device_type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None


class DeviceCreate(DeviceBase):
    owner_id: int  


class DeviceUpdate(BaseModel):
    device_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: int
    owner_id: int  
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)