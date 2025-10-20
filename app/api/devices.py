from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.device import Device
from app.models.customer import Customer, UserRole
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.deps import get_current_user, get_admin_user

router = APIRouter()


@router.post("/", response_model=DeviceResponse, status_code=201)
def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Create a new device"""
    # Customers can only create devices for themselves
    if current_user.role == UserRole.CUSTOMER and device.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create devices for yourself"
        )
    
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.get("/", response_model=List[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Get devices (filtered by role)"""
    # Admins and technicians see all devices
    if current_user.role in [UserRole.ADMIN, UserRole.TECHNICIAN]:
        devices = db.query(Device).all()
    else:
        # Customers only see their own devices
        devices = db.query(Device).filter(Device.customer_id == current_user.id).all()
    
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Get a specific device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check authorization
    if current_user.role == UserRole.CUSTOMER and device.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this device"
        )
    
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)  # ← Authenticated
):
    """Update a device"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check authorization
    if current_user.role == UserRole.CUSTOMER and db_device.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this device"
        )
    
    for key, value in device.model_dump().items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device


@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_admin_user)  # ← Admin only
):
    """Delete a device (Admin only)"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}