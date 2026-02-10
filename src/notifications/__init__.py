"""
FILE: src/notifications/__init__.py
Notification module initialization - Enhanced with Broadcast Support
"""
from src.notifications.router import router
from src.notifications.service import NotificationService, BroadcastService
from src.notifications.types import (
    NotificationType, 
    NotificationPriority,
    BroadcastRecipientType
)
from src.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    BroadcastCreate,
    BroadcastResponse
)

__all__ = [
    "router",
    "NotificationService",
    "BroadcastService",
    "NotificationType",
    "NotificationPriority",
    "BroadcastRecipientType",
    "NotificationCreate",
    "NotificationResponse",
    "BroadcastCreate",
    "BroadcastResponse"
]