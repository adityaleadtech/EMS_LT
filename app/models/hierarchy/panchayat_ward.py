from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, DECIMAL, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PanchayatWard(Base):
    __tablename__ = "panchayat_wards"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    block_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("blocks.id", ondelete="CASCADE"),
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

    ward_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    ward_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    population: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    area: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True
    )

    pincode: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True
    )

    latitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 8),
        nullable=True
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(11, 8),
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
    block: Mapped["Block"] = relationship(
        "Block",
        back_populates="panchayat_wards"
    )

    polling_booths: Mapped[List["PollingBooth"]] = relationship(
        "PollingBooth",
        back_populates="panchayat_ward",
        cascade="all, delete-orphan"
    )