from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================================
# Client Ministry
# ==========================================================

class ClientMinistryUpdate(BaseModel):
    ministries: List[str]


class ClientMinistryResponse(BaseModel):
    id: str
    ministry_name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Create Client
# ==========================================================

class ClientCreate(BaseModel):
    client_code: str
    client_name: str

    party: str

    email: EmailStr
    phone: str

    is_mp: bool = False
    is_mla: bool = False
    is_minister: bool = False
    is_party_president: bool = False

    constituency: Optional[str] = None

    office_address: Optional[str] = None

    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None

    office_logo: Optional[str] = None
    office_banner: Optional[str] = None

    description: Optional[str] = None

    ministries: List[str] = []


# ==========================================================
# Update Client
# ==========================================================

class ClientUpdate(BaseModel):
    client_code: Optional[str] = None
    client_name: Optional[str] = None

    party: Optional[str] = None

    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    is_mp: Optional[bool] = None
    is_mla: Optional[bool] = None
    is_minister: Optional[bool] = None
    is_party_president: Optional[bool] = None

    constituency: Optional[str] = None

    office_address: Optional[str] = None

    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None

    office_logo: Optional[str] = None
    office_banner: Optional[str] = None

    description: Optional[str] = None

    ministries: Optional[List[str]] = None


# ==========================================================
# Client Response
# ==========================================================

class ClientResponse(BaseModel):
    id: str

    client_code: str
    client_name: str

    party: str

    email: EmailStr
    phone: str

    is_mp: bool
    is_mla: bool
    is_minister: bool
    is_party_president: bool

    constituency: Optional[str] = None

    office_address: Optional[str] = None

    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None

    office_logo: Optional[str] = None
    office_banner: Optional[str] = None

    description: Optional[str] = None

    is_active: bool

    created_by: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Client List Response
# ==========================================================

class ClientListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool
    items: List[ClientResponse]


# ==========================================================
# Client Count Response
# ==========================================================

class ClientCountResponse(BaseModel):
    total: int