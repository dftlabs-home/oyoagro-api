"""
FILE: src/admin/__init__.py
Admin module initialization
"""
from src.admin.router import router
from src.admin.service import (
    UserManagementService,
    RoleManagementService,
    AdminStatsService
)
from src.admin.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserListResponse,
    UserDetailResponse,
    SystemStatsResponse
)

__all__ = [
    "router",
    "UserManagementService",
    "RoleManagementService",
    "AdminStatsService",
    "CreateUserRequest",
    "UpdateUserRequest",
    "UserListResponse",
    "UserDetailResponse",
    "SystemStatsResponse"
]