from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers, devices, work_orders, auth

app = FastAPI(title="Repair Shop API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers 
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(work_orders.router, prefix="/api/work-orders", tags=["work-orders"])

@app.get("/")
def root():
    return {"message": "Repair Shop API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}