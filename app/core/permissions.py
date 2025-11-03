from fastapi import Depends, HTTPException, status
from app.models.user import User  
from app.models.user_role import UserRole
from app.core.security import get_current_user


def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires the user to be an admin.
    Use this for admin-only endpoints.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_technician(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires the user to be a technician OR admin.
    Use this for endpoints that both admins and technicians can access.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technician or admin access required"
        )
    return current_user


def require_staff(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Alias for require_technician (staff = admin or technician).
    """
    return require_technician(current_user)


def is_admin(user: User) -> bool:
    """Helper function to check if a user is an admin"""
    return user.role == UserRole.ADMIN


def is_technician_or_admin(user: User) -> bool:
    """Helper function to check if a user is a technician or admin"""
    return user.role in [UserRole.ADMIN, UserRole.TECHNICIAN]