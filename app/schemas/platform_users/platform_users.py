from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# =====================================================
# Permission
# =====================================================

class PermissionCreate(BaseModel):
    service_code: str

    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


# =====================================================
# Base
# =====================================================

class PlatformUserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    profile_image: Optional[str] = None


# =====================================================
# Create
# =====================================================

class PlatformUserCreate(PlatformUserBase):
    password: str
    permissions: List[PermissionCreate] = []


# =====================================================
# Login
# =====================================================

class PlatformUserLogin(BaseModel):
    email: EmailStr
    password: str


# =====================================================
# Update
# =====================================================

class PlatformUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    profile_image: Optional[str] = None
    permissions: Optional[List[PermissionCreate]] = None


# =====================================================
# Change Password
# =====================================================

class PlatformUserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


# =====================================================
# Response
# =====================================================

class PlatformUserResponse(BaseModel):
    id: str

    full_name: str

    email: EmailStr

    phone: Optional[str] = None

    employee_id: Optional[str] = None

    profile_image: Optional[str] = None

    is_active: bool

    last_login: Optional[datetime] = None

    created_by: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================
# Login Response
# =====================================================

class PlatformUserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PlatformUserResponse


# =====================================================
# List Response
# =====================================================

class PlatformUserListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool
    items: List[PlatformUserResponse]