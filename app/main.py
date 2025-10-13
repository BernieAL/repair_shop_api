from fastapi import FastAPI
from app.db.base_class import Base
from app.db.session import engine
from app.models import *

# Import the routers - try this syntax
from app.api.customers import router as customers_router
from app.api.devices import router as devices_router
from app.api.work_orders import router as work_orders_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Repair Shop API",
    description="Work order and customer management system",
    version="0.1.0"
)

# Include all routers
app.include_router(customers_router)
app.include_router(devices_router)
app.include_router(work_orders_router)

@app.get("/")
async def root():
    return {"message": "Repair Shop API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}