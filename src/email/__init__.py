"""
FILE: src/email/__init__.py
Email module initialization
"""
from src.email.service import EmailService
from src.email.schemas import (
    WelcomeEmailData,
    PasswordResetEmailData,
    PasswordChangedEmailData,
    AccountLockedEmailData,
    EmailResponse
)

__all__ = [
    "EmailService",
    "WelcomeEmailData",
    "PasswordResetEmailData",
    "PasswordChangedEmailData",
    "AccountLockedEmailData",
    "EmailResponse"
]