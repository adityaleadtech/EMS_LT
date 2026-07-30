from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ClientUser(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)

    client_id = Column(
        String(36),
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )

    full_name = Column(
        String(255),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    phone = Column(
        String(20),
        unique=True,
        nullable=False,
    )

    password = Column(
        String(255),
        nullable=False,
    )

    designation = Column(
        String(150),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    client = relationship(
        "Client",
        back_populates="users",
    )