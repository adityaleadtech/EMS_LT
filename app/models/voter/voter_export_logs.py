# app/models/voter_export_log.py
from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class VoterExportLog(Base):
    __tablename__ = "voter_export_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    export_type = Column(String(50))
    filename = Column(String(255))
    total_records = Column(Integer, default=0)
    filter_criteria = Column(JSON)
    
    exported_by = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))
    exported_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    client = relationship("Client", foreign_keys=[client_id])
    exporter = relationship("ClientUser", foreign_keys=[exported_by])