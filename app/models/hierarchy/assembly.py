from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Assembly(Base):
    __tablename__ = "assemblies"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    pc_district_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("pc_districts.id", ondelete="CASCADE"),
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

    assembly_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    constituency_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    population: Mapped[Optional[str]] = mapped_column(
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
    pc_district: Mapped["PCDistrict"] = relationship(
        "PCDistrict",
        back_populates="assemblies"
    )

    blocks: Mapped[List["Block"]] = relationship(
        "Block",
        back_populates="assembly",
        cascade="all, delete-orphan"
    )