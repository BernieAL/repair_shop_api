from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user import UserCreateAdmin, UserResponse, UserUpdateAdmin
from app.core.permissions import require_admin, require_technician
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician)
):
    """Get all users (Technician or Admin). Optionally filter by role."""
    query = db.query(User)
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be: user, technician, or admin"
            )
    
    users = query.all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician)
):
    """Get a specific user (Technician or Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (Admin only)"""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash the password
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=get_password_hash(user.password),
        role=user.role,
        notes=user.notes
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user (Admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle password separately (needs hashing)
    if 'password' in update_data:
        password = update_data.pop('password')
        if password:
            db_user.password_hash = get_password_hash(password)
    
    # Update other fields
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a user (Admin only).
    This removes the user account entirely from the system.
    Use this to remove terminated technicians or close customer accounts.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    # Optional: Add warning if user has active work orders
    from app.models.work_order import WorkOrder, WorkOrderStatus
    active_orders = db.query(WorkOrder).filter(
        WorkOrder.customer_id == user_id,
        WorkOrder.status.in_([
            WorkOrderStatus.PENDING,
            WorkOrderStatus.DIAGNOSED,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.IN_PROGRESS
        ])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete user with {active_orders} active work order(s). Complete or cancel them first."
        )
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}


# Technician management endpoints

@router.get("/technicians/list", response_model=List[UserResponse])
def list_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all technicians (Admin only)"""
    technicians = db.query(User).filter(
        User.role == UserRole.TECHNICIAN
    ).all()
    return technicians


@router.post("/technicians/promote/{user_id}")
def promote_to_technician(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Promote a regular user to technician role (Admin only).
    Use this to give an existing user access to technician features.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="Cannot change admin role"
        )
    
    if user.role == UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=400,
            detail="User is already a technician"
        )
    
    user.role = UserRole.TECHNICIAN
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"{user.name} promoted to technician",
        "user": UserResponse.model_validate(user)
    }


@router.post("/technicians/create", response_model=UserResponse, status_code=201)
def create_technician(
    user: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new technician account (Admin only).
    Convenience endpoint that automatically sets role to TECHNICIAN.
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Force technician role
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password_hash=get_password_hash(user.password),
        role=UserRole.TECHNICIAN,  # Force technician
        notes=user.notes
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/technicians/{technician_id}")
def remove_technician(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Remove a technician from the system (Admin only).
    This is the same as deleting the user - removes the account entirely.
    Use this when a technician is terminated or leaves the company.
    """
    user = db.query(User).filter(User.id == technician_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Technician not found")
    
    if user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=400,
            detail="User is not a technician"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    # Check for assigned work orders
    from app.models.work_order import WorkOrder
    assigned_orders = db.query(WorkOrder).filter(
        WorkOrder.assigned_technician == user.name
    ).count()
    
    if assigned_orders > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot remove technician with {assigned_orders} assigned work order(s). Reassign them first."
        )
    
    db.delete(user)
    db.commit()
    return {"message": f"Technician {user.name} removed successfully"}