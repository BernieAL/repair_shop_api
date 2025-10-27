from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.device import Device
from app.models.customer import Customer
from app.schemas.device import DeviceCreate, DeviceResponse
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[DeviceResponse])
def get_my_devices(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Get all devices for the currently logged-in customer.
    User ID is extracted from JWT token automatically.
    """
    devices = db.query(Device).filter(
        Device.customer_id == current_user.id
    ).all()
    return devices


@router.post("/", response_model=DeviceResponse, status_code=201)
def create_my_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """
    Create a new device for the currently logged-in customer.
    Customer ID is automatically set from JWT token.
    """
    # Override customer_id with current user's ID (security!)
    device_data = device.model_dump()
    device_data['customer_id'] = current_user.id
    
    db_device = Device(**device_data)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.get("/{device_id}", response_model=DeviceResponse)
def get_my_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Get a specific device (must belong to current user)"""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.customer_id == current_user.id  # Security check
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission to view it"
        )
    
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_my_device(
    device_id: int,
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Update a device (must belong to current user)"""
    db_device = db.query(Device).filter(
        Device.id == device_id,
        Device.customer_id == current_user.id  # Security check
    ).first()
    
    if not db_device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission to update it"
        )
    
    # Update fields
    for key, value in device.model_dump().items():
        if key != 'customer_id':  # Don't allow changing owner
            setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device


@router.delete("/{device_id}")
def delete_my_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user)
):
    """Delete a device (must belong to current user)"""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.customer_id == current_user.id  # Security check
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission to delete it"
        )
    
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}