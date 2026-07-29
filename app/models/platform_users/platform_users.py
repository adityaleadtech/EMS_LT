from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    func,
)

from app.core.database import Base


class PlatformUser(Base):
    __tablename__ = "platform_users"

    id = Column(String(36), primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    email = Column(String(150), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    phone = Column(String(20), unique=True, nullable=True)

    employee_id = Column(String(50), unique=True, nullable=True)

    profile_image = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    last_login = Column(DateTime, nullable=True)

    created_by = Column(String(36), nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )