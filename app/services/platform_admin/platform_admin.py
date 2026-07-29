from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.platform_admin.platform_admin import PlatformAdmin
from app.schemas.platform_admin import (
    PlatformAdminCreate,
    PlatformAdminLogin,
    PlatformAdminUpdate,
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def create_platform_admin(db: Session, payload: PlatformAdminCreate):

    existing_admin = (
        db.query(PlatformAdmin)
        .filter(PlatformAdmin.email == payload.email)
        .first()
    )

    if existing_admin:
        raise ValueError("Platform admin already exists.")

    admin = PlatformAdmin(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password=hash_password(payload.password),
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def login_platform_admin(db: Session, payload: PlatformAdminLogin):

    admin = (
        db.query(PlatformAdmin)
        .filter(PlatformAdmin.email == payload.email)
        .first()
    )

    if not admin:
        raise ValueError("Invalid email or password.")

    if not verify_password(payload.password, admin.password):
        raise ValueError("Invalid email or password.")

    if not admin.is_active:
        raise ValueError("Platform admin is inactive.")

    admin.last_login = datetime.utcnow()

    db.commit()

    access_token = create_access_token(
        {
            "sub": str(admin.id),
            "role": "PLATFORM_ADMIN",
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": admin,
    }


def get_platform_admin_by_id(db: Session, admin_id: str):

    return (
        db.query(PlatformAdmin)
        .filter(PlatformAdmin.id == admin_id)
        .first()
    )


def get_all_platform_admins(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
):

    query = db.query(PlatformAdmin)

    if is_active is not None:
        query = query.filter(PlatformAdmin.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def update_platform_admin(
    db: Session,
    admin_id: str,
    payload: PlatformAdminUpdate,
):

    admin = get_platform_admin_by_id(db, admin_id)

    if not admin:
        raise ValueError("Platform admin not found.")

    if payload.full_name is not None:
        admin.full_name = payload.full_name

    if payload.email is not None:
        existing = (
            db.query(PlatformAdmin)
            .filter(
                PlatformAdmin.email == payload.email,
                PlatformAdmin.id != admin_id,
            )
            .first()
        )

        if existing:
            raise ValueError("Email already exists.")

        admin.email = payload.email

    if payload.phone is not None:
        admin.phone = payload.phone

    if payload.password:
        admin.password = hash_password(payload.password)

    db.commit()
    db.refresh(admin)

    return admin


def delete_platform_admin(
    db: Session,
    admin_id: str,
):

    admin = get_platform_admin_by_id(db, admin_id)

    if not admin:
        raise ValueError("Platform admin not found.")

    admin.is_active = False

    db.commit()


def hard_delete_platform_admin(
    db: Session,
    admin_id: str,
):

    admin = get_platform_admin_by_id(db, admin_id)

    if not admin:
        raise ValueError("Platform admin not found.")

    db.delete(admin)
    db.commit()


def activate_platform_admin(
    db: Session,
    admin_id: str,
):

    admin = get_platform_admin_by_id(db, admin_id)

    if not admin:
        raise ValueError("Platform admin not found.")

    admin.is_active = True

    db.commit()
    db.refresh(admin)

    return admin


def deactivate_platform_admin(
    db: Session,
    admin_id: str,
):

    admin = get_platform_admin_by_id(db, admin_id)

    if not admin:
        raise ValueError("Platform admin not found.")

    admin.is_active = False

    db.commit()
    db.refresh(admin)

    return admin


def count_platform_admins(
    db: Session,
    is_active: bool | None = None,
):

    query = db.query(PlatformAdmin)

    if is_active is not None:
        query = query.filter(PlatformAdmin.is_active == is_active)

    return query.count()