# app/models/voter_group_mapping.py
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class VoterGroupMapping(Base):
    __tablename__ = "voter_group_mapping"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey("voter_group_master.id", ondelete="CASCADE"), nullable=False)
    voter_id = Column(String(36), ForeignKey("voter_master.id", ondelete="CASCADE"), nullable=False)
    
    added_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    added_by = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))

    # Relationships
    group = relationship("VoterGroupMaster", back_populates="mappings")
    voter = relationship("VoterMaster", back_populates="group_mappings")
    adder = relationship("ClientUser", foreign_keys=[added_by])

    __table_args__ = (
        UniqueConstraint("group_id", "voter_id", name="uk_group_voter"),
    )