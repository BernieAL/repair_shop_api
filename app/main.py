from fastapi import FastAPI
from app.db.base_class import Base
from app.db.session import engine
from app.models import *

# Import the routers - try this syntax
from app.api.customers import router as customers_router
from app.api.devices import router as devices_router
from app.api.work_orders import router as work_orders_router
from app.api import customers, devices, work_orders, auth  # Add auth
from fastapi.middleware.cors import CORSMiddleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Repair Shop API",
    description="Work order and customer management system",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://repair-shop-admin.vercel.app",
        "https://repair-shop-customer-f4rqymn69-bavarianfanboys-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])  # Add this
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(work_orders.router, prefix="/work-orders", tags=["work-orders"])


@app.get("/")
async def root():
    return {"message": "Repair Shop API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}