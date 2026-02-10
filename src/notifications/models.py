"""
FILE: src/notifications/models.py
Notification database models - Enhanced with Broadcast Messages - FIXED
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from typing import Optional
from datetime import datetime


class Notification(SQLModel, table=True):
    """
    Notification model for in-app notifications
    
    Tracks user notifications with type, priority, read status, and metadata
    """
    __tablename__ = "notification" # type: ignore
    
    notificationid: Optional[int] = Field(default=None, primary_key=True)
    userid: int = Field(foreign_key="useraccount.userid", index=True)
    
    # Notification content
    type: str = Field(max_length=50, index=True)
    priority: str = Field(max_length=20)
    title: str = Field(max_length=200)
    message: str = Field(sa_column=Column(Text))  # FIXED: Use Column(Text) instead
    link: Optional[str] = Field(default=None, max_length=500)
    
    # Status tracking
    isread: bool = Field(default=False, index=True)
    readat: Optional[datetime] = Field(default=None)
    
    # Metadata (JSON field for additional data)
    notif_metadata: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSON))  # FIXED: Renamed field, custom column name
    
    # Broadcast tracking (if this notification is part of a broadcast)
    broadcastid: Optional[int] = Field(default=None, foreign_key="broadcast.broadcastid", index=True)
    
    # Timestamps
    createdat: datetime = Field(default_factory=datetime.utcnow, index=True)
    updatedat: Optional[datetime] = Field(default=None)
    deletedat: Optional[datetime] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "userid": 1,
                "type": "admin_broadcast",
                "priority": "high",
                "title": "Important System Update",
                "message": "Please update your profile information by end of week",
                "link": "/profile",
                "isread": False,
                "broadcastid": 5
            }
        }


class Broadcast(SQLModel, table=True):
    """
    Broadcast message model for admin-initiated mass notifications
    
    Tracks broadcast campaigns sent to multiple users
    """
    __tablename__ = "broadcast" # type: ignore
    
    broadcastid: Optional[int] = Field(default=None, primary_key=True)
    
    # Sender information
    senderid: int = Field(foreign_key="useraccount.userid")  # Admin who sent it
    
    # Broadcast content
    title: str = Field(max_length=200)
    message: str = Field(sa_column=Column(Text))  # FIXED: Use Column(Text)
    priority: str = Field(max_length=20)
    link: Optional[str] = Field(default=None, max_length=500)
    
    # Recipient targeting
    recipienttype: str = Field(max_length=50)  # all, by_lga, by_region, by_role
    recipientfilter: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # LGA IDs, Region IDs, etc.
    
    # Statistics
    totalrecipients: int = Field(default=0)
    deliveredcount: int = Field(default=0)
    readcount: int = Field(default=0)
    
    # Status
    status: str = Field(max_length=20, default="pending")  # pending, sending, completed, failed
    
    # Timestamps
    createdat: datetime = Field(default_factory=datetime.utcnow)
    sentat: Optional[datetime] = Field(default=None)
    completedat: Optional[datetime] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "senderid": 100,
                "title": "Training Session Announcement",
                "message": "Mandatory training on new data collection system...",
                "priority": "high",
                "recipienttype": "by_region",
                "recipientfilter": {"region_ids": [1, 2, 3]},
                "totalrecipients": 45,
                "status": "completed"
            }
        }