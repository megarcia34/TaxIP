"""
Application configuration management
Centralized settings from environment variables
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taxip_db"
    DEBUG: bool = False
    
    # JWT / Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: str = ""
    
    # Storage configuration
    STORAGE_TYPE: str = "local"  # local, s3, cloudinary
    STORAGE_PATH: str = "./uploads"
    
    # QR Configuration
    QR_SECRET_KEY: str = "taxip_qr_secret_2024"
    QR_EXPIRATION_MINUTES: int = 5
    
    # API Base URL (para generar QR)
    API_BASE_URL: str = "http://localhost:8000"
    
    # Route deviation
    DEVIATION_THRESHOLD_METERS: float = 100.0
    DEVIATION_CHECK_INTERVAL_SECONDS: int = 10
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Email (SMTP)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Singleton instance
settings = Settings()