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

from app.schemas.client_admin.client_admin import (
    ClientAdminCreate,
    ClientAdminUpdate,
    ClientAdminLogin,
    ClientAdminChangePassword,
    ClientAdminResponse,
    ClientAdminLoginResponse,
    ClientAdminListResponse,
    ClientAdminCountResponse,
)

from app.services.client_admin.client_admin import (
    ClientAdminService,
)

router = APIRouter(
    prefix="/client-admins",
    tags=["Client Admins"],
)


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "/",
    response_model=ClientAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Client Admin",
)
def create_client_admin(
    payload: ClientAdminCreate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.create_client_admin(
        db=db,
        payload=payload,
        created_by=admin.id,
    )


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=ClientAdminLoginResponse,
    summary="Client Admin Login",
)
def login(
    payload: ClientAdminLogin,
    db: Session = Depends(get_db),
):
    return ClientAdminService.login(
        db=db,
        payload=payload,
    )


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "/",
    response_model=ClientAdminListResponse,
    summary="Get Client Admins",
)
def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.get_all(
        db=db,
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
    response_model=ClientAdminCountResponse,
    summary="Count Client Admins",
)
def count(
    is_active: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminCountResponse(
        total=ClientAdminService.count(
            db=db,
            is_active=is_active,
            search=search,
        )
    )


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{client_admin_id}",
    response_model=ClientAdminResponse,
    summary="Get Client Admin",
)
def get_by_id(
    client_admin_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.get_by_id(
        db=db,
        client_admin_id=client_admin_id,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{client_admin_id}",
    response_model=ClientAdminResponse,
    summary="Update Client Admin",
)
def update(
    client_admin_id: str,
    payload: ClientAdminUpdate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.update(
        db=db,
        client_admin_id=client_admin_id,
        payload=payload,
    )


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{client_admin_id}",
    summary="Delete Client Admin",
)
def delete(
    client_admin_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.delete(
        db=db,
        client_admin_id=client_admin_id,
    )


# ==========================================================
# RESTORE
# ==========================================================

@router.patch(
    "/{client_admin_id}/restore",
    response_model=ClientAdminResponse,
    summary="Restore Client Admin",
)
def restore(
    client_admin_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.restore(
        db=db,
        client_admin_id=client_admin_id,
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@router.patch(
    "/{client_admin_id}/change-password",
    summary="Change Client Admin Password",
)
def change_password(
    client_admin_id: str,
    payload: ClientAdminChangePassword,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientAdminService.change_password(
        db=db,
        client_admin_id=client_admin_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )