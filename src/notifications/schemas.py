"""
FILE: src/notifications/schemas.py
Notification Pydantic schemas - FIXED for metadata field
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.notifications.types import (
    NotificationType, 
    NotificationPriority,
    BroadcastRecipientType
)


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    userid: int
    type: NotificationType
    priority: NotificationPriority
    title: str = Field(max_length=200)
    message: str
    link: Optional[str] = Field(default=None, max_length=500)
    notif_metadata: Optional[dict] = Field(default=None, alias="metadata")  # FIXED: Use notif_metadata with alias
    broadcastid: Optional[int] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    notificationid: int
    userid: int
    type: str
    priority: str
    title: str
    message: str
    link: Optional[str] = None
    isread: bool
    readat: Optional[datetime] = None
    metadata: Optional[dict] = Field(default=None, alias="notif_metadata")  # FIXED: Expose as metadata, read from notif_metadata
    broadcastid: Optional[int] = None
    createdat: datetime
    updatedat: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow population by alias


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list"""
    success: bool
    message: str
    data: List[NotificationResponse]
    tag: int = 1
    total: int
    unread_count: int
    page: int
    limit: int


class NotificationCountResponse(BaseModel):
    """Schema for unread notification count"""
    success: bool
    message: str
    data: dict
    tag: int = 1


class MarkAsReadRequest(BaseModel):
    """Schema for marking multiple notifications as read"""
    notification_ids: List[int]


# ============================================================================
# BROADCAST SCHEMAS
# ============================================================================

class BroadcastCreate(BaseModel):
    """Schema for creating a broadcast message"""
    title: str = Field(max_length=200, description="Broadcast message title")
    message: str = Field(description="Broadcast message content")
    priority: NotificationPriority = Field(description="Message priority level")
    link: Optional[str] = Field(default=None, max_length=500, description="Optional link")
    
    # Recipient targeting
    recipienttype: BroadcastRecipientType = Field(description="Recipient category")
    lga_ids: Optional[List[int]] = Field(default=None, description="LGA IDs if recipienttype is by_lga")
    region_ids: Optional[List[int]] = Field(default=None, description="Region IDs if recipienttype is by_region")
    role_ids: Optional[List[int]] = Field(default=None, description="Role IDs if recipienttype is by_role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Training Session Announcement",
                "message": "Mandatory training session on new data collection procedures scheduled for next week.",
                "priority": "high",
                "link": "/training/details",
                "recipienttype": "by_region",
                "region_ids": [1, 2, 3]
            }
        }


class BroadcastResponse(BaseModel):
    """Schema for broadcast response"""
    broadcastid: int
    senderid: int
    title: str
    message: str
    priority: str
    link: Optional[str] = None
    recipienttype: str
    recipientfilter: Optional[dict] = None
    totalrecipients: int
    deliveredcount: int
    readcount: int
    status: str
    createdat: datetime
    sentat: Optional[datetime] = None
    completedat: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BroadcastListResponse(BaseModel):
    """Schema for broadcast list response"""
    success: bool
    message: str
    data: List[BroadcastResponse]
    tag: int = 1
    total: int


class BroadcastStatsResponse(BaseModel):
    """Schema for broadcast statistics"""
    broadcastid: int
    totalrecipients: int
    deliveredcount: int
    readcount: int
    unreadcount: int
    readpercentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "broadcastid": 5,
                "totalrecipients": 45,
                "deliveredcount": 45,
                "readcount": 32,
                "unreadcount": 13,
                "readpercentage": 71.11
            }
        }