# app/schemas/voter/voter.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============ Voter Master Schemas ============

class VoterMasterBase(BaseModel):
    voter_id: str = Field(..., description="Unique voter ID from election commission")
    ac_no: Optional[str] = Field(None, description="Assembly constituency number")
    ac_name: Optional[str] = Field(None, description="Assembly constituency name")
    assembly_id: Optional[str] = Field(None, description="Assembly UUID from assemblies table")
    booth_no: Optional[str] = Field(None, description="Booth number")
    booth_name_other: Optional[str] = Field(None, description="Booth name in other language")
    booth_name_english: Optional[str] = Field(None, description="Booth name in English")
    booth_id: Optional[str] = Field(None, description="Booth UUID from polling_booths table")
    panchayat_ward_id: Optional[str] = Field(None, description="Panchayat ward UUID")
    pc_district_id: Optional[str] = Field(None, description="PC district UUID")
    section_no: Optional[str] = Field(None, description="Section number")
    section_name_other: Optional[str] = Field(None, description="Section name in other language")
    section_name_english: Optional[str] = Field(None, description="Section name in English")
    sno: Optional[str] = Field(None, description="Serial number in voter list")
    name_other: Optional[str] = Field(None, description="Name in other language")
    name_english: Optional[str] = Field(None, description="Name in English")
    relation_type: Optional[str] = Field(None, description="Relation type: H/F/M/S/D etc.")
    relation_name_other: Optional[str] = Field(None, description="Relation name in other language")
    relation_name_english: Optional[str] = Field(None, description="Relation name in English")
    gender: Optional[str] = Field(None, description="Gender: M/F/O")
    house_no_other: Optional[str] = Field(None, description="House number in other language")
    house_no_english: Optional[str] = Field(None, description="House number in English")
    age: Optional[int] = Field(None, description="Age of voter")
    is_active: Optional[bool] = Field(True, description="Is voter active")

    @validator('voter_id')
    def validate_voter_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Voter ID cannot be empty")
        return v.strip()
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 18 or v > 120):
            raise ValueError("Age must be between 18 and 120")
        return v


class VoterMasterCreate(VoterMasterBase):
    pass


class VoterMasterUpdate(BaseModel):
    ac_no: Optional[str] = None
    ac_name: Optional[str] = None
    assembly_id: Optional[str] = None
    booth_no: Optional[str] = None
    booth_name_other: Optional[str] = None
    booth_name_english: Optional[str] = None
    booth_id: Optional[str] = None
    panchayat_ward_id: Optional[str] = None
    pc_district_id: Optional[str] = None
    section_no: Optional[str] = None
    section_name_other: Optional[str] = None
    section_name_english: Optional[str] = None
    sno: Optional[str] = None
    name_other: Optional[str] = None
    name_english: Optional[str] = None
    relation_type: Optional[str] = None
    relation_name_other: Optional[str] = None
    relation_name_english: Optional[str] = None
    gender: Optional[str] = None
    house_no_other: Optional[str] = None
    house_no_english: Optional[str] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None


class VoterMasterResponse(VoterMasterBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Voter Additional Info Schemas ============

class VoterAdditionalInfoBase(BaseModel):
    client_code: str = Field(..., description="Client code")
    caste: Optional[str] = Field(None, description="Caste of voter")
    mobile: Optional[str] = Field(None, description="Mobile number")
    voter_status: Optional[str] = Field(None, description="Voter status: Voted/Not Voted/Pending")
    designation: Optional[str] = Field(None, description="Designation of voter")
    vote_status: Optional[str] = Field(None, description="Vote status: Favor/Not Favor/Neutral")
    remarks: Optional[str] = Field(None, description="Additional remarks")
    is_active: Optional[bool] = Field(True, description="Is active")

    @validator('mobile')
    def validate_mobile(cls, v):
        if v and not re.match(r'^[0-9]{10}$', v):
            raise ValueError("Mobile number must be 10 digits")
        return v
    
    @validator('voter_status')
    def validate_voter_status(cls, v):
        if v and v not in ['Voted', 'Not Voted', 'Pending', 'Absent', 'Rejected']:
            raise ValueError("Invalid voter status")
        return v
    
    @validator('vote_status')
    def validate_vote_status(cls, v):
        if v and v not in ['Favor', 'Not Favor', 'Neutral', 'Undecided', 'Not Contacted']:
            raise ValueError("Invalid vote status")
        return v


class VoterAdditionalInfoCreate(VoterAdditionalInfoBase):
    voter_id: str = Field(..., description="Voter UUID")
    client_id: str = Field(..., description="Client UUID")


class VoterAdditionalInfoUpdate(VoterAdditionalInfoBase):
    pass


class VoterAdditionalInfoResponse(VoterAdditionalInfoBase):
    id: str
    voter_id: str
    client_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Combined Voter Response Schemas ============

class VoterWithAdditionalInfo(BaseModel):
    """Complete voter data with additional info for a specific client"""
    voter: VoterMasterResponse
    additional_info: Optional[VoterAdditionalInfoResponse] = None


class VoterFullResponse(BaseModel):
    """Full voter response with all details and relations"""
    id: str
    voter_id: str
    ac_no: Optional[str]
    ac_name: Optional[str]
    assembly_id: Optional[str]
    assembly: Optional[Dict[str, Any]]
    booth_no: Optional[str]
    booth_name_english: Optional[str]
    booth_name_other: Optional[str]
    booth_id: Optional[str]
    booth: Optional[Dict[str, Any]]
    panchayat_ward_id: Optional[str]
    panchayat_ward: Optional[Dict[str, Any]]
    pc_district_id: Optional[str]
    pc_district: Optional[Dict[str, Any]]
    section_no: Optional[str]
    section_name_english: Optional[str]
    section_name_other: Optional[str]
    sno: Optional[str]
    name_english: Optional[str]
    name_other: Optional[str]
    relation_type: Optional[str]
    relation_name_english: Optional[str]
    relation_name_other: Optional[str]
    gender: Optional[str]
    house_no_english: Optional[str]
    house_no_other: Optional[str]
    age: Optional[int]
    additional_info: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Search/Filter Schemas ============

class VoterSearchParams(BaseModel):
    # Text Search
    search: Optional[str] = None
    voter_id: Optional[str] = None
    name_english: Optional[str] = None
    name_other: Optional[str] = None
    relation_name_english: Optional[str] = None
    relation_name_other: Optional[str] = None
    ac_no: Optional[str] = None
    ac_name: Optional[str] = None
    booth_no: Optional[str] = None
    booth_name_english: Optional[str] = None
    booth_name_other: Optional[str] = None
    section_no: Optional[str] = None
    section_name_english: Optional[str] = None
    section_name_other: Optional[str] = None
    sno: Optional[str] = None
    house_no_english: Optional[str] = None
    house_no_other: Optional[str] = None
    relation_type: Optional[str] = None
    gender: Optional[str] = None
    
    # Additional Info Filters
    caste: Optional[str] = None
    mobile: Optional[str] = None
    voter_status: Optional[str] = None
    designation: Optional[str] = None
    vote_status: Optional[str] = None
    client_code: Optional[str] = None
    
    # Range Filters
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    
    # Client Filter
    client_id: Optional[str] = None
    
    # Boolean Filters
    is_active: Optional[bool] = True
    has_additional_info: Optional[bool] = None
    is_voted: Optional[bool] = None
    
    # Sorting
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    
    # Pagination
    skip: int = 0
    limit: int = 100
    
    class Config:
        from_attributes = True


class VoterListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    voters: List[VoterFullResponse]