from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import customers, devices, work_orders, auth

app = FastAPI(title="Repair Shop API")

# CORS - Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://repair-shop-admin.vercel.app",
        "https://repair-shop-customer-f4rqymn69-bavarianfanboys-projects.vercel.app",
        "https://*.vercel.app",
    ],
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