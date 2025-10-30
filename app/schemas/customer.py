from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.customer import UserRole

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    password: str
    role: UserRole = UserRole.CUSTOMER

class CustomerUpdate(BaseModel):
    """For partial updates - all fields optional"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


