from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_current_user  # Import from security


def require_role(allowed_roles: List[UserRole]):
    """Dependency to check if user has required role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    return role_checker


# Convenience dependencies for specific roles
def get_admin_user(current_user: User = Depends(require_role([UserRole.ADMIN]))) -> User:
    """Require admin role"""
    return current_user


def get_technician_user(current_user: User = Depends(require_role([UserRole.TECHNICIAN, UserRole.ADMIN]))) -> User:
    """Require technician or admin role"""
    return current_user


def get_user_customer(current_user: User = Depends(require_role([UserRole.USER, UserRole.ADMIN]))) -> User:
    """Require regular user or admin role (for customer-facing endpoints)"""
    return current_user