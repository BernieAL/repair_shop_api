from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse, CustomerUpdate
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=CustomerResponse)
def get_my_profile(
    current_user: Customer = Depends(get_current_user)
):
    """Get current user's profile (from JWT token)"""
    return current_user


@router.put("/me", response_model=CustomerResponse)
def update_my_profile(
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Update current user's profile"""
    # Update only provided fields
    for key, value in customer_update.model_dump(exclude_unset=True).items():
        if key not in ['id', 'role', 'created_at']:  # Don't allow changing these
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Delete current user's account.
    This will also delete all associated devices and work orders (cascade).
    """
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}