"""
FILE: src/notifications/service.py
Notification service - Enhanced with Admin Broadcast Messaging
"""
from sqlmodel import Session, select
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import logging

from src.notifications.models import Notification, Broadcast
from src.notifications.types import NotificationType, NotificationPriority, BroadcastRecipientType
from src.shared.models import Useraccount, Userprofile, Userregion

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    async def create_notification(
        user_id: int,
        type: NotificationType,
        priority: NotificationPriority,
        title: str,
        message: str,
        session: Session,
        link: Optional[str] = None,
        metadata: Optional[dict] = None,
        broadcast_id: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            user_id: User ID to notify
            type: Notification type
            priority: Notification priority
            title: Notification title
            message: Notification message
            session: Database session
            link: Optional link to related resource
            metadata: Optional additional data
            broadcast_id: Optional broadcast ID if part of broadcast
            
        Returns:
            Created notification
        """
        notification = Notification(
            userid=user_id,
            type=type.value,
            priority=priority.value,
            title=title,
            message=message,
            link=link,
            notif_metadata=metadata,
            broadcastid=broadcast_id,
            isread=False,
            createdat=datetime.utcnow()
        )
        
        session.add(notification)
        session.commit()
        session.refresh(notification)
        
        logger.info(f"Notification created for user {user_id}: {title}")
        
        return notification
    
    @staticmethod
    async def get_user_notifications(
        user_id: int,
        session: Session,
        skip: int = 0,
        limit: int = 20,
        type: Optional[str] = None,
        priority: Optional[str] = None,
        isread: Optional[bool] = None
    ) -> Tuple[List[Notification], int]:
        """Get user notifications with filtering and pagination"""
        query = select(Notification).where(
            Notification.userid == user_id,
            Notification.deletedat.is_(None) # type: ignore
        )
        
        if type:
            query = query.where(Notification.type == type)
        if priority:
            query = query.where(Notification.priority == priority)
        if isread is not None:
            query = query.where(Notification.isread == isread)
        
        # Get total count
        count_query = select(Notification).where(
            Notification.userid == user_id,
            Notification.deletedat.is_(None) # type: ignore
        )
        if type:
            count_query = count_query.where(Notification.type == type)
        if priority:
            count_query = count_query.where(Notification.priority == priority)
        if isread is not None:
            count_query = count_query.where(Notification.isread == isread)
        
        total = len(session.exec(count_query).all())
        
        query = query.order_by(Notification.createdat.desc()).offset(skip).limit(limit) # type: ignore
        notifications = session.exec(query).all()
        
        return list(notifications), total
    
    @staticmethod
    async def get_unread_count(user_id: int, session: Session) -> int:
        """Get count of unread notifications for user"""
        query = select(Notification).where(
            Notification.userid == user_id,
            Notification.isread == False,
            Notification.deletedat.is_(None) # type: ignore
        )
        return len(session.exec(query).all())
    
    @staticmethod
    async def get_notification_by_id(
        notification_id: int,
        user_id: int,
        session: Session
    ) -> Optional[Notification]:
        """Get specific notification by ID"""
        query = select(Notification).where(
            Notification.notificationid == notification_id,
            Notification.userid == user_id,
            Notification.deletedat.is_(None) # type: ignore
        )
        return session.exec(query).first()
    
    @staticmethod
    async def mark_as_read(
        notification_id: int,
        user_id: int,
        session: Session
    ) -> Optional[Notification]:
        """Mark notification as read"""
        notification = await NotificationService.get_notification_by_id(
            notification_id, user_id, session
        )
        
        if notification and not notification.isread:
            notification.isread = True
            notification.readat = datetime.utcnow()
            notification.updatedat = datetime.utcnow()
            
            session.add(notification)
            session.commit()
            session.refresh(notification)
            
            # Update broadcast read count if applicable
            if notification.broadcastid:
                await BroadcastService.update_read_count(notification.broadcastid, session)
            
            logger.info(f"Notification {notification_id} marked as read for user {user_id}")
        
        return notification
    
    @staticmethod
    async def mark_multiple_as_read(
        notification_ids: List[int],
        user_id: int,
        session: Session
    ) -> int:
        """Mark multiple notifications as read"""
        query = select(Notification).where(
            Notification.notificationid.in_(notification_ids), # type: ignore
            Notification.userid == user_id,
            Notification.isread == False,
            Notification.deletedat.is_(None) # type: ignore
        )
        
        notifications = session.exec(query).all()
        count = 0
        broadcast_ids = set()
        
        for notification in notifications:
            notification.isread = True
            notification.readat = datetime.utcnow()
            notification.updatedat = datetime.utcnow()
            session.add(notification)
            count += 1
            
            if notification.broadcastid:
                broadcast_ids.add(notification.broadcastid)
        
        session.commit()
        
        # Update broadcast read counts
        for broadcast_id in broadcast_ids:
            await BroadcastService.update_read_count(broadcast_id, session)
        
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count
    
    @staticmethod
    async def mark_all_as_read(user_id: int, session: Session) -> int:
        """Mark all user notifications as read"""
        query = select(Notification).where(
            Notification.userid == user_id,
            Notification.isread == False,
            Notification.deletedat.is_(None) # type: ignore
        )
        
        notifications = session.exec(query).all()
        count = 0
        broadcast_ids = set()
        
        for notification in notifications:
            notification.isread = True
            notification.readat = datetime.utcnow()
            notification.updatedat = datetime.utcnow()
            session.add(notification)
            count += 1
            
            if notification.broadcastid:
                broadcast_ids.add(notification.broadcastid)
        
        session.commit()
        
        # Update broadcast read counts
        for broadcast_id in broadcast_ids:
            await BroadcastService.update_read_count(broadcast_id, session)
        
        logger.info(f"Marked all {count} notifications as read for user {user_id}")
        return count
    
    @staticmethod
    async def delete_notification(
        notification_id: int,
        user_id: int,
        session: Session
    ) -> bool:
        """Delete notification (soft delete)"""
        notification = await NotificationService.get_notification_by_id(
            notification_id, user_id, session
        )
        
        if notification:
            notification.deletedat = datetime.utcnow()
            notification.updatedat = datetime.utcnow()
            session.add(notification)
            session.commit()
            logger.info(f"Notification {notification_id} deleted for user {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def clear_all_notifications(user_id: int, session: Session) -> int:
        """Clear all user notifications (soft delete)"""
        query = select(Notification).where(
            Notification.userid == user_id,
            Notification.deletedat.is_(None) # type: ignore
        )
        
        notifications = session.exec(query).all()
        count = 0
        
        for notification in notifications:
            notification.deletedat = datetime.utcnow()
            notification.updatedat = datetime.utcnow()
            session.add(notification)
            count += 1
        
        session.commit()
        logger.info(f"Cleared all {count} notifications for user {user_id}")
        return count


class BroadcastService:
    """Service for managing broadcast messages"""
    
    @staticmethod
    async def get_recipient_user_ids(
        recipient_type: BroadcastRecipientType,
        session: Session,
        lga_ids: Optional[List[int]] = None,
        region_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None
    ) -> List[int]:
        """
        Get list of user IDs based on recipient criteria
        
        Args:
            recipient_type: Type of recipients
            session: Database session
            lga_ids: LGA IDs if filtering by LGA
            region_ids: Region IDs if filtering by region
            role_ids: Role IDs if filtering by role
            
        Returns:
            List of user IDs
        """
        user_ids = []
        
        if recipient_type == BroadcastRecipientType.ALL:
            # Get all active users (exclude admins - roleid != 1)
            query = select(Useraccount.userid).join(
                Userprofile, Userprofile.userid == Useraccount.userid # type: ignore
            ).where(
                Useraccount.status == 1,
                Useraccount.islocked == False,
                Userprofile.roleid != 1  # Exclude admins
            )
            users = session.exec(query).all()
            user_ids = [u for u in users]
            
        elif recipient_type == BroadcastRecipientType.BY_LGA and lga_ids:
            # Get users in specific LGAs
            query = select(Useraccount.userid).where(
                Useraccount.status == 1,
                Useraccount.islocked == False,
                Useraccount.lgaid.in_(lga_ids) # type: ignore
            )
            users = session.exec(query).all()
            user_ids = [u for u in users]
            
        elif recipient_type == BroadcastRecipientType.BY_REGION and region_ids:
            # Get users in specific regions via Userregion table
            query = select(Userregion.userid).where(
                Userregion.regionid.in_(region_ids) # type: ignore
            )
            region_users = session.exec(query).all()
            
            # Filter for active users
            if region_users:
                user_query = select(Useraccount.userid).where(
                    Useraccount.userid.in_(region_users), # type: ignore
                    Useraccount.status == 1,
                    Useraccount.islocked == False
                )
                users = session.exec(user_query).all()
                user_ids = [u for u in users]
                
        elif recipient_type == BroadcastRecipientType.BY_ROLE and role_ids:
            # Get users with specific roles
            query = select(Userprofile.userid).where(
                Userprofile.roleid.in_(role_ids) # type: ignore
            )
            role_users = session.exec(query).all()
            
            # Filter for active users
            if role_users:
                user_query = select(Useraccount.userid).where(
                    Useraccount.userid.in_(role_users), # type: ignore
                    Useraccount.status == 1,
                    Useraccount.islocked == False
                )
                users = session.exec(user_query).all()
                user_ids = [u for u in users]
        
        return user_ids # type: ignore
    
    @staticmethod
    async def create_broadcast(
        sender_id: int,
        title: str,
        message: str,
        priority: NotificationPriority,
        recipient_type: BroadcastRecipientType,
        session: Session,
        link: Optional[str] = None,
        lga_ids: Optional[List[int]] = None,
        region_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None
    ) -> Broadcast:
        """
        Create and send a broadcast message
        
        Args:
            sender_id: Admin user ID who is sending
            title: Broadcast title
            message: Broadcast message
            priority: Message priority
            recipient_type: Type of recipients
            session: Database session
            link: Optional link
            lga_ids: LGA IDs if filtering by LGA
            region_ids: Region IDs if filtering by region
            role_ids: Role IDs if filtering by role
            
        Returns:
            Created broadcast with statistics
        """
        # Build recipient filter
        recipient_filter = {}
        if lga_ids:
            recipient_filter["lga_ids"] = lga_ids
        if region_ids:
            recipient_filter["region_ids"] = region_ids
        if role_ids:
            recipient_filter["role_ids"] = role_ids
        
        # Create broadcast record
        broadcast = Broadcast(
            senderid=sender_id,
            title=title,
            message=message,
            priority=priority.value,
            link=link,
            recipienttype=recipient_type.value,
            recipientfilter=recipient_filter if recipient_filter else None,
            status="pending",
            createdat=datetime.utcnow()
        )
        
        session.add(broadcast)
        session.flush()  # Get broadcast ID
        
        # Get recipient user IDs
        recipient_user_ids = await BroadcastService.get_recipient_user_ids(
            recipient_type=recipient_type,
            session=session,
            lga_ids=lga_ids,
            region_ids=region_ids,
            role_ids=role_ids
        )
        
        # Update broadcast with recipient count
        broadcast.totalrecipients = len(recipient_user_ids)
        broadcast.status = "sending"
        broadcast.sentat = datetime.utcnow()
        session.add(broadcast)
        session.commit()
        
        # Create notifications for all recipients
        delivered_count = 0
        for user_id in recipient_user_ids:
            try:
                await NotificationService.create_notification(
                    user_id=user_id,
                    type=NotificationType.ADMIN_BROADCAST,
                    priority=priority,
                    title=title,
                    message=message,
                    link=link,
                    broadcast_id=broadcast.broadcastid,
                    session=session
                )
                delivered_count += 1
            except Exception as e:
                logger.error(f"Failed to create notification for user {user_id}: {e}")
        
        # Update broadcast statistics
        broadcast.deliveredcount = delivered_count
        broadcast.status = "completed"
        broadcast.completedat = datetime.utcnow()
        session.add(broadcast)
        session.commit()
        session.refresh(broadcast)
        
        logger.info(
            f"Broadcast {broadcast.broadcastid} sent by admin {sender_id}: "
            f"{delivered_count}/{broadcast.totalrecipients} delivered"
        )
        
        return broadcast
    
    @staticmethod
    async def get_broadcast_by_id(
        broadcast_id: int,
        session: Session
    ) -> Optional[Broadcast]:
        """Get specific broadcast by ID"""
        return session.get(Broadcast, broadcast_id)
    
    @staticmethod
    async def get_all_broadcasts(
        session: Session,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Broadcast], int]:
        """Get all broadcasts with pagination"""
        query = select(Broadcast).order_by(Broadcast.createdat.desc()) # type: ignore
        
        total = len(session.exec(query).all())
        
        broadcasts = session.exec(query.offset(skip).limit(limit)).all()
        
        return list(broadcasts), total
    
    @staticmethod
    async def update_read_count(broadcast_id: int, session: Session) -> None:
        """Update read count for a broadcast"""
        broadcast = session.get(Broadcast, broadcast_id)
        if broadcast:
            # Count read notifications for this broadcast
            query = select(Notification).where(
                Notification.broadcastid == broadcast_id,
                Notification.isread == True
            )
            read_count = len(session.exec(query).all())
            
            broadcast.readcount = read_count
            session.add(broadcast)
            session.commit()
    
    @staticmethod
    async def get_broadcast_stats(
        broadcast_id: int,
        session: Session
    ) -> Optional[Dict]:
        """Get detailed statistics for a broadcast"""
        broadcast = session.get(Broadcast, broadcast_id)
        if not broadcast:
            return None
        
        # Refresh read count
        await BroadcastService.update_read_count(broadcast_id, session)
        session.refresh(broadcast)
        
        unread_count = broadcast.deliveredcount - broadcast.readcount
        read_percentage = (
            (broadcast.readcount / broadcast.deliveredcount * 100)
            if broadcast.deliveredcount > 0 else 0
        )
        
        return {
            "broadcastid": broadcast.broadcastid,
            "totalrecipients": broadcast.totalrecipients,
            "deliveredcount": broadcast.deliveredcount,
            "readcount": broadcast.readcount,
            "unreadcount": unread_count,
            "readpercentage": round(read_percentage, 2)
        }