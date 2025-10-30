from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api import auth
from app.api.customers import router as customers_router
# from app.api.admin import router as admin_router
from app.api.customers.messages import router as messages_router 
from app.api.customers.notifications import router as notifications_router

app = FastAPI(
    title="Repair Shop API",
    description="API for managing device repairs with customer and admin portals",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Admin panel local
        "http://localhost:3001",  # Customer portal local
        "https://repair-shop-admin.vercel.app",  # Admin panel production
        "https://repair-shop-customer-f4rqymn69-bavarianfanboys-projects.vercel.app",  # Customer portal production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all models so SQLAlchemy registers them
from app.models import customer, device, work_order, notification, message  # ADD THIS LINE


# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(customers_router, prefix="/api/customers", tags=["Customers"])
# app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(messages_router, prefix="/api/customers", tags=["Messages"])


# Health check endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Repair Shop API is running"
    }

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Repair Shop API",
        "docs": "/docs",
        "health": "/api/health"
    }