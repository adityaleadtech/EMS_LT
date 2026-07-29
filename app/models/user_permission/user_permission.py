from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)

from app.core.database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id = Column(String(36), primary_key=True, index=True)

    user_type = Column(String(30), nullable=False)

    user_id = Column(String(36), nullable=False, index=True)

    service_id = Column(
        String(36),
        ForeignKey("services.id"),
        nullable=False,
    )

    can_create = Column(Boolean, default=False)

    can_read = Column(Boolean, default=False)

    can_update = Column(Boolean, default=False)

    can_delete = Column(Boolean, default=False)

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