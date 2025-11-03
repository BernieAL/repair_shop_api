# app/api/admin/__init__.py
from fastapi import APIRouter
from .devices import router as devices_router
from .work_orders import router as work_orders_router
from .users import router as users
from app.api.admin import work_orders, devices, users  

router = APIRouter()

router.include_router(
    work_orders.router,
    prefix="/work-orders",
    tags=["admin-work-orders"]
)

router.include_router(
    devices.router,
    prefix="/devices",
    tags=["admin-devices"]
)

router.include_router(
    users.router,  
    prefix="/users",  
    tags=["admin-users"]  
)