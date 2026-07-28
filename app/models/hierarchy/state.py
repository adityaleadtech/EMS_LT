# app/models/hierarchy/state.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# NO imports of Country or PCDistrict here


class State(Base):
    __tablename__ = "states"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    country_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("countries.id", ondelete="CASCADE"),
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

    state_code: Mapped[Optional[str]] = mapped_column(
        String(10),
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

    area: Mapped[Optional[str]] = mapped_column(
        String(50),
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

    # Relationships - Use string references
    country: Mapped["Country"] = relationship(
        "Country",  # String reference
        back_populates="states"
    )

    pc_districts: Mapped[List["PCDistrict"]] = relationship(
        "PCDistrict",  # String reference
        back_populates="state",
        cascade="all, delete-orphan"
    )