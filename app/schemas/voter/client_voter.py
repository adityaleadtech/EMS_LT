# app/schemas/voter/client_voter.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ClientVoterStats(BaseModel):
    total_voters: int
    by_vote_status: Dict[str, int]
    by_voter_status: Dict[str, int]
    by_caste: Dict[str, int]
    by_gender: Dict[str, int]
    by_booth: Dict[str, int]
    by_ac: Dict[str, int]
    last_updated: Optional[str] = None


class ClientVoterDataResponse(BaseModel):
    """Complete client voter response with all fields from JSON cache"""
    client_id: str
    client_code: str
    client_name: str
    total_voters: int
    last_updated: str
    voters: Dict[str, Any]  # voter_id -> full voter data
    stats: Optional[ClientVoterStats] = None


class AssignVotersRequest(BaseModel):
    voter_ids: List[str] = Field(..., description="List of voter UUIDs to assign")
    assigned_by: Optional[str] = Field(None, description="User who is assigning")


class AssignVotersResponse(BaseModel):
    assigned_count: int
    skipped_duplicates: int
    failed_count: int
    errors: Optional[List[Dict[str, str]]] = None


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete voters from client"""
    voter_ids: List[str] = Field(..., description="List of voter IDs to delete")


class ClientVoterResponse(BaseModel):
    """Single voter response with all fields for a client"""
    id: str
    voter_id: str
    ac_no: Optional[str] = None
    ac_name: Optional[str] = None
    assembly_id: Optional[str] = None
    booth_no: Optional[str] = None
    booth_name_english: Optional[str] = None
    booth_name_other: Optional[str] = None
    booth_id: Optional[str] = None
    panchayat_ward_id: Optional[str] = None
    pc_district_id: Optional[str] = None
    section_no: Optional[str] = None
    section_name_english: Optional[str] = None
    section_name_other: Optional[str] = None
    sno: Optional[str] = None
    name_english: Optional[str] = None
    name_other: Optional[str] = None
    relation_type: Optional[str] = None
    relation_name_english: Optional[str] = None
    relation_name_other: Optional[str] = None
    gender: Optional[str] = None
    house_no_english: Optional[str] = None
    house_no_other: Optional[str] = None
    age: Optional[int] = None
    
    # Additional Info (Client-Specific)
    caste: Optional[str] = None
    mobile: Optional[str] = None
    voter_status: Optional[str] = None
    designation: Optional[str] = None
    vote_status: Optional[str] = None
    client_code: Optional[str] = None
    remarks: Optional[str] = None
    
    # Client Metadata
    client_id: str
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime