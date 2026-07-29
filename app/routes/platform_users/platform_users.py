from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import admin_required
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.schemas.platform_users import (
    PlatformUserCreate,
    PlatformUserLogin,
    PlatformUserUpdate,
    PlatformUserChangePassword,
    PlatformUserResponse,
    PlatformUserLoginResponse,
    PlatformUserListResponse,
)
from app.services.platform_users.platform_users import PlatformUserService

router = APIRouter(
    prefix="/platform-users",
    tags=["Platform Users"],
)


# ==================== PUBLIC ENDPOINTS ====================

@router.post(
    "/login",
    response_model=PlatformUserLoginResponse,
    summary="Login Platform User",
    description="Authenticates a platform user and returns a JWT access token"
)
def login(
    payload: PlatformUserLogin,
    db: Session = Depends(get_db),
):
    """
    Login endpoint - Public access
    """
    return PlatformUserService.login(
        db=db,
        payload=payload,
    )


# ==================== PROTECTED ENDPOINTS (Admin Only) ====================

@router.post(
    "/",
    response_model=PlatformUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Platform User",
    description="Creates a new platform user (Admin only)"
)
def create_platform_user(
    payload: PlatformUserCreate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Create a new platform user - Requires Platform Admin authentication
    """
    return PlatformUserService.create_platform_user(
        db=db,
        payload=payload,
        created_by=admin.id,  # Track which admin created this user
    )


@router.get(
    "/",
    response_model=PlatformUserListResponse,
    summary="Get All Platform Users",
    description="Retrieves a paginated list of all platform users (Admin only)"
)
def get_platform_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None, description="Search by name, email, employee ID, or phone"),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get all platform users with pagination and filtering - Requires Platform Admin authentication
    """
    return PlatformUserService.get_all(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )


@router.get(
    "/count",
    summary="Get Platform Users Count",
    description="Returns the total number of platform users (Admin only)"
)
def count_platform_users(
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None, description="Search by name, email, employee ID, or phone"),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get total count of platform users - Requires Platform Admin authentication
    """
    count = PlatformUserService.count(
        db=db,
        is_active=is_active,
        search=search,
    )
    return {"total": count}


@router.get(
    "/{user_id}",
    response_model=PlatformUserResponse,
    summary="Get Platform User by ID",
    description="Retrieves a specific platform user by their UUID (Admin only)"
)
def get_platform_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get platform user by ID - Requires Platform Admin authentication
    """
    return PlatformUserService.get_by_id(
        db=db,
        user_id=user_id,
    )


@router.put(
    "/{user_id}",
    response_model=PlatformUserResponse,
    summary="Update Platform User",
    description="Updates a platform user's details (Admin only)"
)
def update_platform_user(
    user_id: str,
    payload: PlatformUserUpdate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Update platform user - Requires Platform Admin authentication
    """
    return PlatformUserService.update(
        db=db,
        user_id=user_id,
        payload=payload,
    )


@router.delete(
    "/{user_id}",
    summary="Soft Delete Platform User",
    description="Soft deletes a platform user (sets is_active=False) (Admin only)"
)
def delete_platform_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Soft delete platform user - Requires Platform Admin authentication
    """
    return PlatformUserService.delete(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}/restore",
    response_model=PlatformUserResponse,
    summary="Restore Platform User",
    description="Restores a soft-deleted platform user (Admin only)"
)
def restore_platform_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Restore platform user - Requires Platform Admin authentication
    """
    return PlatformUserService.restore(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}/change-password",
    summary="Change Platform User Password",
    description="Changes a platform user's password (Admin only)"
)
def change_password(
    user_id: str,
    payload: PlatformUserChangePassword,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Change platform user password - Requires Platform Admin authentication
    """
    # Validate password confirmation
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match.",
        )

    return PlatformUserService.change_password(
        db=db,
        user_id=user_id,
        payload=payload,
    )


@router.get(
    "/{user_id}/permissions",
    response_model=List[Dict[str, Any]],
    summary="Get Platform User Permissions",
    description="Retrieves all permissions for a platform user (Admin only)"
)
def get_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get platform user permissions - Requires Platform Admin authentication
    """
    return PlatformUserService.get_permissions(
        db=db,
        user_id=user_id,
    )


@router.put(
    "/{user_id}/permissions",
    summary="Update Platform User Permissions",
    description="Updates all permissions for a platform user (Admin only)"
)
def update_permissions(
    user_id: str,
    permissions: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Update platform user permissions - Requires Platform Admin authentication
    """
    return PlatformUserService.update_permissions(
        db=db,
        user_id=user_id,
        permissions=permissions,
    )


@router.get(
    "/me",
    response_model=PlatformUserResponse,
    summary="Get Current Platform User",
    description="Retrieves the currently authenticated platform user's profile"
)
def get_current_user(
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get current platform user profile - Requires Platform Admin authentication
    Note: This returns the admin's own profile since they are the ones authenticated
    """
    return PlatformUserService.get_by_id(
        db=db,
        user_id=admin.id,
    )