from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user_role import UserRole

# Base - common fields (NO role here)
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None

# Public registration - CANNOT set role
class UserCreate(UserBase):
    password: str
    # No role field = always creates USER

# Admin creating users - CAN set role
class UserCreateAdmin(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER  # Changed from CUSTOMER

# Users updating themselves - limited fields
class UserUpdateSelf(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    # Cannot change email or role

# Admin updating users - CAN change everything
class UserUpdateAdmin(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    notes: Optional[str] = None
    password: Optional[str] = None

# Response - what gets returned (NO password)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str