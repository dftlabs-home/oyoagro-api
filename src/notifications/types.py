"""
FILE: src/notifications/types.py
Notification type enums and constants - Enhanced with Admin Broadcasts
"""
from enum import Enum


class NotificationType(str, Enum):
    """Notification type categories"""
    SYSTEM = "system"
    USER_ACTIVITY = "user_activity"
    ADMIN_ACTION = "admin_action"
    ADMIN_BROADCAST = "admin_broadcast"  # NEW: Admin broadcast messages
    DATA_CHANGE = "data_change"
    ALERT = "alert"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BroadcastRecipientType(str, Enum):
    """Broadcast recipient categories"""
    ALL = "all"                    # All extension officers
    BY_LGA = "by_lga"             # Officers in specific LGAs
    BY_REGION = "by_region"       # Officers in specific regions
    BY_ROLE = "by_role"           # Officers with specific role


# Notification icons mapping (for frontend)
NOTIFICATION_ICONS = {
    NotificationType.SYSTEM: "system_update",
    NotificationType.USER_ACTIVITY: "person",
    NotificationType.ADMIN_ACTION: "admin_panel_settings",
    NotificationType.ADMIN_BROADCAST: "campaign",  # NEW
    NotificationType.DATA_CHANGE: "folder",
    NotificationType.ALERT: "warning",
}

# Notification colors mapping (for frontend)
NOTIFICATION_COLORS = {
    NotificationPriority.LOW: "#4CAF50",      # Green
    NotificationPriority.MEDIUM: "#2196F3",   # Blue
    NotificationPriority.HIGH: "#FF9800",     # Orange
    NotificationPriority.URGENT: "#F44336",   # Red
}