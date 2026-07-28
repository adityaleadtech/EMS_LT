from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# REMOVE: from app.models.hierarchy.state import State


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    iso_code: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True
    )

    phone_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    currency: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    capital: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    region: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    sub_region: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    flag_url: Mapped[Optional[str]] = mapped_column(
        Text,
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

    # Relationships - Use string reference
    states: Mapped[List["State"]] = relationship(
        "State",  # String reference
        back_populates="country",
        cascade="all, delete-orphan"
    )