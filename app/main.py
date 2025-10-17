from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers, devices, work_orders

app = FastAPI(title="Repair Shop API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - THIS IS CRITICAL
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(work_orders.router, prefix="/work-orders", tags=["work-orders"])

@app.get("/")
def root():
    return {"message": "Repair Shop API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}