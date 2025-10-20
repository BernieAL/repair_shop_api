from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.work_order import WorkOrder
from app.models.device import Device
from app.models.customer import Customer, UserRole
from app.schemas.work_order import WorkOrderCreate, WorkOrderResponse
from app.core.deps import get_current_user, get_technician_user

router = APIRouter()


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Create a new work order"""
    # Verify device exists and user has access
    device = db.query(Device).filter(Device.id == work_order.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Customers can only create work orders for their own devices
    if current_user.role == UserRole.CUSTOMER and device.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create work orders for your own devices"
        )
    
    db_work_order = WorkOrder(**work_order.model_dump())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.get("/", response_model=List[WorkOrderResponse])
def get_work_orders(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Get work orders (filtered by role)"""
    # Admins and technicians see all work orders
    if current_user.role in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        work_orders = db.query(WorkOrder).all()
    else:
        # Customers only see work orders for their devices
        work_orders = db.query(WorkOrder).join(Device).filter(
            Device.customer_id == current_user.id
        ).all()
    
    return work_orders


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Get a specific work order"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Check authorization for customers
    if current_user.role == UserRole.CUSTOMER:
        device = db.query(Device).filter(Device.id == work_order.device_id).first()
        if device.customer_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this work order"
            )
    
    return work_order


@router.put("/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: int,
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_technician_user)  # ← Technician/Admin only
):
    """Update a work order (Technician/Admin only)"""
    db_work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    for key, value in work_order.model_dump().items():
        setattr(db_work_order, key, value)
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.delete("/{work_order_id}")
def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_technician_user)  # ← Technician/Admin only
):
    """Delete a work order (Technician/Admin only)"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    db.delete(work_order)
    db.commit()
    return {"message": "Work order deleted successfully"}