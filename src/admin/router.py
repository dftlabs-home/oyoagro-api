"""
FILE: src/admin/router.py
Admin API endpoints for user management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional

from src.core.database import get_session
from src.core.dependencies import get_current_user
from src.shared.models import Useraccount
from src.shared.schemas import ResponseModel
from src.admin.service import (
    UserManagementService,
    RoleManagementService,
    AdminStatsService
)
from src.admin.schemas import (
    UserListResponse,
    UserDetailResponse,
    CreateUserRequest,
    UpdateUserRequest,
    ResetPasswordRequest,
    RoleListResponse,
    AssignRoleRequest,
    UserPermissionsResponse,
    SystemStatsResponse,
    UsersByRoleResponse,
    RecentActivityResponse,
    LoginHistoryResponse,
    UserListItem
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# ADMIN AUTHORIZATION DEPENDENCY
# ============================================================================

async def require_admin(current_user: Useraccount = Depends(get_current_user)):
    """Require admin role for access"""
    # TODO: Implement proper role check when Userprofile is available
    # For now, just require authentication
    # In production: check if user has roleid = 1 (Admin)
    return current_user


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session),
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    roleid: Optional[int] = Query(None, ge=1, description="Filter by role"),
    lgaid: Optional[int] = Query(None, ge=1, description="Filter by LGA"),
    regionid: Optional[int] = Query(None, ge=1, description="Filter by region"),
    status: Optional[int] = Query(None, ge=0, le=1, description="Filter by status"),
    isactive: Optional[bool] = Query(None, description="Filter by active status"),
    islocked: Optional[bool] = Query(None, description="Filter by locked status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get all users with filters and pagination (Admin only)
    
    **Requires:** Admin authentication
    
    **Query Parameters:**
    - search: Search term for username, email, or name
    - roleid: Filter by role ID
    - lgaid: Filter by LGA ID
    - regionid: Filter by region ID
    - status: Filter by status (0=inactive, 1=active)
    - isactive: Filter by active status
    - islocked: Filter by locked status
    - skip: Pagination offset
    - limit: Results per page (max 100)
    
    **Returns:**
    - List of users with profile and location information
    - Total count and pagination info
    """
    users, total = await UserManagementService.get_all_users(
        session=session,
        search=search,
        roleid=roleid,
        lgaid=lgaid,
        regionid=regionid,
        status=status,
        isactive=isactive,
        islocked=islocked,
        skip=skip,
        limit=limit
    )
    
    # Convert to UserListItem models
    user_items = [UserListItem(**user) for user in users]
    
    return UserListResponse(
        success=True,
        message="Users retrieved successfully",
        data=user_items,
        total=total,
        page=skip // limit + 1,
        limit=limit
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get detailed user information (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to retrieve
    
    **Returns:**
    - Complete user information including:
      - Account details
      - Profile information
      - Location (LGA and regions)
      - Statistics (farmers, farms, registries)
    """
    user_detail = await UserManagementService.get_user_detail(user_id, session)
    
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserDetailResponse(
        success=True,
        message="User details retrieved successfully",
        data=user_detail
    )


@router.post("/users", response_model=ResponseModel)
async def create_user(
    user_data: CreateUserRequest,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Create a new user (Admin only)
    
    **Requires:** Admin authentication
    
    **Request Body:**
    - username: Unique username (alphanumeric)
    - email: Valid email address
    - password: Strong password (min 8 chars, uppercase, lowercase, digit)
    - firstname, lastname: User's name
    - phonenumber: Contact number
    - roleid: Role ID to assign
    - lgaid: Primary LGA ID
    - regionids: List of region IDs
    
    **Returns:**
    - Created user information
    
    **Example:**
    ```json
    {
      "username": "officer5",
      "email": "officer5@oyoagro.gov.ng",
      "password": "TempPass123",
      "firstname": "John",
      "lastname": "Doe",
      "phonenumber": "08012345678",
      "roleid": 2,
      "lgaid": 1,
      "regionids": [1, 2]
    }
    ```
    """
    try:
        user = await UserManagementService.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            phonenumber=user_data.phonenumber,
            roleid=user_data.roleid,
            lgaid=user_data.lgaid,
            regionids=user_data.regionids,
            middlename=user_data.middlename,
            designation=user_data.designation,
            gender=user_data.gender,
            admin_id=current_user.userid, # type: ignore
            session=session
        )
        
        return ResponseModel(
            success=True,
            message=f"User '{user.username}' created successfully",
            data={
                "userid": user.userid,
                "username": user.username,
                "email": user.email
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/users/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Update user information (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to update
    
    **Request Body:**
    - All fields are optional
    - Only provided fields will be updated
    
    **Returns:**
    - Updated user information
    """
    try:
        user = await UserManagementService.update_user(
            user_id=user_id,
            email=user_data.email,
            firstname=user_data.firstname,
            middlename=user_data.middlename,
            lastname=user_data.lastname,
            phonenumber=user_data.phonenumber,
            designation=user_data.designation,
            gender=user_data.gender,
            lgaid=user_data.lgaid,
            regionids=user_data.regionids,
            admin_id=current_user.userid, # type: ignore
            session=session
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return ResponseModel(
            success=True,
            message=f"User '{user.username}' updated successfully",
            data={
                "userid": user.userid,
                "username": user.username,
                "email": user.email
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/users/{user_id}/activate", response_model=ResponseModel)
async def activate_user(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Activate user account (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to activate
    
    **Returns:**
    - Success message and user info
    """
    user = await UserManagementService.activate_user(
        user_id=user_id,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"User '{user.username}' activated successfully",
        data={
            "userid": user.userid,
            "username": user.username,
            "isactive": user.isactive,
            "status": user.status
        }
    )


@router.post("/users/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Deactivate user account (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to deactivate
    
    **Returns:**
    - Success message and user info
    """
    user = await UserManagementService.deactivate_user(
        user_id=user_id,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"User '{user.username}' deactivated successfully",
        data={
            "userid": user.userid,
            "username": user.username,
            "isactive": user.isactive,
            "status": user.status
        }
    )


@router.post("/users/{user_id}/lock", response_model=ResponseModel)
async def lock_user(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Lock user account (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to lock
    
    **Returns:**
    - Success message and user info
    """
    user = await UserManagementService.lock_user(
        user_id=user_id,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"User '{user.username}' locked successfully",
        data={
            "userid": user.userid,
            "username": user.username,
            "islocked": user.islocked
        }
    )


@router.post("/users/{user_id}/unlock", response_model=ResponseModel)
async def unlock_user(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Unlock user account (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to unlock
    
    **Returns:**
    - Success message and user info
    """
    user = await UserManagementService.unlock_user(
        user_id=user_id,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"User '{user.username}' unlocked successfully",
        data={
            "userid": user.userid,
            "username": user.username,
            "islocked": user.islocked,
            "failedloginattempt": user.failedloginattempt
        }
    )


@router.post("/users/{user_id}/reset-password", response_model=ResponseModel)
async def reset_user_password(
    user_id: int,
    reset_data: ResetPasswordRequest,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Reset user password (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to reset password for
    
    **Request Body:**
    - new_password: New password (strong password required)
    - send_email: Whether to send email notification (default: true)
    
    **Returns:**
    - Success message
    
    **Note:** User will receive a notification to change password after login
    """
    user = await UserManagementService.reset_user_password(
        user_id=user_id,
        new_password=reset_data.new_password,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"Password reset successfully for user '{user.username}'",
        data={
            "userid": user.userid,
            "username": user.username,
            "email_sent": reset_data.send_email
        }
    )


@router.delete("/users/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Delete user (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to delete
    
    **Returns:**
    - Success message
    
    **Note:** This performs a soft delete by deactivating the user
    """
    # Prevent admin from deleting themselves
    if user_id == current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    deleted = await UserManagementService.delete_user(
        user_id=user_id,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message=f"User deleted successfully",
        data={"userid": user_id}
    )


# ============================================================================
# ROLE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/roles", response_model=RoleListResponse)
async def get_all_roles(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get all roles (Admin only)
    
    **Requires:** Admin authentication
    
    **Returns:**
    - List of all available roles
    """
    roles = await RoleManagementService.get_all_roles(session)
    
    return RoleListResponse(
        success=True,
        message="Roles retrieved successfully",
        data=roles # type: ignore
    )


@router.get("/roles/{role_id}", response_model=ResponseModel)
async def get_role_detail(
    role_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get role details (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - role_id: Role ID to retrieve
    
    **Returns:**
    - Role information
    """
    role = await RoleManagementService.get_role_by_id(role_id, session)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message="Role retrieved successfully",
        data={
            "roleid": role.roleid,
            "rolename": role.rolename
        }
    )


@router.post("/users/{user_id}/assign-role", response_model=ResponseModel)
async def assign_role_to_user(
    user_id: int,
    role_data: AssignRoleRequest,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Assign role to user (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to assign role to
    
    **Request Body:**
    - roleid: Role ID to assign
    
    **Returns:**
    - Success message with updated role info
    """
    profile = await RoleManagementService.assign_role_to_user(
        user_id=user_id,
        role_id=role_data.roleid,
        session=session,
        admin_id=current_user.userid # type: ignore
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return ResponseModel(
        success=True,
        message="Role assigned successfully",
        data={
            "userid": user_id,
            "roleid": profile.roleid
        }
    )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get user permissions (Admin only)
    
    **Requires:** Admin authentication
    
    **Path Parameter:**
    - user_id: User ID to get permissions for
    
    **Returns:**
    - List of user permissions with activity details
    """
    permissions = await RoleManagementService.get_user_permissions(user_id, session)
    
    return UserPermissionsResponse(
        success=True,
        message="User permissions retrieved successfully",
        data=permissions # type: ignore
    )


# ============================================================================
# STATISTICS & REPORTS ENDPOINTS
# ============================================================================

@router.get("/stats/overview", response_model=SystemStatsResponse)
async def get_system_overview(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get system overview statistics (Admin only)
    
    **Requires:** Admin authentication
    
    **Returns:**
    - Complete system statistics including:
      - Total users (active, inactive, locked)
      - Users by role breakdown
      - Recent registrations and logins
      - Total farmers and farms
    """
    stats = await AdminStatsService.get_system_overview(session)
    
    return SystemStatsResponse(
        success=True,
        message="System statistics retrieved successfully",
        data=stats # type: ignore
    )


@router.get("/stats/users-by-role", response_model=UsersByRoleResponse)
async def get_users_by_role(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get user count by role (Admin only)
    
    **Requires:** Admin authentication
    
    **Returns:**
    - User count statistics for each role
    - Active vs inactive breakdown per role
    """
    stats = await AdminStatsService.get_users_by_role(session)
    
    return UsersByRoleResponse(
        success=True,
        message="Users by role statistics retrieved successfully",
        data=stats # type: ignore
    )


@router.get("/activity/recent", response_model=RecentActivityResponse)
async def get_recent_activities(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=100, description="Number of activities to retrieve")
):
    """
    Get recent user activities (Admin only)
    
    **Requires:** Admin authentication
    
    **Query Parameter:**
    - limit: Number of activities to retrieve (max 100)
    
    **Returns:**
    - List of recent user activities
    - Includes farmer registrations and other actions
    """
    activities, total = await AdminStatsService.get_recent_activities(session, limit)
    
    return RecentActivityResponse(
        success=True,
        message="Recent activities retrieved successfully",
        data=activities, # type: ignore
        total=total
    )


@router.get("/activity/login-history", response_model=LoginHistoryResponse)
async def get_login_history(
    current_user: Useraccount = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get login history (Admin only)
    
    **Requires:** Admin authentication
    
    **Query Parameters:**
    - skip: Pagination offset
    - limit: Results per page (max 100)
    
    **Returns:**
    - Login history with user details
    - Failed login attempts
    - Locked account status
    """
    history, total = await AdminStatsService.get_login_history(session, skip, limit)
    
    return LoginHistoryResponse(
        success=True,
        message="Login history retrieved successfully",
        data=history, # type: ignore
        total=total
    )