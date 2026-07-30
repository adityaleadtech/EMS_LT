from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ClientService(Base):
    __tablename__ = "client_services"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
    )

    client_id = Column(
        String(36),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    service_id = Column(
        String(36),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ✅ ADDED: service_code for denormalization
    service_code = Column(
        String(50),
        nullable=True,
        index=True,
    )

    # ✅ ADDED: service_name for denormalization
    service_name = Column(
        String(255),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_by = Column(
        String(36),
        nullable=False,
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

    # Relationships
    client = relationship(
        "Client",
        back_populates="client_services",
    )

    service = relationship(
        "Service",
        back_populates="client_services",
    )