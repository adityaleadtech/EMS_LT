from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    assembly_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assemblies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    block_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    block_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    area: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    assembly: Mapped["Assembly"] = relationship(
        "Assembly",
        back_populates="blocks"
    )

    panchayat_wards: Mapped[List["PanchayatWard"]] = relationship(
        "PanchayatWard",
        back_populates="block",
        cascade="all, delete-orphan"
    )