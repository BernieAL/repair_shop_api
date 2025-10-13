from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.device import Device
from app.models.customer import Customer
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

@router.post("", response_model=DeviceResponse, status_code=201)
async def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db)
):
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == device.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if serial number already exists
    existing = db.query(Device).filter(Device.serial_number == device.serial_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Serial number already registered")
    
    db_device = Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device

@router.get("", response_model=List[DeviceResponse])
async def get_devices(
    skip: int = 0,
    limit: int = 100,
    customer_id: int = None,  # Optional filter by customer
    db: Session = Depends(get_db)
):
    query = db.query(Device)
    
    if customer_id:
        query = query.filter(Device.customer_id == customer_id)
    
    devices = query.offset(skip).limit(limit).all()
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check serial number uniqueness if being updated
    if device_update.serial_number and device_update.serial_number != device.serial_number:
        existing = db.query(Device).filter(Device.serial_number == device_update.serial_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="Serial number already registered")
    
    update_data = device_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    return None