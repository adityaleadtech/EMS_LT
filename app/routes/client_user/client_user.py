from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import admin_required

from app.models.platform_admin.platform_admin import PlatformAdmin

from app.schemas.client_user.client_user import (
    ClientUserCreate,
    ClientUserUpdate,
    ClientUserLogin,
    
    ClientUserResponse,
    ClientUserLoginResponse,
    ClientUserListResponse,
)

from app.services.client_user.client_user import (
    ClientUserService,
)

router = APIRouter(
    prefix="/client-users",
    tags=["Client Users"],
)


# ==========================================================
# CREATE CLIENT USER
# ==========================================================

@router.post(
    "",
    response_model=ClientUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Client User",
)
def create_client_user(
    payload: ClientUserCreate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.create_client_user(
        db=db,
        payload=payload,
        created_by=admin.id,
    )


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=ClientUserLoginResponse,
    summary="Client User Login",
)
def login(
    payload: ClientUserLogin,
    db: Session = Depends(get_db),
):
    return ClientUserService.login(
        db=db,
        payload=payload,
    )


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=ClientUserListResponse,
    summary="Get Client Users",
)
def get_client_users(
    client_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.get_all(
        db=db,
        client_id=client_id,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )


# ==========================================================
# COUNT
# ==========================================================

@router.get(
    "/count",
    summary="Count Client Users",
)
def count_client_users(
    client_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return {
        "count": ClientUserService.count(
            db=db,
            client_id=client_id,
            is_active=is_active,
            search=search,
        )
    }


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{user_id}",
    response_model=ClientUserResponse,
    summary="Get Client User",
)
def get_client_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.get_by_id(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{user_id}",
    response_model=ClientUserResponse,
    summary="Update Client User",
)
def update_client_user(
    user_id: str,
    payload: ClientUserUpdate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.update(
        db=db,
        user_id=user_id,
        payload=payload,
    )


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{user_id}",
    summary="Delete Client User",
)
def delete_client_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.delete(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# RESTORE
# ==========================================================

@router.patch(
    "/{user_id}/restore",
    response_model=ClientUserResponse,
    summary="Restore Client User",
)
def restore_client_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.restore(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================


# ==========================================================
# GET USER PERMISSIONS
# ==========================================================

@router.get(
    "/{user_id}/permissions",
    summary="Get Client User Permissions",
)
def get_permissions(
    user_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.get_permissions(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# UPDATE USER PERMISSIONS
# ==========================================================

@router.put(
    "/{user_id}/permissions",
    summary="Update Client User Permissions",
)
def update_permissions(
    user_id: str,
    permissions: list,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientUserService.update_permissions(
        db=db,
        user_id=user_id,
        permissions=permissions,
    )