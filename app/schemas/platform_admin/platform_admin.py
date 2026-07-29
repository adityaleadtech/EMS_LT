from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================================
# Base Schema
# ==========================================================

class PlatformAdminBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    profile_image: Optional[str] = None


# ==========================================================
# Create
# ==========================================================

class PlatformAdminCreate(PlatformAdminBase):
    password: str = Field(..., min_length=8, max_length=100)


# ==========================================================
# Login
# ==========================================================

class PlatformAdminLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================================================
# Update
# ==========================================================

class PlatformAdminUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    profile_image: Optional[str] = None


# ==========================================================
# Change Password
# ==========================================================

class PlatformAdminChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)


# ==========================================================
# Response
# ==========================================================

class PlatformAdminResponse(PlatformAdminBase):
    id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Login Response
# ==========================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: PlatformAdminResponse


# ==========================================================
# List Response
# ==========================================================

class PlatformAdminListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool
    items: List[PlatformAdminResponse]