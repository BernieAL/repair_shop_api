from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.device import Device
from app.models.customer import Customer, UserRole
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[DeviceResponse])
def get_all_devices(
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Get all devices (Admin/Tech only).
    Optionally filter by customer_id query parameter.
    """
    # Check if user is admin or technician
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can access this endpoint"
        )
    
    query = db.query(Device)
    
    # Optional filter by customer_id
    if customer_id:
        query = query.filter(Device.customer_id == customer_id)
    
    devices = query.all()
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Get any device by ID (Admin/Tech only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can access this endpoint"
        )
    
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device


@router.post("/", response_model=DeviceResponse, status_code=201)
def create_device_for_customer(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Create a device for any customer (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create devices for other customers"
        )
    
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Update any device (Admin/Tech only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and technicians can update devices"
        )
    
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    for key, value in device.model_dump().items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device


@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Delete any device (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete devices"
        )
    
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}