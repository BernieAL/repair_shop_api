# app/api/customers/__init__.py
from fastapi import APIRouter
from .devices import router as devices_router
from .work_orders import router as work_orders_router
from .profile import router as profile_router

router = APIRouter()
router.include_router(devices_router, prefix="/devices", tags=["Customer Devices"])
router.include_router(work_orders_router, prefix="/work-orders", tags=["Customer Work Orders"])
router.include_router(profile_router, prefix="/profile", tags=["Customer Profile"])