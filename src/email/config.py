"""
FILE: src/email/config.py
Email service configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class EmailSettings(BaseSettings):
    """Email service configuration settings"""
    
    # SMTP Configuration
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "noreply@oyoagro.gov.ng")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Oyo Agro System")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "True").lower() == "true"
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS", "True").lower() == "true"
    
    # Email Features
    SEND_EMAILS: bool = os.getenv("SEND_EMAILS", "False").lower() == "false"
    EMAIL_TEMPLATES_DIR: str = os.getenv("EMAIL_TEMPLATES_DIR", "src/email/templates")
    
    # Frontend URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    PASSWORD_RESET_URL: str = os.getenv(
        "PASSWORD_RESET_URL", 
        f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password"
    )
    LOGIN_URL: str = os.getenv(
        "LOGIN_URL",
        f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/login"
    )
    
    # Token Expiration
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "24")
    )
    
    class Config:
        case_sensitive = True
        env_file = ".env"


email_settings = EmailSettings()