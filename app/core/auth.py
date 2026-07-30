from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.core.enum import ServiceCode, Action

from app.models.platform_users.platform_users import PlatformUser
from app.models.client_admin.client_admin import ClientAdmin
from app.models.client_users.client_users import ClientUser

from app.models.service.service import Service
from app.models.user_permission.user_permission import UserPermission
from app.models.client_services.client_services import ClientService

security = HTTPBearer()


def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> PlatformAdmin:
    """
    Dependency to authenticate Platform Admin.
    Uses decode_token from security.py
    """

    token = credentials.credentials

    # Use the decode_token function from security.py
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    if payload.get("user_type") != "PLATFORM_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Platform Admins can access this resource.",
        )

    admin = (
        db.query(PlatformAdmin)
        .filter(PlatformAdmin.id == payload.get("sub"))
        .first()
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform Admin not found.",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform Admin account is inactive.",
        )

    return admin


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Generic function to get current user (can be used for any user type)
    Uses decode_token from security.py
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    return payload


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get current user ID from token without DB query.
    Useful for lightweight operations.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token.",
        )

    return user_id


def get_user_type_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Get user type from token without DB query.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_type = payload.get("user_type")
    if not user_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User type not found in token.",
        )

    return user_type


def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate token and return payload without DB query.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    return payload





def _check_permission(
    permission: UserPermission,
    action: Action,
) -> bool:
    """
    Check if a permission allows the requested action.
    Delete is reserved for Admins only.
    """

    if action == Action.DELETE:
        return False

    if action == Action.CREATE:
        return permission.can_create

    if action == Action.READ:
        return permission.can_read

    if action == Action.UPDATE:
        return permission.can_update

    return False




def require_permission(
    service: ServiceCode,
    action: Action,
):
    """
    Generic permission dependency.

    PLATFORM_ADMIN -> Full Access

    CLIENT_ADMIN -> Full Access

    PLATFORM_USER ->
        User Permissions

    CLIENT_USER ->
        Client Service +
        User Permissions
    """

    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db),
    ):

        payload = validate_token(credentials)

        user_type = payload["user_type"]
        user_id = payload["sub"]
        client_id = payload.get("client_id")

        # -----------------------------------------------------
        # PLATFORM ADMIN
        # -----------------------------------------------------

        if user_type == "PLATFORM_ADMIN":

            admin = (
                db.query(PlatformAdmin)
                .filter(
                    PlatformAdmin.id == user_id,
                    PlatformAdmin.is_active == True,
                )
                .first()
            )

            if not admin:
                raise HTTPException(
                    status_code=403,
                    detail="Platform Admin not found.",
                )

            return admin

        # -----------------------------------------------------
        # CLIENT ADMIN
        # -----------------------------------------------------

        if user_type == "CLIENT_ADMIN":

            admin = (
                db.query(ClientAdmin)
                .filter(
                    ClientAdmin.id == user_id,
                    ClientAdmin.is_active == True,
                )
                .first()
            )

            if not admin:
                raise HTTPException(
                    status_code=403,
                    detail="Client Admin not found.",
                )

            return admin

        # -----------------------------------------------------
        # SERVICE
        # -----------------------------------------------------

        service_row = (
            db.query(Service)
            .filter(
                Service.service_code == service.value,
            )
            .first()
        )

        if not service_row:
            raise HTTPException(
                status_code=404,
                detail="Service not found.",
            )

        # -----------------------------------------------------
        # PLATFORM USER
        # -----------------------------------------------------

        if user_type == "PLATFORM_USER":

            user = (
                db.query(PlatformUser)
                .filter(
                    PlatformUser.id == user_id,
                    PlatformUser.is_active == True,
                )
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=403,
                    detail="Platform User not found.",
                )

            permission = (
                db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user.id,
                    UserPermission.service_id == service_row.id,
                )
                .first()
            )

            if not permission:
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied.",
                )

            if not _check_permission(permission, action):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied.",
                )

            return user

        # -----------------------------------------------------
        # CLIENT USER
        # -----------------------------------------------------

        if user_type == "CLIENT_USER":

            user = (
                db.query(ClientUser)
                .filter(
                    ClientUser.id == user_id,
                    ClientUser.is_active == True,
                )
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=403,
                    detail="Client User not found.",
                )

            service_enabled = (
                db.query(ClientService)
                .filter(
                    ClientService.client_id == client_id,
                    ClientService.service_id == service_row.id,
                    ClientService.is_active == True,
                )
                .first()
            )

            if not service_enabled:
                raise HTTPException(
                    status_code=403,
                    detail="This service is not enabled for your client.",
                )

            permission = (
                db.query(UserPermission)
                .filter(
                    UserPermission.user_id == user.id,
                    UserPermission.service_id == service_row.id,
                )
                .first()
            )

            if not permission:
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied.",
                )

            if not _check_permission(permission, action):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied.",
                )

            return user

        raise HTTPException(
            status_code=403,
            detail="Unauthorized.",
        )

    return dependency