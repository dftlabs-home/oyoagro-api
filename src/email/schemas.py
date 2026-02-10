"""
FILE: src/email/schemas.py
Email data schemas for type safety
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class WelcomeEmailData(BaseModel):
    """Data for welcome email to new officers"""
    email: EmailStr
    firstname: str
    lastname: str
    username: str
    temp_password: str
    lga_name: Optional[str] = None


class PasswordResetEmailData(BaseModel):
    """Data for password reset email"""
    email: EmailStr
    username: str
    firstname: str
    reset_token: str
    expires_at: datetime


class PasswordChangedEmailData(BaseModel):
    """Data for password changed notification"""
    email: EmailStr
    username: str
    firstname: str
    changed_at: datetime


class AccountLockedEmailData(BaseModel):
    """Data for account locked notification"""
    email: EmailStr
    username: str
    firstname: str
    locked_at: datetime
    reason: str = "Multiple failed login attempts"


class EmailResponse(BaseModel):
    """Standard email service response"""
    success: bool
    message: str
    email_sent_to: Optional[EmailStr] = None
    error: Optional[str] = None