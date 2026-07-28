from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import enum

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, Text, DECIMAL, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class PollingStationType(str, enum.Enum):
    PERMANENT = "Permanent"
    TEMPORARY = "Temporary"
    MOBILE = "Mobile"


class PollingBooth(Base):
    __tablename__ = "polling_booths"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    panchayat_ward_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("panchayat_wards.id", ondelete="CASCADE"),
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

    booth_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    latitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(10, 8),
        nullable=True
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        DECIMAL(11, 8),
        nullable=True
    )

    polling_station_type: Mapped[PollingStationType] = mapped_column(
        Enum(PollingStationType),
        default=PollingStationType.PERMANENT,
        nullable=False
    )

    capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    facilities: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    is_accessible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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
    panchayat_ward: Mapped["PanchayatWard"] = relationship(
        "PanchayatWard",
        back_populates="polling_booths"
    )