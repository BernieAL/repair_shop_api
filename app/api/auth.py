from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.auth import UserLogin, UserRegister, Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=Token, status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new customer"""
    # Check if email already exists
    existing_user = db.query(Customer).filter(Customer.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new customer
    hashed_password = get_password_hash(user.password)
    new_customer = Customer(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        role="customer"
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Create access token with role
    access_token = create_access_token(
        data={
            "sub": new_customer.email,
            "customer_id": new_customer.id,
            "role": new_customer.role.value
        }
    )
    
    # ✅ CHANGED: Add user object to response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": { 
            "id": new_customer.id,
            "name": new_customer.name,
            "email": new_customer.email,
            "phone": new_customer.phone,
            "role": new_customer.role.value
        }
    }

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user by email
    customer = db.query(Customer).filter(Customer.email == credentials.email).first()
    
    # Verify user exists and password is correct
    if not customer or not verify_password(credentials.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with role
    access_token = create_access_token(
        data={
            "sub": customer.email,
            "customer_id": customer.id,
            "role": customer.role.value
        }
    )
    
    # ✅ CHANGED: Add user object to response (NOT just "user": user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {  
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "role": customer.role.value
        }
    }

@router.get("/me")
def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user info from token"""
    # Decode token
    token_data = decode_access_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    customer = db.query(Customer).filter(Customer.email == token_data.get("sub")).first()
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "role": customer.role.value
    }