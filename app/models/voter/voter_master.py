# app/models/voter/voter_master.py
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

# ========== CORRECT IMPORTS ==========
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.polling_booth import PollingBooth
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.models.hierarchy.pc_district import PCDistrict
from app.models.client.client import Client


class VoterMaster(Base):
    __tablename__ = "voter_master"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    voter_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # AC Info (Foreign Key to assemblies)
    assembly_id = Column(String(36), ForeignKey("assemblies.id", ondelete="SET NULL"))
    ac_no = Column(String(50))
    ac_name = Column(String(200))
    
    # Booth Info (Foreign Key to polling_booths)
    booth_id = Column(String(36), ForeignKey("polling_booths.id", ondelete="SET NULL"))
    booth_no = Column(String(50))
    booth_name_other = Column(String(200))
    booth_name_english = Column(String(200))
    
    # Panchayat Ward (Foreign Key to panchayat_wards)
    panchayat_ward_id = Column(String(36), ForeignKey("panchayat_wards.id", ondelete="SET NULL"))
    
    # PC District (Foreign Key to pc_districts)
    pc_district_id = Column(String(36), ForeignKey("pc_districts.id", ondelete="SET NULL"))
    
    # Section Info
    section_no = Column(String(50))
    section_name_other = Column(String(200))
    section_name_english = Column(String(200))
    
    # Voter Info
    sno = Column(String(50))
    name_other = Column(String(200))
    name_english = Column(String(200), index=True)
    relation_type = Column(String(10))
    relation_name_other = Column(String(200))
    relation_name_english = Column(String(200))
    gender = Column(String(10))
    house_no_other = Column(String(100))
    house_no_english = Column(String(100))
    age = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # ========== RELATIONSHIPS - Use string references to avoid circular imports ==========
    assembly = relationship(
        "Assembly",
        foreign_keys=[assembly_id],
        lazy="select"
    )
    booth = relationship(
        "PollingBooth",
        foreign_keys=[booth_id],
        lazy="select"
    )
    panchayat_ward = relationship(
        "PanchayatWard",
        foreign_keys=[panchayat_ward_id],
        lazy="select"
    )
    pc_district = relationship(
        "PCDistrict",
        foreign_keys=[pc_district_id],
        lazy="select"
    )
    
    # Relationships to voter tables (same folder)
    additional_info = relationship(
        "VoterAdditionalInfo",
        back_populates="voter",
        cascade="all, delete-orphan",
        lazy="select"
    )
    activities = relationship(
        "VoterActivityLog",
        back_populates="voter",
        cascade="all, delete-orphan",
        lazy="select"
    )
    group_mappings = relationship(
        "VoterGroupMapping",
        back_populates="voter",
        cascade="all, delete-orphan",
        lazy="select"
    )