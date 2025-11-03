from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.work_order import WorkOrder
from app.models.device import Device
from app.models.user import User
from app.schemas.work_order import WorkOrderCreate, WorkOrderResponse
from app.core.deps import get_current_user


router = APIRouter()


@router.get("/", response_model=List[WorkOrderResponse])
def get_my_work_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all work orders for the currently logged-in customer.
    Returns only work orders for devices owned by this customer.
    """
    work_orders = db.query(WorkOrder).join(Device).filter(
        Device.customer_id == current_user.id
    ).all()
    
    return work_orders


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_my_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new work order for one of the customer's devices.
    Device ownership is verified automatically.
    """
    # Verify device exists
    device = db.query(Device).filter(Device.id == work_order.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Verify device belongs to current user (security check)
    if device.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create work orders for your own devices"
        )
    
    db_work_order = WorkOrder(**work_order.model_dump())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_my_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific work order (must belong to current user's devices)"""
    work_order = db.query(WorkOrder).join(Device).filter(
        WorkOrder.id == work_order_id,
        Device.customer_id == current_user.id
    ).first()
    
    if not work_order:
        raise HTTPException(
            status_code=404,
            detail="Work order not found or you don't have permission to view it"
        )
    
    return work_order


@router.delete("/{work_order_id}")
def cancel_my_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a work order (only if status is 'pending').
    Customer can only cancel their own work orders.
    """
    work_order = db.query(WorkOrder).join(Device).filter(
        WorkOrder.id == work_order_id,
        Device.customer_id == current_user.id
    ).first()
    
    if not work_order:
        raise HTTPException(
            status_code=404,
            detail="Work order not found or you don't have permission"
        )
    
    # Only allow cancellation if work hasn't started
    if work_order.status not in ['pending']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel work order with status '{work_order.status}'. Please contact support."
        )
    
    work_order.status = 'cancelled'
    db.commit()
    return {"message": "Work order cancelled successfully"}