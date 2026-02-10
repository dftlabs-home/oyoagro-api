"""
FILE: tests/test_notifications.py
Comprehensive test suite for notifications and broadcast functionality - FINAL
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime

from src.notifications.models import Notification, Broadcast
from src.notifications.service import NotificationService, BroadcastService
from src.notifications.types import (
    NotificationType, 
    NotificationPriority,
    BroadcastRecipientType
)
from src.shared.models import Useraccount


# ============================================================================
# NOTIFICATION SERVICE TESTS
# ============================================================================

@pytest.mark.notifications
@pytest.mark.unit
class TestNotificationService:
    """Test notification service methods"""
    
    @pytest.mark.asyncio
    async def test_create_notification(self, session: Session, officer_user: dict):
        """Test creating a notification"""
        notification = await NotificationService.create_notification(
            user_id=officer_user["user"].userid,
            type=NotificationType.USER_ACTIVITY,
            priority=NotificationPriority.MEDIUM,
            title="Test Notification",
            message="This is a test message",
            link="/test",
            metadata={"test_key": "test_value"},
            session=session
        )
        
        assert notification.notificationid is not None
        assert notification.userid == officer_user["user"].userid
        assert notification.type == NotificationType.USER_ACTIVITY.value
        assert notification.priority == NotificationPriority.MEDIUM.value
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test message"
        assert notification.link == "/test"
        assert notification.notif_metadata == {"test_key": "test_value"}
        assert notification.isread is False
        assert notification.readat is None
    
    @pytest.mark.asyncio
    async def test_get_user_notifications(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test getting user notifications with pagination"""
        notifications, total = await NotificationService.get_user_notifications(
            user_id=officer_user["user"].userid,
            session=session,
            skip=0,
            limit=10
        )
        
        assert len(notifications) == 3
        assert total == 3
        assert notifications[0].title == "Notification 3"
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_filtered_by_type(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test filtering notifications by type"""
        notifications, total = await NotificationService.get_user_notifications(
            user_id=officer_user["user"].userid,
            session=session,
            type=NotificationType.ALERT.value
        )
        
        assert len(notifications) == 1
        assert notifications[0].type == NotificationType.ALERT.value
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_filtered_by_read_status(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test filtering notifications by read status"""
        notifications, total = await NotificationService.get_user_notifications(
            user_id=officer_user["user"].userid,
            session=session,
            isread=False
        )
        
        assert len(notifications) == 3
        assert all(not n.isread for n in notifications)
    
    @pytest.mark.asyncio
    async def test_get_unread_count(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test getting unread notification count"""
        count = await NotificationService.get_unread_count(
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert count == 3
    
    @pytest.mark.asyncio
    async def test_get_notification_by_id(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test getting specific notification"""
        notification = await NotificationService.get_notification_by_id(
            notification_id=test_notifications[0].notificationid,
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert notification is not None
        assert notification.notificationid == test_notifications[0].notificationid
    
    @pytest.mark.asyncio
    async def test_get_notification_wrong_user(
        self, session: Session, admin_user: dict, test_notifications: list
    ):
        """Test cannot get notification belonging to different user"""
        notification = await NotificationService.get_notification_by_id(
            notification_id=test_notifications[0].notificationid,
            user_id=admin_user["user"].userid,
            session=session
        )
        
        assert notification is None
    
    @pytest.mark.asyncio
    async def test_mark_as_read(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test marking notification as read"""
        notification = await NotificationService.mark_as_read(
            notification_id=test_notifications[0].notificationid,
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert notification is not None
        assert notification.isread is True
        assert notification.readat is not None
    
    @pytest.mark.asyncio
    async def test_mark_multiple_as_read(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test marking multiple notifications as read"""
        notification_ids = [n.notificationid for n in test_notifications[:2]]
        
        count = await NotificationService.mark_multiple_as_read(
            notification_ids=notification_ids,
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert count == 2
        
        for notif_id in notification_ids:
            notif = session.get(Notification, notif_id)
            assert notif.isread is True # type: ignore
    
    @pytest.mark.asyncio
    async def test_mark_all_as_read(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test marking all notifications as read"""
        count = await NotificationService.mark_all_as_read(
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert count == 3
        
        unread = await NotificationService.get_unread_count(
            user_id=officer_user["user"].userid,
            session=session
        )
        assert unread == 0
    
    @pytest.mark.asyncio
    async def test_delete_notification(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test soft deleting a notification"""
        deleted = await NotificationService.delete_notification(
            notification_id=test_notifications[0].notificationid,
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert deleted is True
        
        notif = session.get(Notification, test_notifications[0].notificationid)
        assert notif.deletedat is not None # type: ignore

    @pytest.mark.asyncio
    async def test_clear_all_notifications(
        self, session: Session, officer_user: dict, test_notifications: list
    ):
        """Test clearing all notifications"""
        count = await NotificationService.clear_all_notifications(
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert count == 3
        
        notifications, total = await NotificationService.get_user_notifications(
            user_id=officer_user["user"].userid,
            session=session
        )
        assert len(notifications) == 0

# ============================================================================
# BROADCAST SERVICE TESTS
# ============================================================================

@pytest.mark.notifications
@pytest.mark.unit
class TestBroadcastService:
    """Test broadcast service methods"""
    
    @pytest.mark.asyncio
    async def test_get_recipient_user_ids_all(
        self, session: Session, multiple_officers: list
    ):
        """Test getting all recipients"""
        user_ids = await BroadcastService.get_recipient_user_ids(
            recipient_type=BroadcastRecipientType.ALL,
            session=session
        )
        
        assert len(user_ids) == 3
    
    @pytest.mark.asyncio
    async def test_get_recipient_user_ids_by_lga(
        self, session: Session, multiple_officers: list, test_lga
    ):
        """Test getting recipients by LGA"""
        user_ids = await BroadcastService.get_recipient_user_ids(
            recipient_type=BroadcastRecipientType.BY_LGA,
            lga_ids=[test_lga.lgaid],
            session=session
        )
        
        assert len(user_ids) == 3
    
    @pytest.mark.asyncio
    async def test_get_recipient_user_ids_by_region(
        self, session: Session, multiple_officers: list, test_region
    ):
        """Test getting recipients by region"""
        user_ids = await BroadcastService.get_recipient_user_ids(
            recipient_type=BroadcastRecipientType.BY_REGION,
            region_ids=[test_region.regionid],
            session=session
        )
        
        assert len(user_ids) == 3
    
    @pytest.mark.asyncio
    async def test_create_broadcast_all_recipients(
        self, session: Session, admin_user: dict, multiple_officers: list
    ):
        """Test creating broadcast to all recipients"""
        broadcast = await BroadcastService.create_broadcast(
            sender_id=admin_user["user"].userid,
            title="System Announcement",
            message="Important system update for all officers",
            priority=NotificationPriority.HIGH,
            recipient_type=BroadcastRecipientType.ALL,
            session=session
        )
        
        assert broadcast.broadcastid is not None
        assert broadcast.senderid == admin_user["user"].userid
        assert broadcast.title == "System Announcement"
        assert broadcast.totalrecipients == 3
        assert broadcast.deliveredcount == 3
        assert broadcast.status == "completed"
        
        notifications = session.exec(
            select(Notification).where(
                Notification.broadcastid == broadcast.broadcastid
            )
        ).all()
        assert len(notifications) == 3
    
    @pytest.mark.asyncio
    async def test_create_broadcast_by_lga(
        self, session: Session, admin_user: dict, multiple_officers: list, test_lga
    ):
        """Test creating broadcast to specific LGA"""
        broadcast = await BroadcastService.create_broadcast(
            sender_id=admin_user["user"].userid,
            title="LGA Update",
            message="Update for Ibadan North officers",
            priority=NotificationPriority.MEDIUM,
            recipient_type=BroadcastRecipientType.BY_LGA,
            lga_ids=[test_lga.lgaid],
            session=session
        )
        
        assert broadcast.totalrecipients == 4
        assert broadcast.recipientfilter["lga_ids"] == [test_lga.lgaid] # type: ignore
    
    @pytest.mark.asyncio
    async def test_create_broadcast_by_region(
        self, session: Session, admin_user: dict, multiple_officers: list, test_region
    ):
        """Test creating broadcast to specific region"""
        broadcast = await BroadcastService.create_broadcast(
            sender_id=admin_user["user"].userid,
            title="Regional Training",
            message="Training for Ibadan Zone",
            priority=NotificationPriority.LOW,
            recipient_type=BroadcastRecipientType.BY_REGION,
            region_ids=[test_region.regionid],
            session=session
        )
        
        assert broadcast.totalrecipients == 4
        assert broadcast.recipientfilter["region_ids"] == [test_region.regionid] # type: ignore
    
    @pytest.mark.asyncio
    async def test_get_broadcast_by_id(
        self, session: Session, test_broadcast: Broadcast
    ):
        """Test getting broadcast by ID"""
        broadcast = await BroadcastService.get_broadcast_by_id(
            broadcast_id=test_broadcast.broadcastid, # type: ignore
            session=session
        )
        
        assert broadcast is not None
        assert broadcast.broadcastid == test_broadcast.broadcastid
    
    @pytest.mark.asyncio
    async def test_get_all_broadcasts(
        self, session: Session, test_broadcast: Broadcast
    ):
        """Test getting all broadcasts"""
        broadcasts, total = await BroadcastService.get_all_broadcasts(
            session=session,
            skip=0,
            limit=50
        )
        
        assert len(broadcasts) >= 1
        assert total >= 1
    
    @pytest.mark.asyncio
    async def test_update_read_count(
        self, session: Session, test_broadcast: Broadcast
    ):
        """Test updating broadcast read count"""
        notification = session.exec(
            select(Notification).where(
                Notification.broadcastid == test_broadcast.broadcastid
            )
        ).first()
        
        notification.isread = True # type: ignore
        notification.readat = datetime.utcnow() # type: ignore
        session.add(notification)
        session.commit()
        
        await BroadcastService.update_read_count(
            broadcast_id=test_broadcast.broadcastid, # type: ignore
            session=session
        )
        
        session.refresh(test_broadcast)
        assert test_broadcast.readcount == 1
    
    @pytest.mark.asyncio
    async def test_get_broadcast_stats(
        self, session: Session, test_broadcast: Broadcast
    ):
        """Test getting broadcast statistics"""
        stats = await BroadcastService.get_broadcast_stats(
            broadcast_id=test_broadcast.broadcastid, # type: ignore
            session=session
        )
        
        assert stats is not None
        assert stats["broadcastid"] == test_broadcast.broadcastid
        assert stats["totalrecipients"] == 3
        assert stats["deliveredcount"] == 3
        assert "readcount" in stats
        assert "unreadcount" in stats
        assert "readpercentage" in stats


# ============================================================================
# NOTIFICATION API TESTS
# ============================================================================

@pytest.mark.notifications
@pytest.mark.integration
class TestNotificationAPI:
    """Test notification API endpoints"""
    
    def test_get_notifications(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test GET /notifications endpoint"""
        response = client.get(
            "/api/v1/notifications?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["total"] == 3
        assert data["unread_count"] == 3
    
    def test_get_notifications_filtered(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test GET /notifications with filters"""
        response = client.get(
            f"/api/v1/notifications?type={NotificationType.ALERT.value}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
    
    def test_get_unread_count(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test GET /notifications/unread-count endpoint"""
        response = client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 3
    
    def test_get_notification_by_id(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test GET /notifications/{id} endpoint"""
        response = client.get(
            f"/api/v1/notifications/{test_notifications[0].notificationid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["notificationid"] == test_notifications[0].notificationid
    
    def test_get_notification_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test GET /notifications/{id} with invalid ID"""
        response = client.get(
            "/api/v1/notifications/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_mark_notification_as_read(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test POST /notifications/{id}/read endpoint"""
        response = client.post(
            f"/api/v1/notifications/{test_notifications[0].notificationid}/read",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["isread"] is True
    
    def test_mark_multiple_as_read(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test POST /notifications/mark-multiple-read endpoint"""
        notification_ids = [n.notificationid for n in test_notifications[:2]]
        
        response = client.post(
            "/api/v1/notifications/mark-multiple-read",
            headers=auth_headers,
            json={"notification_ids": notification_ids}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 2
    
    def test_mark_all_as_read(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test POST /notifications/mark-all-read endpoint"""
        response = client.post(
            "/api/v1/notifications/mark-all-read",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 3
    
    def test_delete_notification(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test DELETE /notifications/{id} endpoint"""
        response = client.delete(
            f"/api/v1/notifications/{test_notifications[0].notificationid}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_clear_all_notifications(
        self, client: TestClient, auth_headers: dict, test_notifications: list
    ):
        """Test DELETE /notifications/clearall endpoint"""
        response = client.delete(
            "/api/v1/notifications/clearall",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] == 3


# ============================================================================
# BROADCAST API TESTS
# ============================================================================

@pytest.mark.notifications
@pytest.mark.integration
class TestBroadcastAPI:
    """Test broadcast API endpoints"""
    
    def test_create_broadcast_all(
        self, client: TestClient, admin_headers: dict, multiple_officers: list
    ):
        """Test POST /notifications/broadcast - send to all"""
        response = client.post(
            "/api/v1/notifications/broadcast",
            headers=admin_headers,
            json={
                "title": "System Update",
                "message": "Important system maintenance scheduled",
                "priority": "high",
                "recipienttype": "all"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["totalrecipients"] == 3
        assert data["data"]["deliveredcount"] == 3
        assert data["data"]["status"] == "completed"
    
    def test_create_broadcast_by_lga(
        self, client: TestClient, admin_headers: dict, 
        multiple_officers: list, test_lga
    ):
        """Test POST /notifications/broadcast - send to specific LGA"""
        response = client.post(
            "/api/v1/notifications/broadcast",
            headers=admin_headers,
            json={
                "title": "LGA Meeting",
                "message": "Mandatory meeting for Ibadan North officers",
                "priority": "urgent",
                "recipienttype": "by_lga",
                "lga_ids": [test_lga.lgaid]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["recipienttype"] == "by_lga"
    
    def test_create_broadcast_by_region(
        self, client: TestClient, admin_headers: dict,
        multiple_officers: list, test_region
    ):
        """Test POST /notifications/broadcast - send to specific region"""
        response = client.post(
            "/api/v1/notifications/broadcast",
            headers=admin_headers,
            json={
                "title": "Regional Training",
                "message": "Training session for Ibadan Zone",
                "priority": "medium",
                "recipienttype": "by_region",
                "region_ids": [test_region.regionid]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["recipienttype"] == "by_region"
    
    def test_get_broadcasts(
        self, client: TestClient, admin_headers: dict, test_broadcast: Broadcast
    ):
        """Test GET /notifications/broadcast/list endpoint"""
        response = client.get(
            "/api/v1/notifications/broadcast/list?skip=0&limit=50",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
    
    def test_get_broadcast_by_id(
        self, client: TestClient, admin_headers: dict, test_broadcast: Broadcast
    ):
        """Test GET /notifications/broadcast/{id} endpoint"""
        response = client.get(
            f"/api/v1/notifications/broadcast/{test_broadcast.broadcastid}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["broadcastid"] == test_broadcast.broadcastid
    
    def test_get_broadcast_stats(
        self, client: TestClient, admin_headers: dict, test_broadcast: Broadcast
    ):
        """Test GET /notifications/broadcast/{id}/stats endpoint"""
        response = client.get(
            f"/api/v1/notifications/broadcast/{test_broadcast.broadcastid}/stats",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "totalrecipients" in data["data"]
        assert "deliveredcount" in data["data"]
        assert "readcount" in data["data"]
        assert "readpercentage" in data["data"]
    
    def test_broadcast_creates_individual_notifications(
        self, client: TestClient, admin_headers: dict, 
        multiple_officers: list, session: Session
    ):
        """Test that broadcast creates individual notifications for each recipient"""
        response = client.post(
            "/api/v1/notifications/broadcast",
            headers=admin_headers,
            json={
                "title": "Test Broadcast",
                "message": "Testing individual notifications",
                "priority": "low",
                "recipienttype": "all"
            }
        )
        
        assert response.status_code == 200
        broadcast_id = response.json()["data"]["broadcastid"]
        
        notifications = session.exec(
            select(Notification).where(
                Notification.broadcastid == broadcast_id
            )
        ).all()
        
        assert len(notifications) == 3
        
        for notif in notifications:
            assert notif.type == NotificationType.ADMIN_BROADCAST.value
            assert notif.title == "Test Broadcast"


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.notifications
@pytest.mark.unit
class TestNotificationEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_mark_already_read_notification(
        self, session: Session, officer_user: dict
    ):
        """Test marking already read notification as read again"""
        notification = await NotificationService.create_notification(
            user_id=officer_user["user"].userid,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Test",
            message="Test",
            session=session
        )
        
        await NotificationService.mark_as_read(
            notification_id=notification.notificationid, # type: ignore
            user_id=officer_user["user"].userid,
            session=session
        )
        
        result = await NotificationService.mark_as_read(
            notification_id=notification.notificationid, # type: ignore
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert result is not None
        assert result.isread is True
    
    @pytest.mark.asyncio
    async def test_delete_already_deleted_notification(
        self, session: Session, officer_user: dict
    ):
        """Test deleting already deleted notification"""
        notification = await NotificationService.create_notification(
            user_id=officer_user["user"].userid,
            type=NotificationType.SYSTEM,
            priority=NotificationPriority.LOW,
            title="Test",
            message="Test",
            session=session
        )
        
        await NotificationService.delete_notification(
            notification_id=notification.notificationid, # type: ignore
            user_id=officer_user["user"].userid,
            session=session
        )
        
        deleted = await NotificationService.delete_notification(
            notification_id=notification.notificationid, # type: ignore
            user_id=officer_user["user"].userid,
            session=session
        )
        
        assert deleted is False
    
    @pytest.mark.asyncio
    async def test_broadcast_with_no_recipients(
        self, session: Session, admin_user: dict
    ):
        """Test broadcast with no matching recipients"""
        broadcast = await BroadcastService.create_broadcast(
            sender_id=admin_user["user"].userid,
            title="No Recipients",
            message="This should have no recipients",
            priority=NotificationPriority.LOW,
            recipient_type=BroadcastRecipientType.BY_LGA,
            lga_ids=[99999],
            session=session
        )
        
        assert broadcast.totalrecipients == 0
        assert broadcast.deliveredcount == 0
    
    def test_unauthorized_access_to_notification(
        self, client: TestClient, auth_headers: dict, admin_user: dict, session: Session
    ):
        """Test accessing another user's notification"""
        admin_notif = Notification(
            userid=admin_user["user"].userid,
            type=NotificationType.SYSTEM.value,
            priority=NotificationPriority.LOW.value,
            title="Admin Notification",
            message="For admin only",
            createdat=datetime.utcnow()
        )
        session.add(admin_notif)
        session.commit()
        
        response = client.get(
            f"/api/v1/notifications/{admin_notif.notificationid}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])