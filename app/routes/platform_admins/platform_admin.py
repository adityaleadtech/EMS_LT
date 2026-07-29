from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.platform_admin import (
    PlatformAdminCreate,
    PlatformAdminLogin,
    PlatformAdminUpdate,
    PlatformAdminChangePassword,
    PlatformAdminResponse,
    PlatformAdminListResponse,
    LoginResponse,
)

from app.services.platform_admin.platform_admin import (
    create_platform_admin,
    login_platform_admin,
    get_platform_admin_by_id,
    get_all_platform_admins,
    update_platform_admin,
    activate_platform_admin,
    deactivate_platform_admin,
    delete_platform_admin,
    hard_delete_platform_admin,
    count_platform_admins,
)

router = APIRouter(
    prefix="/platform-admins",
    tags=["Platform Admins"],
)



# ============================================================
# List
# ============================================================

@router.get("/", response_model=PlatformAdminListResponse)
def get_platform_admins(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    admins = get_all_platform_admins(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
    )

    total = count_platform_admins(db, is_active)

    return PlatformAdminListResponse(
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
        items=admins,
    )




# ============================================================
# Create
# ============================================================

@router.post(
    "/",
    response_model=PlatformAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_admin(
    payload: PlatformAdminCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_platform_admin(db, payload)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================
# Login
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    payload: PlatformAdminLogin,
    db: Session = Depends(get_db),
):
    try:
        return login_platform_admin(db, payload)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ============================================================
# Update
# ============================================================

@router.patch(
    "/{admin_id}",
    response_model=PlatformAdminResponse,
)
def update_admin(
    admin_id: str,
    payload: PlatformAdminUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_platform_admin(
            db,
            admin_id,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================
# Change Password
# ============================================================


# ============================================================
# Activate
# ============================================================

@router.patch(
    "/{admin_id}/activate",
    response_model=PlatformAdminResponse,
)
def activate_admin(
    admin_id: str,
    db: Session = Depends(get_db),
):
    try:
        return activate_platform_admin(
            db,
            admin_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# Deactivate
# ============================================================

@router.patch(
    "/{admin_id}/deactivate",
    response_model=PlatformAdminResponse,
)
def deactivate_admin(
    admin_id: str,
    db: Session = Depends(get_db),
):
    try:
        return deactivate_platform_admin(
            db,
            admin_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# Soft Delete
# ============================================================

@router.delete("/{admin_id}")
def delete_admin(
    admin_id: str,
    db: Session = Depends(get_db),
):
    try:
        delete_platform_admin(
            db,
            admin_id,
        )

        return {
            "success": True,
            "message": "Platform admin deleted successfully.",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# Permanent Delete
# ============================================================

@router.delete("/{admin_id}/permanent")
def permanent_delete_admin(
    admin_id: str,
    db: Session = Depends(get_db),
):
    try:
        hard_delete_platform_admin(
            db,
            admin_id,
        )

        return {
            "success": True,
            "message": "Platform admin permanently deleted.",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# Current Logged-in Admin (JWT)
# ============================================================

# from app.core.dependencies import get_current_platform_admin
#
# @router.get("/me", response_model=PlatformAdminResponse)
# def get_current_admin(
#     current_admin=Depends(get_current_platform_admin),
# ):
#     return current_admin