from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ==========================================================
# PERMISSION
# ==========================================================

class PermissionCreate(BaseModel):
    service_id: str
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


class PermissionResponse(BaseModel):
    service_id: str
    service_name: str
    service_code: str

    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool

    class Config:
        from_attributes = True


# ==========================================================
# CREATE
# ==========================================================

class ClientUserCreate(BaseModel):
    client_id: str

    full_name: str = Field(..., min_length=3, max_length=255)

    email: EmailStr

    phone: str = Field(..., min_length=10, max_length=15)

    password: str = Field(..., min_length=8)

    designation: Optional[str] = None

    permissions: List[PermissionCreate]


# ==========================================================
# UPDATE
# ==========================================================

class ClientUserUpdate(BaseModel):
    full_name: Optional[str] = None

    email: Optional[EmailStr] = None

    phone: Optional[str] = None

    designation: Optional[str] = None

    is_active: Optional[bool] = None

    permissions: Optional[List[PermissionCreate]] = None


# ==========================================================
# RESPONSE
# ==========================================================

class ClientUserResponse(BaseModel):
    id: str

    client_id: str

    full_name: str

    email: str

    phone: str

    designation: Optional[str]

    is_active: bool

    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True


# ==========================================================
# LIST RESPONSE
# ==========================================================

class ClientUserListResponse(BaseModel):
    total: int
    page: int
    limit: int

    users: List[ClientUserResponse]


# ==========================================================
# COUNT RESPONSE
# ==========================================================

class ClientUserCountResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int


# ==========================================================
# LOGIN
# ==========================================================

class ClientUserLogin(BaseModel):
    email: EmailStr

    password: str


class ClientUserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    user: ClientUserResponse


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ChangePassword(BaseModel):
    old_password: str

    new_password: str = Field(..., min_length=8)


class PermissionUpdateRequest(BaseModel):
    permissions: List[PermissionCreate]