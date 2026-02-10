"""
FILE: src/admin/schemas.py
Admin module Pydantic schemas for user management
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime, date


# ============================================================================
# USER MANAGEMENT SCHEMAS
# ============================================================================

class UserListItem(BaseModel):
    """Schema for user in list view"""
    userid: int
    username: str
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    roleid: Optional[int] = None
    rolename: Optional[str] = None
    lganame: Optional[str] = None
    regionname: Optional[str] = None
    status: int
    isactive: bool
    islocked: bool
    lastlogindate: Optional[date] = None
    createdat: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    success: bool
    message: str
    data: List[UserListItem]
    tag: int = 1
    total: int
    page: int
    limit: int


class UserAccountDetail(BaseModel):
    """Schema for user account details"""
    userid: int
    username: str
    email: str
    status: int
    isactive: bool
    islocked: bool
    logincount: int
    lastlogindate: Optional[date] = None
    failedloginattempt: int
    createdat: datetime
    updatedat: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileDetail(BaseModel):
    """Schema for user profile details"""
    firstname: Optional[str] = None
    middlename: Optional[str] = None
    lastname: Optional[str] = None
    designation: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    photo: Optional[str] = None
    roleid: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserLocationDetail(BaseModel):
    """Schema for user location details"""
    lgaid: Optional[int] = None
    lganame: Optional[str] = None
    regionid: Optional[int] = None
    regionname: Optional[str] = None
    regions: List[str] = []


class UserStatsDetail(BaseModel):
    """Schema for user statistics"""
    farmers_registered: int = 0
    farms_registered: int = 0
    crop_registries: int = 0
    livestock_registries: int = 0
    last_activity: Optional[datetime] = None


class UserDetailResponse(BaseModel):
    """Schema for detailed user information"""
    success: bool
    message: str
    data: Dict
    tag: int = 1
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "User details retrieved successfully",
                "data": {
                    "account": {
                        "userid": 101,
                        "username": "officer1",
                        "email": "officer1@oyoagro.gov.ng",
                        "status": 1,
                        "isactive": True,
                        "islocked": False
                    },
                    "profile": {
                        "firstname": "Extension",
                        "lastname": "Officer",
                        "phonenumber": "08022222222"
                    },
                    "location": {
                        "lganame": "Ibadan North",
                        "regionname": "Ibadan Zone"
                    },
                    "stats": {
                        "farmers_registered": 45,
                        "farms_registered": 52
                    }
                },
                "tag": 1
            }
        }


class CreateUserRequest(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    firstname: str = Field(min_length=2, max_length=100)
    middlename: Optional[str] = Field(default=None, max_length=100)
    lastname: str = Field(min_length=2, max_length=100)
    phonenumber: str = Field(min_length=10, max_length=15)
    designation: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    roleid: int = Field(ge=1)
    lgaid: int = Field(ge=1)
    regionids: List[int] = Field(min_items=1) # type: ignore
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with optional _ or -)')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "officer5",
                "email": "officer5@oyoagro.gov.ng",
                "password": "TempPass123",
                "firstname": "John",
                "lastname": "Doe",
                "phonenumber": "08012345678",
                "designation": "Field Officer",
                "gender": "Male",
                "roleid": 2,
                "lgaid": 1,
                "regionids": [1, 2]
            }
        }


class UpdateUserRequest(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    firstname: Optional[str] = Field(default=None, min_length=2, max_length=100)
    middlename: Optional[str] = Field(default=None, max_length=100)
    lastname: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phonenumber: Optional[str] = Field(default=None, min_length=10, max_length=15)
    designation: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=20)
    lgaid: Optional[int] = Field(default=None, ge=1)
    regionids: Optional[List[int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "officer5_updated@oyoagro.gov.ng",
                "phonenumber": "08099999999",
                "designation": "Senior Field Officer",
                "lgaid": 2
            }
        }


class ResetPasswordRequest(BaseModel):
    """Schema for admin password reset"""
    new_password: str = Field(min_length=8, max_length=100)
    send_email: bool = Field(default=True, description="Send email notification to user")
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============================================================================
# ROLE MANAGEMENT SCHEMAS
# ============================================================================

class RoleDetail(BaseModel):
    """Schema for role details"""
    roleid: int
    rolename: str
    
    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Schema for role list"""
    success: bool
    message: str
    data: List[RoleDetail]
    tag: int = 1


