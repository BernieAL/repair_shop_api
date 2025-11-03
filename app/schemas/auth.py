from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class UserResponse(BaseModel):
    """User data returned in responses"""
    id: int
    name: str
    email: str
    phone: str
    role: str
    
    class Config:
        from_attributes = True  

class Token(BaseModel):
    """Token response with user data"""
    access_token: str
    token_type: str
    user: UserResponse  