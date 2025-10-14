from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Use environment variable or default to SQLite
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./repair_shop.db"
    )
    SECRET_KEY: str = "your-secret-key-change-this"
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()