class AssignRoleRequest(BaseModel):
    """Schema for assigning role to user"""
    roleid: int = Field(ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "roleid": 2
            }
        }


class PermissionDetail(BaseModel):
    """Schema for permission details"""
    activityid: int
    activityname: str
    activityparentname: str
    canadd: bool = False
    canedit: bool = False
    canview: bool = False
    candelete: bool = False
    canapprove: bool = False
    
    class Config:
        from_attributes = True


class UserPermissionsResponse(BaseModel):
    """Schema for user permissions"""
    success: bool
    message: str
    data: List[PermissionDetail]
    tag: int = 1


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class SystemOverviewStats(BaseModel):
    """Schema for system overview statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    locked_users: int
    users_by_role: Dict[str, int]
    recent_registrations: int
    recent_logins: int
    total_farmers: int
    total_farms: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 150,
                "active_users": 142,
                "inactive_users": 8,
                "locked_users": 3,
                "users_by_role": {
                    "Admin": 5,
                    "Extension Officer": 120,
                    "Supervisor": 25
                },
                "recent_registrations": 12,
                "recent_logins": 85,
                "total_farmers": 1250,
                "total_farms": 1480
            }
        }


class SystemStatsResponse(BaseModel):
    """Schema for system statistics response"""
    success: bool
    message: str
    data: SystemOverviewStats
    tag: int = 1


class UsersByRoleStats(BaseModel):
    """Schema for users by role statistics"""
    roleid: int
    rolename: str
    user_count: int
    active_count: int
    inactive_count: int


class UsersByRoleResponse(BaseModel):
    """Schema for users by role response"""
    success: bool
    message: str
    data: List[UsersByRoleStats]
    tag: int = 1


# ============================================================================
# ACTIVITY & AUDIT SCHEMAS
# ============================================================================

class RecentActivityItem(BaseModel):
    """Schema for recent activity item"""
    userid: int
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    activity_type: str
    activity_description: str
    createdat: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "userid": 101,
                "username": "officer1",
                "firstname": "Extension",
                "lastname": "Officer",
                "activity_type": "farmer_registration",
                "activity_description": "Registered new farmer: John Doe",
                "createdat": "2026-01-25T14:30:00"
            }
        }


class RecentActivityResponse(BaseModel):
    """Schema for recent activities"""
    success: bool
    message: str
    data: List[RecentActivityItem]
    tag: int = 1
    total: int


class LoginHistoryItem(BaseModel):
    """Schema for login history item"""
    userid: int
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    login_date: date
    login_count: int
    last_login: Optional[datetime] = None
    failed_attempts: int
    is_locked: bool


class LoginHistoryResponse(BaseModel):
    """Schema for login history"""
    success: bool
    message: str
    data: List[LoginHistoryItem]
    tag: int = 1
    total: int


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class UserFilterParams(BaseModel):
    """Schema for user list filter parameters"""
    search: Optional[str] = Field(default=None, description="Search by username, email, or name")
    roleid: Optional[int] = Field(default=None, ge=1, description="Filter by role")
    lgaid: Optional[int] = Field(default=None, ge=1, description="Filter by LGA")
    regionid: Optional[int] = Field(default=None, ge=1, description="Filter by region")
    status: Optional[int] = Field(default=None, ge=0, le=1, description="Filter by status (0=inactive, 1=active)")
    isactive: Optional[bool] = Field(default=None, description="Filter by active status")
    islocked: Optional[bool] = Field(default=None, description="Filter by locked status")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class BulkUserAction(BaseModel):
    """Schema for bulk user actions"""
    user_ids: List[int] = Field(min_items=1) # type: ignore
    action: str = Field(description="Action to perform: activate, deactivate, lock, unlock")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['activate', 'deactivate', 'lock', 'unlock']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v


class ExportUsersRequest(BaseModel):
    """Schema for exporting users"""
    format: str = Field(default="csv", description="Export format: csv, excel, pdf")
    include_stats: bool = Field(default=False)
    filters: Optional[UserFilterParams] = None
    
    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['csv', 'excel', 'pdf']
        if v not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v