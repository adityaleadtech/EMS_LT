# app/models/hierarchy/assembly.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# ❌ REMOVE any imports like:
# from app.models.hierarchy.pc_district import PCDistrict
# from app.models.hierarchy.state import State


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

    # ... other fields ...

    # ✅ Relationships - Use string references
    pc_district: Mapped["PCDistrict"] = relationship(
        "PCDistrict",  # String reference
        back_populates="assemblies"
    )