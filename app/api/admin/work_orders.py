from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.work_order import WorkOrder
from app.models.device import Device
from app.models.customer import Customer, UserRole
from app.schemas.work_order import WorkOrderCreate, WorkOrderResponse, WorkOrderUpdate
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[WorkOrderResponse])
def get_all_work_orders(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Get all work orders (Admin/Tech only).
    Optionally filter by customer_id or status.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can access this endpoint"
        )
    
    query = db.query(WorkOrder)
    
    # Optional filters
    if customer_id:
        query = query.join(Device).filter(Device.customer_id == customer_id)
    
    if status:
        query = query.filter(WorkOrder.status == status)
    
    work_orders = query.all()
    return work_orders


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Get any work order by ID (Admin/Tech only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can access this endpoint"
        )
    
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return work_order


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Create a work order for any device (Admin/Tech only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can create work orders for any device"
        )
    
    # Verify device exists
    device = db.query(Device).filter(Device.id == work_order.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db_work_order = WorkOrder(**work_order.model_dump())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.put("/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: int,
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Update any work order (Admin/Tech only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can update work orders"
        )
    
    db_work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    for key, value in work_order.model_dump().items():
        setattr(db_work_order, key, value)
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.patch("/{work_order_id}/status")
def update_work_order_status(
    work_order_id: int,
    status: str,
    technician_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Update work order status (Admin/Tech only).
    Allows partial update of just status and notes.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can update work order status"
        )
    
    db_work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'waiting_for_parts', 'completed', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    db_work_order.status = status
    if technician_notes:
        db_work_order.technician_notes = technician_notes
    
    # Set completed_at if status is completed
    if status == 'completed' and not db_work_order.completed_at:
        from datetime import datetime
        db_work_order.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_work_order)
    return db_work_order


@router.delete("/{work_order_id}")
def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Delete any work order (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete work orders"
        )
    
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    db.delete(work_order)
    db.commit()
    return {"message": "Work order deleted successfully"}