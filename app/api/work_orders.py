from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.work_order import WorkOrder
from app.models.device import Device
from app.schemas.work_order import WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse

router = APIRouter(
    prefix="/work-orders",
    tags=["work-orders"]
)

@router.post("", response_model=WorkOrderResponse, status_code=201)
async def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db)
):
    # Verify device exists
    device = db.query(Device).filter(Device.id == work_order.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db_work_order = WorkOrder(**work_order.dict())
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    
    return db_work_order

@router.get("", response_model=List[WorkOrderResponse])
async def get_work_orders(
    skip: int = 0,
    limit: int = 100,
    device_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(WorkOrder)
    
    if device_id:
        query = query.filter(WorkOrder.device_id == device_id)
    
    if status:
        query = query.filter(WorkOrder.status == status)
    
    work_orders = query.offset(skip).limit(limit).all()
    return work_orders

@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return work_order

@router.put("/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: int,
    work_order_update: WorkOrderUpdate,
    db: Session = Depends(get_db)
):
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    update_data = work_order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work_order, field, value)
    
    db.commit()
    db.refresh(work_order)
    return work_order

@router.delete("/{work_order_id}", status_code=204)
async def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db)
):
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    db.delete(work_order)
    db.commit()
    return None