# app/models/voter/voter_additional_info.py
from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

# ========== CORRECT IMPORTS ==========
from app.models.client.client import Client


class VoterAdditionalInfo(Base):
    __tablename__ = "voter_additional_info"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    voter_id = Column(String(36), ForeignKey("voter_master.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    client_code = Column(String(50), nullable=False, index=True)
    
    # Additional Fields from Excel
    caste = Column(String(50))
    mobile = Column(String(15), index=True)
    voter_status = Column(String(20))
    designation = Column(String(100))
    vote_status = Column(String(20))
    
    # Extra fields
    remarks = Column(Text)
    updated_by = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # ========== RELATIONSHIPS ==========
    voter = relationship("VoterMaster", back_populates="additional_info")
    client = relationship(
        "Client",  # ✅ String reference
        foreign_keys=[client_id]
    )
    updated_by_user = relationship(
        "ClientUser",  # ✅ String reference
        foreign_keys=[updated_by]
    )

    __table_args__ = (
        UniqueConstraint("voter_id", "client_id", name="uk_voter_client"),
    )