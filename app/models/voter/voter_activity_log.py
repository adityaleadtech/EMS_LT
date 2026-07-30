# app/models/voter_activity_log.py
from sqlalchemy import Column, String, TIMESTAMP, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class VoterActivityLog(Base):
    __tablename__ = "voter_activity_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    voter_id = Column(String(36), ForeignKey("voter_master.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))
    
    activity_type = Column(String(50))
    activity_description = Column(Text)
    
    # Additional Data
    activity_data = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    
    # Timestamp
    performed_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    voter = relationship("VoterMaster", back_populates="activities")
    client = relationship("Client", foreign_keys=[client_id])
    user = relationship("ClientUser", foreign_keys=[user_id])