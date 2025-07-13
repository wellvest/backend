import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Base settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "WellVest API"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://backend-asn8.onrender.com", "http://localhost:8080"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/wellvest")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-jwt-please-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Security settings
    SECURITY_PASSWORD_SALT: str = os.getenv("SECURITY_PASSWORD_SALT", "your-salt-for-password-please-change-in-production")
    
    # Admin settings
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-admin-please-change-in-production")
    
    # SMS Mode API settings
    SMSMODE_API_KEY: str = os.getenv("SMSMODE_API_KEY", "AGgWEYjm7v8JHmqG1tp5aqeWZ7ofGVcz")

    class Config:
        case_sensitive = True

settings = Settings()
