from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./repair_shop.db"  # Default to SQLite for now
    SECRET_KEY: str = "your-secret-key-change-this"
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()