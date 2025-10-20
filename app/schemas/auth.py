from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """Registration request"""
    name: str
    email: EmailStr
    phone: str
    password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data stored in token"""
    email: Optional[str] = None
    customer_id: Optional[int] = None