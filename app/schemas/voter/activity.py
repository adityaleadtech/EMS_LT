# app/schemas/voter/activity.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ActivityType:
    IMPORTED = "IMPORTED"
    ASSIGNED = "ASSIGNED"
    CONTACTED = "CONTACTED"
    VOTED = "VOTED"
    UPDATED = "UPDATED"
    REMOVED = "REMOVED"
    EXPORTED = "EXPORTED"
    GROUP_ADDED = "GROUP_ADDED"
    GROUP_REMOVED = "GROUP_REMOVED"
    BULK_UPDATED = "BULK_UPDATED"


class VoterActivityBase(BaseModel):
    voter_id: str = Field(..., description="Voter UUID")
    client_id: str = Field(..., description="Client UUID")
    user_id: Optional[str] = Field(None, description="User who performed action")
    activity_type: str = Field(..., description="Type of activity")
    activity_description: Optional[str] = Field(None, description="Description of activity")
    activity_data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    ip_address: Optional[str] = Field(None, description="IP address of user")
    user_agent: Optional[str] = Field(None, description="User agent of browser")


class VoterActivityCreate(VoterActivityBase):
    pass


class VoterActivityResponse(VoterActivityBase):
    id: str
    performed_at: datetime
    
    class Config:
        from_attributes = True