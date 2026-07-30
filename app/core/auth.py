from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.platform_admin.platform_admin import PlatformAdmin

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