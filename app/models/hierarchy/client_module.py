from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClientModule(Base):
    __tablename__ = "client_modules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    client_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    module_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    assigned_by: Mapped[str] = mapped_column(
        String(36),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )