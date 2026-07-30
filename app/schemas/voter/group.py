# app/schemas/voter/group.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class VoterGroupBase(BaseModel):
    client_id: str = Field(..., description="Client UUID")
    group_name: str = Field(..., description="Name of the group")
    group_description: Optional[str] = Field(None, description="Description of group")
    group_type: Optional[str] = Field("STATIC", description="STATIC, DYNAMIC, SMART")
    criteria: Optional[Dict[str, Any]] = Field(None, description="Criteria for dynamic groups")
    is_active: Optional[bool] = Field(True, description="Is group active")
    
    @validator('group_name')
    def validate_group_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Group name cannot be empty")
        return v.strip()
    
    @validator('group_type')
    def validate_group_type(cls, v):
        if v and v not in ['STATIC', 'DYNAMIC', 'SMART']:
            raise ValueError("Invalid group type")
        return v


class VoterGroupCreate(VoterGroupBase):
    created_by: Optional[str] = None


class VoterGroupUpdate(BaseModel):
    group_name: Optional[str] = None
    group_description: Optional[str] = None
    group_type: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class VoterGroupResponse(VoterGroupBase):
    id: str
    total_voters: int
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BulkGroupAddRequest(BaseModel):
    group_id: str
    voter_ids: List[str] = Field(..., description="List of voter UUIDs to add to group")
    added_by: Optional[str] = None


class BulkGroupRemoveRequest(BaseModel):
    group_id: str
    voter_ids: List[str]


class GroupOperationResult(BaseModel):
    added_count: Optional[int] = None
    removed_count: Optional[int] = None
    skipped_count: Optional[int] = None
    failed_count: int = 0
    errors: List[Dict[str, str]] = []