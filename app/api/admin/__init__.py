# app/api/admin/__init__.py
from fastapi import APIRouter
from .devices import router as devices_router
from .work_orders import router as work_orders_router
from .customers import router as customers_router

router = APIRouter()
router.include_router(devices_router, prefix="/devices", tags=["Admin Devices"])
router.include_router(work_orders_router, prefix="/work-orders", tags=["Admin Work Orders"])
router.include_router(customers_router, prefix="/customers", tags=["Admin Customers"])
