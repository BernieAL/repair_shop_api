from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.customer import Customer, UserRole
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse])
def get_all_customers(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Get all customers (Admin only). Optionally filter by role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can access all customers"
        )
    
    query = db.query(Customer)
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(Customer.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be: customer, technician, or admin"
            )
    
    customers = query.all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Get a specific customer (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can view other customers"
        )
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Create a new customer (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create customers"
        )
    
    # Check if email already exists
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Update a customer (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update customers"
        )
    
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer_update.model_dump(exclude_unset=True).items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Delete a customer (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete customers"
        )
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Prevent deleting yourself
    if customer.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}