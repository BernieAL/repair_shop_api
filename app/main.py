from fastapi import FastAPI

app = FastAPI(
    title="Repair Shop API",
    description="Work order and customer management system",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Repair Shop API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}