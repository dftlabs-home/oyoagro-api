"""
FILE: src/admin/service.py
Admin service layer for user management
"""
from sqlmodel import Session, select, func, or_
from typing import List, Optional, Tuple, Dict
from datetime import datetime, date, timedelta
import logging

from src.shared.models import (
    Useraccount, Userprofile, Role, Address, Userregion,
    Region, Lga, Farmer, Farm, CropRegistry, LivestockRegistry,
    Profileactivity, Profileadditionalactivity
)
from src.core.security import simple_encrypt, generate_salt
from src.notifications.service import NotificationService
from src.notifications.types import NotificationType, NotificationPriority

logger = logging.getLogger(__name__)


class UserManagementService:
    """Service for user management operations"""
    
    @staticmethod
    async def get_all_users(
        session: Session,
        search: Optional[str] = None,
        roleid: Optional[int] = None,
        lgaid: Optional[int] = None,
        regionid: Optional[int] = None,
        status: Optional[int] = None,
        isactive: Optional[bool] = None,
        islocked: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """
        Get all users with filters and pagination
        
        Returns list of user dictionaries with profile and location info
        """
        # Build query
        query = select(
            Useraccount,
            Userprofile,
            Lga.lganame,
            Region.regionname,
            Role.rolename
        ).join( # type: ignore
            Userprofile, Userprofile.userid == Useraccount.userid, isouter=True
        ).join(
            Lga, Lga.lgaid == Useraccount.lgaid, isouter=True
        ).join(
            Role, Role.roleid == Userprofile.roleid, isouter=True
        ).join(
            Userregion, Userregion.userid == Useraccount.userid, isouter=True
        ).join(
            Region, Region.regionid == Userregion.regionid, isouter=True
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Useraccount.username.like(search_term), # type: ignore
                    Useraccount.email.like(search_term), # type: ignore
                    Userprofile.firstname.like(search_term), # type: ignore
                    Userprofile.lastname.like(search_term) # type: ignore
                )
            )
        
        if roleid:
            query = query.where(Userprofile.roleid == roleid)
        
        if lgaid:
            query = query.where(Useraccount.lgaid == lgaid)
        
        if regionid:
            query = query.where(Userregion.regionid == regionid)
        
        if status is not None:
            query = query.where(Useraccount.status == status)
        
        if isactive is not None:
            query = query.where(Useraccount.isactive == isactive)
        
        if islocked is not None:
            query = query.where(Useraccount.islocked == islocked)
        
        # Get total count
        count_query = select(func.count(Useraccount.userid.distinct())).select_from(Useraccount) # type: ignore
        if search or roleid or lgaid or regionid or status is not None or isactive is not None or islocked is not None:
            # Apply same filters to count query
            count_query = query
        
        total = session.exec(select(func.count()).select_from(query.subquery())).first() or 0
        
        # Get paginated results
        results = session.exec(
            query.order_by(Useraccount.createdat.desc()) # type: ignore
            .offset(skip)
            .limit(limit)
        ).all()
        
        # Format response
        users = []
        for row in results:
            user, profile, lganame, regionname, rolename = row
            users.append({
                "userid": user.userid,
                "username": user.username,
                "email": user.email,
                "firstname": profile.firstname if profile else None,
                "lastname": profile.lastname if profile else None,
                "roleid": profile.roleid if profile else None,
                "rolename": rolename,
                "lganame": lganame,
                "regionname": regionname,
                "status": user.status,
                "isactive": user.isactive,
                "islocked": user.islocked,
                "lastlogindate": user.lastlogindate,
                "createdat": user.createdat
            })
        
        return users, total
    
    @staticmethod
    async def get_user_detail(user_id: int, session: Session) -> Optional[Dict]:
        """Get detailed user information"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        # Get profile
        profile = session.exec(
            select(Userprofile).where(Userprofile.userid == user_id)
        ).first()
        
        # Get LGA
        lga = None
        if user.lgaid:
            lga = session.get(Lga, user.lgaid)
        
        # Get regions
        user_regions = session.exec(
            select(Userregion, Region)
            .join(Region, Region.regionid == Userregion.regionid) # type: ignore
            .where(Userregion.userid == user_id)
        ).all()
        
        regions = [{"regionid": ur.regionid, "regionname": reg.regionname} for ur, reg in user_regions]
        
        # Get user statistics
        farmers_count = session.exec(
            select(func.count(Farmer.farmerid)).where(Farmer.userid == user_id) # type: ignore
        ).first() or 0
        
        farms_count = session.exec(
            select(func.count(Farm.farmid)) # type: ignore
            .join(Farmer, Farmer.farmerid == Farm.farmerid) # type: ignore
            .where(Farmer.userid == user_id)
        ).first() or 0
        
        crop_registries = session.exec(
            select(func.count(CropRegistry.cropregistryid)) # type: ignore
            .join(Farm, Farm.farmid == CropRegistry.farmid) # type: ignore
            .join(Farmer, Farmer.farmerid == Farm.farmerid) # type: ignore
            .where(Farmer.userid == user_id)
        ).first() or 0
        
        livestock_registries = session.exec(
            select(func.count(LivestockRegistry.livestockregistryid)) # type: ignore
            .join(Farm, Farm.farmid == LivestockRegistry.farmid) # type: ignore
            .join(Farmer, Farmer.farmerid == Farm.farmerid) # type: ignore
            .where(Farmer.userid == user_id)
        ).first() or 0
        
        # Compile response
        return {
            "account": {
                "userid": user.userid,
                "username": user.username,
                "email": user.email,
                "status": user.status,
                "isactive": user.isactive,
                "islocked": user.islocked,
                "logincount": user.logincount,
                "lastlogindate": user.lastlogindate,
                "failedloginattempt": user.failedloginattempt,
                "createdat": user.createdat,
                "updatedat": user.updatedat
            },
            "profile": {
                "firstname": profile.firstname if profile else None,
                "middlename": profile.middlename if profile else None,
                "lastname": profile.lastname if profile else None,
                "designation": profile.designation if profile else None,
                "gender": profile.gender if profile else None,
                "email": profile.email if profile else None,
                "phonenumber": profile.phonenumber if profile else None,
                "photo": profile.photo if profile else None,
                "roleid": profile.roleid if profile else None
            },
            "location": {
                "lgaid": user.lgaid,
                "lganame": lga.lganame if lga else None,
                "regions": regions
            },
            "stats": {
                "farmers_registered": farmers_count,
                "farms_registered": farms_count,
                "crop_registries": crop_registries,
                "livestock_registries": livestock_registries,
                "last_activity": user.updatedat or user.createdat
            }
        }
    
    @staticmethod
    async def create_user(
        username: str,
        email: str,
        password: str,
        firstname: str,
        lastname: str,
        phonenumber: str,
        roleid: int,
        lgaid: int,
        regionids: List[int],
        session: Session,
        middlename: Optional[str] = None,
        designation: Optional[str] = None,
        gender: Optional[str] = None,
        admin_id: Optional[int] = None
    ) -> Useraccount:
        """Create a new user with profile and regions"""
        # Check if username exists
        existing_user = session.exec(
            select(Useraccount).where(Useraccount.username == username)
        ).first()
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email exists
        existing_email = session.exec(
            select(Useraccount).where(Useraccount.email == email)
        ).first()
        if existing_email:
            raise ValueError(f"Email '{email}' already exists")
        
        # Create user account
        salt = generate_salt()
        encrypted_password = simple_encrypt(password, salt)
        
        user = Useraccount(
            username=username,
            email=email,
            passwordhash=encrypted_password,
            salt=salt,
            status=1,
            isactive=True,
            islocked=False,
            logincount=0,
            failedloginattempt=0,
            lgaid=lgaid,
            createdat=datetime.utcnow()
        )
        
        session.add(user)
        session.flush()
        
        # Create user profile
        profile = Userprofile(
            userid=user.userid,
            firstname=firstname,
            middlename=middlename,
            lastname=lastname,
            email=email,
            phonenumber=phonenumber,
            designation=designation,
            gender=gender,
            roleid=roleid,
            lgaid=lgaid,
            createdat=datetime.utcnow()
        )
        session.add(profile)
        
        # Create user-region mappings
        for region_id in regionids:
            user_region = Userregion(
                userid=user.userid,
                regionid=region_id,
                createdat=datetime.utcnow()
            )
            session.add(user_region)
        
        session.commit()
        session.refresh(user)
        
        logger.info(f"User created: {username} (ID: {user.userid}) by admin {admin_id}")
        
        # Send notification to new user
        try:
            await NotificationService.create_notification(
                user_id=user.userid, # type: ignore
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.HIGH,
                title="Welcome to Oyo Agro Platform",
                message=f"Your account has been created. Username: {username}",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send notification to new user: {e}")
        
        return user
    
    @staticmethod
    async def update_user(
        user_id: int,
        session: Session,
        email: Optional[str] = None,
        firstname: Optional[str] = None,
        middlename: Optional[str] = None,
        lastname: Optional[str] = None,
        phonenumber: Optional[str] = None,
        designation: Optional[str] = None,
        gender: Optional[str] = None,
        lgaid: Optional[int] = None,
        regionids: Optional[List[int]] = None,
        admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Update user information"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        # Update user account
        if email:
            user.email = email
        if lgaid:
            user.lgaid = lgaid
        
        user.updatedat = datetime.utcnow()
        session.add(user)
        
        # Update profile
        profile = session.exec(
            select(Userprofile).where(Userprofile.userid == user_id)
        ).first()
        
        if profile:
            if firstname:
                profile.firstname = firstname
            if middlename is not None:
                profile.middlename = middlename
            if lastname:
                profile.lastname = lastname
            if email:
                profile.email = email
            if phonenumber:
                profile.phonenumber = phonenumber
            if designation is not None:
                profile.designation = designation
            if gender:
                profile.gender = gender
            if lgaid:
                profile.lgaid = lgaid
            
            profile.updatedat = datetime.utcnow()
            session.add(profile)
        
        # Update regions if provided
        if regionids is not None:
            # Delete existing regions
            existing_regions = session.exec(
                select(Userregion).where(Userregion.userid == user_id)
            ).all()
            for ur in existing_regions:
                session.delete(ur)
            
            # Add new regions
            for region_id in regionids:
                user_region = Userregion(
                    userid=user_id,
                    regionid=region_id,
                    createdat=datetime.utcnow()
                )
                session.add(user_region)
        
        session.commit()
        session.refresh(user)
        
        logger.info(f"User updated: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        return user
    
    @staticmethod
    async def activate_user(
        user_id: int, session: Session, admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Activate user account"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        user.isactive = True
        user.status = 1
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info(f"User activated: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        # Send notification
        try:
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.MEDIUM,
                title="Account Activated",
                message="Your account has been activated by an administrator",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send activation notification: {e}")
        
        return user
    
    @staticmethod
    async def deactivate_user(
        user_id: int, session: Session, admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Deactivate user account"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        user.isactive = False
        user.status = 0
        user.deactivateddate = date.today()
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info(f"User deactivated: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        # Send notification
        try:
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.HIGH,
                title="Account Deactivated",
                message="Your account has been deactivated by an administrator",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send deactivation notification: {e}")
        
        return user
    
    @staticmethod
    async def lock_user(
        user_id: int, session: Session, admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Lock user account"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        user.islocked = True
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info(f"User locked: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        # Send notification
        try:
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.URGENT,
                title="Account Locked",
                message="Your account has been locked by an administrator. Please contact support.",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send lock notification: {e}")
        
        return user
    
    @staticmethod
    async def unlock_user(
        user_id: int, session: Session, admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Unlock user account"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        user.islocked = False
        user.failedloginattempt = 0  # Reset failed attempts
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info(f"User unlocked: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        # Send notification
        try:
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.MEDIUM,
                title="Account Unlocked",
                message="Your account has been unlocked by an administrator",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send unlock notification: {e}")
        
        return user
    
    @staticmethod
    async def reset_user_password(
        user_id: int,
        new_password: str,
        session: Session,
        admin_id: Optional[int] = None
    ) -> Optional[Useraccount]:
        """Reset user password"""
        user = session.get(Useraccount, user_id)
        if not user:
            return None
        
        # Generate new password
        salt = generate_salt()
        encrypted_password = simple_encrypt(new_password, salt)
        
        user.passwordhash = encrypted_password
        user.salt = salt
        user.lastpasswordreset = datetime.utcnow()
        user.updatedat = datetime.utcnow()
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        logger.info(f"Password reset: {user.username} (ID: {user_id}) by admin {admin_id}")
        
        # Send notification
        try:
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.URGENT,
                title="Password Reset",
                message="Your password has been reset by an administrator. Please change it after logging in.",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send password reset notification: {e}")
        
        return user
    
    @staticmethod
    async def delete_user(
        user_id: int, session: Session, admin_id: Optional[int] = None
    ) -> bool:
        """Delete user (soft delete by deactivating)"""
        user = await UserManagementService.deactivate_user(user_id, session, admin_id)
        if user:
            # Could add deletedat field here if needed
            logger.info(f"User deleted: {user.username} (ID: {user_id}) by admin {admin_id}")
            return True
        return False


class RoleManagementService:
    """Service for role management operations"""
    
    @staticmethod
    async def get_all_roles(session: Session) -> List[Role]:
        """Get all roles"""
        roles = session.exec(select(Role)).all()
        return list(roles)
    
    @staticmethod
    async def get_role_by_id(role_id: int, session: Session) -> Optional[Role]:
        """Get role by ID"""
        return session.get(Role, role_id)
    
    @staticmethod
    async def assign_role_to_user(
        user_id: int,
        role_id: int,
        session: Session,
        admin_id: Optional[int] = None
    ) -> Optional[Userprofile]:
        """Assign role to user"""
        profile = session.exec(
            select(Userprofile).where(Userprofile.userid == user_id)
        ).first()
        
        if not profile:
            return None
        
        profile.roleid = role_id
        profile.updatedat = datetime.utcnow()
        
        session.add(profile)
        session.commit()
        session.refresh(profile)
        
        logger.info(f"Role assigned: User {user_id} assigned role {role_id} by admin {admin_id}")
        
        # Send notification
        try:
            role = session.get(Role, role_id)
            await NotificationService.create_notification(
                user_id=user_id,
                type=NotificationType.ADMIN_ACTION,
                priority=NotificationPriority.MEDIUM,
                title="Role Updated",
                message=f"Your role has been updated to: {role.rolename if role else 'Unknown'}",
                session=session
            )
        except Exception as e:
            logger.error(f"Failed to send role assignment notification: {e}")
        
        return profile
    
    @staticmethod
    async def get_user_permissions(user_id: int, session: Session) -> List[Dict]:
        """Get user permissions"""
        permissions = session.exec(
            select(Profileadditionalactivity, Profileactivity)
            .join(Profileactivity, Profileactivity.activityid == Profileadditionalactivity.activityid) # type: ignore
            .where(Profileadditionalactivity.userid == user_id)
        ).all()
        
        result = []
        for perm, activity in permissions:
            result.append({
                "activityid": activity.activityid,
                "activityname": activity.activityname,
                "canadd": perm.canadd,
                "canedit": perm.canedit,
                "canview": perm.canview,
                "candelete": perm.candelete,
                "canapprove": perm.canapprove
            })
        
        return result


class AdminStatsService:
    """Service for admin statistics"""
    
    @staticmethod
    async def get_system_overview(session: Session) -> Dict:
        """Get system overview statistics"""
        # Total users
        total_users = session.exec(select(func.count(Useraccount.userid))).first() or 0 # type: ignore
        
        # Active users
        active_users = session.exec(
            select(func.count(Useraccount.userid)).where(Useraccount.isactive == True) # type: ignore
        ).first() or 0
        
        # Inactive users
        inactive_users = total_users - active_users
        
        # Locked users
        locked_users = session.exec(
            select(func.count(Useraccount.userid)).where(Useraccount.islocked == True) # type: ignore
        ).first() or 0
        
        # Users by role
        users_by_role = {}
        roles = session.exec(select(Role)).all()
        for role in roles:
            count = session.exec(
                select(func.count(Userprofile.userid)).where(Userprofile.roleid == role.roleid) # type: ignore
            ).first() or 0
            users_by_role[role.rolename] = count
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = session.exec(
            select(func.count(Useraccount.userid)) # type: ignore
            .where(Useraccount.createdat >= thirty_days_ago) # type: ignore
        ).first() or 0
        
        # Recent logins (last 7 days)
        seven_days_ago = date.today() - timedelta(days=7)
        recent_logins = session.exec(
            select(func.count(Useraccount.userid)) # type: ignore
            .where(Useraccount.lastlogindate >= seven_days_ago) # type: ignore
        ).first() or 0
        
        # Total farmers
        total_farmers = session.exec(select(func.count(Farmer.farmerid))).first() or 0 # type: ignore
        
        # Total farms
        total_farms = session.exec(select(func.count(Farm.farmid))).first() or 0 # type: ignore
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "locked_users": locked_users,
            "users_by_role": users_by_role,
            "recent_registrations": recent_registrations,
            "recent_logins": recent_logins,
            "total_farmers": total_farmers,
            "total_farms": total_farms
        }
    
    @staticmethod
    async def get_users_by_role(session: Session) -> List[Dict]:
        """Get user count statistics by role"""
        roles = session.exec(select(Role)).all()
        
        result = []
        for role in roles:
            total_count = session.exec(
                select(func.count(Userprofile.userid)).where(Userprofile.roleid == role.roleid) # type: ignore
            ).first() or 0
            
            active_count = session.exec(
                select(func.count(Userprofile.userid)) # type: ignore
                .join(Useraccount, Useraccount.userid == Userprofile.userid) # type: ignore
                .where(Userprofile.roleid == role.roleid, Useraccount.isactive == True)
            ).first() or 0
            
            result.append({
                "roleid": role.roleid,
                "rolename": role.rolename,
                "user_count": total_count,
                "active_count": active_count,
                "inactive_count": total_count - active_count
            })
        
        return result
    
    @staticmethod
    async def get_recent_activities(
        session: Session, limit: int = 50
    ) -> Tuple[List[Dict], int]:
        """Get recent user activities (based on farmer registrations)"""
        # Get recent farmer registrations as proxy for activity
        activities = session.exec(
            select(Farmer, Useraccount, Userprofile)
            .join(Useraccount, Useraccount.userid == Farmer.userid) # type: ignore
            .join(Userprofile, Userprofile.userid == Useraccount.userid, isouter=True) # type: ignore
            .order_by(Farmer.createdat.desc()) # type: ignore
            .limit(limit)
        ).all()
        
        result = []
        for farmer, user, profile in activities:
            result.append({
                "userid": user.userid,
                "username": user.username,
                "firstname": profile.firstname if profile else None,
                "lastname": profile.lastname if profile else None,
                "activity_type": "farmer_registration",
                "activity_description": f"Registered farmer: {farmer.firstname} {farmer.lastname}",
                "createdat": farmer.createdat
            })
        
        return result, len(result)
    
    @staticmethod
    async def get_login_history(
        session: Session,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Dict], int]:
        """Get login history"""
        users = session.exec(
            select(Useraccount, Userprofile)
            .join(Userprofile, Userprofile.userid == Useraccount.userid, isouter=True) # type: ignore
            .where(Useraccount.lastlogindate.is_not(None)) # type: ignore
            .order_by(Useraccount.lastlogindate.desc()) # type: ignore
            .offset(skip)
            .limit(limit)
        ).all()
        
        result = []
        for user, profile in users:
            result.append({
                "userid": user.userid,
                "username": user.username,
                "firstname": profile.firstname if profile else None,
                "lastname": profile.lastname if profile else None,
                "login_date": user.lastlogindate,
                "login_count": user.logincount,
                "last_login": user.lastlogindate,
                "failed_attempts": user.failedloginattempt,
                "is_locked": user.islocked
            })
        
        total = session.exec(
            select(func.count(Useraccount.userid)) # type: ignore
            .where(Useraccount.lastlogindate.is_not(None)) # type: ignore
        ).first() or 0
        
        return result, total