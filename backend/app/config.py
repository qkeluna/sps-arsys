"""
Application configuration settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email
    resend_api_key: str
    from_email: str
    support_email: str
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Better Auth
    better_auth_secret: str
    better_auth_url: str = "http://localhost:8000"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    debug: bool = True
    environment: str = "development"
    app_name: str = "SPS Appointment System"
    app_version: str = "1.0.0"
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @validator("secret_key", pre=True)  
    def validate_secret_key(cls, v):
        if not v or v == "your-super-secret-key-here-change-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set and changed in production")
        return v
        
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 