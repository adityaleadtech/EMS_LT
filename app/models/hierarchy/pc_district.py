# app/models/hierarchy/pc_district.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# ❌ REMOVE these imports:
# from app.modules.hierarchy.assembly import Assembly
# from app.modules.hierarchy.state import State


class PCDistrict(Base):
    __tablename__ = "pc_districts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    state_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("states.id", ondelete="CASCADE"),
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

    district_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    total_assemblies: Mapped[Optional[int]] = mapped_column(
        Integer,
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

    district_type: Mapped[Optional[str]] = mapped_column(
        String(20),
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

    # ✅ Relationships - Use string references (NO imports needed)
    state: Mapped["State"] = relationship(
        "State",  # String reference
        back_populates="pc_districts"
    )

    assemblies: Mapped[List["Assembly"]] = relationship(
        "Assembly",  # String reference
        back_populates="pc_district",
        cascade="all, delete-orphan"
    )