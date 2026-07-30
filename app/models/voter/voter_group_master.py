# app/models/voter/voter_group_master.py
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid


class VoterGroupMaster(Base):
    __tablename__ = "voter_group_master"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    group_name = Column(String(200), nullable=False)
    group_description = Column(Text)
    group_type = Column(String(20), default="STATIC")
    criteria = Column(JSON)
    total_voters = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_by = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # ========== RELATIONSHIPS ==========
    client = relationship(
        "Client",  # ✅ String reference
        foreign_keys=[client_id]
    )
    creator = relationship(
        "ClientUser",  # ✅ String reference
        foreign_keys=[created_by]
    )
    mappings = relationship(
        "VoterGroupMapping",
        back_populates="group",
        cascade="all, delete-orphan"
    )