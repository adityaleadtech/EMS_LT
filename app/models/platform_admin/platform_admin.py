import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.sql import func

from app.core.database import Base


class PlatformAdmin(Base):
    __tablename__ = "platform_admins"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String(20),
        unique=True,
        nullable=True,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    profile_image = Column(
        String(500),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    last_login = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )