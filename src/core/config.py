"""
FILE: src/core/config.py
Core configuration module for OyoAgro API
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
import psycopg2


def get_dburl():
    db_user = os.getenv("DB_USER", "postgres") 
    db_password = os.getenv("DB_PASSWORD", "P@ssword@123") 
    host = os.getenv("DB_PASSWORD", "localhost") 
    port = os.getenv("DB_PORT", "5432") 
    db_name = os.getenv("DB_NAME", "oyoagrodb") 
    return f"postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "OyoAgro API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_BASE_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = get_dburl() # P%40ssword%40123
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = True
    
    # JWT
    JWT_SECRET_KEY: str = "IqwK9N7EuBOE7PxbOcWsH1jycwdJIqfemtadEtu6Tp8"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_ISSUER: str = "oyoagro-api"
    JWT_AUDIENCE: str = "oyoagro-frontend"
    
    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "oluwafemip.adejumobi@gmail.com"
    SMTP_PASSWORD: str = "scfn hbku ifvt vdka"
    SMTP_FROM_EMAIL: str = "noreply@oyoaims.com"
    SMTP_FROM_NAME: str = "Oyo Agro Platform"
    SMTP_USE_TLS: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Company
    COMPANY_NAME: str = "Oyo State Ministry of Agriculture and Rural Development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()  # type: ignore


# Global settings instance
settings = get_settings()
