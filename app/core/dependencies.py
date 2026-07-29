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
    """

    token = credentials.credentials

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