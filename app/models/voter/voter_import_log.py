# app/models/voter/voter_import_log.py
from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid


class VoterImportLog(Base):
    __tablename__ = "voter_import_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(255))
    total_records = Column(Integer, default=0)
    inserted_records = Column(Integer, default=0)
    updated_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    errors = Column(Text)
    import_data = Column(JSON)
    
    imported_by = Column(String(36), ForeignKey("client_users.id", ondelete="SET NULL"))
    imported_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # ========== RELATIONSHIPS ==========
    client = relationship(
        "Client",  # ✅ String reference
        foreign_keys=[client_id]
    )
    importer = relationship(
        "ClientUser",  # ✅ String reference
        foreign_keys=[imported_by]
    )