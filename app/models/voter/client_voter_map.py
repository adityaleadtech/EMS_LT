# app/models/voter/client_voter_map.py
from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
from sqlalchemy.ext.mutable import MutableDict
import uuid


class ClientVoterMap(Base):
    __tablename__ = "client_voter_map"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # JSON Column for Combined Voter Data
    voter_data = Column(MutableDict.as_mutable(JSON), default={})
    
    # Metadata
    version = Column(String(20), default="1.0")
    total_voters = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # ========== RELATIONSHIPS ==========
    client = relationship(
        "Client",  # ✅ String reference
        foreign_keys=[client_id]
    )