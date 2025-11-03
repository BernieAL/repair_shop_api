from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import Customer, UserRole
from app.core.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Customer:
    """Get current authenticated user from JWT token"""
    
    # Decode token
    token_data = decode_access_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(Customer).filter(
        Customer.email == token_data.get("sub")
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(allowed_roles: List[UserRole]):
    """Dependency to check if user has required role"""
    def role_checker(current_user: Customer = Depends(get_current_user)) -> Customer:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker


# Convenience dependencies for specific roles
def get_admin_user(current_user: Customer = Depends(require_role([UserRole.ADMIN]))) -> Customer:
    """Require admin role"""
    return current_user


def get_technician_user(current_user: Customer = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))) -> Customer:
    """Require technician or admin role"""
    return current_user


def get_customer_user(current_user: Customer = Depends(require_role([UserRole.CUSTOMER, UserRole.ADMIN]))) -> Customer:
    """Require customer or admin role"""
    return current_user