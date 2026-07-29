from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================================
# Create Client Admin
# ==========================================================

class ClientAdminCreate(BaseModel):
    client_id: str

    full_name: str

    email: EmailStr

    password: str

    phone: str

    employee_id: Optional[str] = None

    profile_image: Optional[str] = None


# ==========================================================
# Login
# ==========================================================

class ClientAdminLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================================================
# Update Client Admin
# ==========================================================

class ClientAdminUpdate(BaseModel):
    full_name: Optional[str] = None

    email: Optional[EmailStr] = None

    phone: Optional[str] = None

    employee_id: Optional[str] = None

    profile_image: Optional[str] = None

    is_active: Optional[bool] = None


# ==========================================================
# Change Password
# ==========================================================

class ClientAdminChangePassword(BaseModel):
    current_password: str
    new_password: str


# ==========================================================
# Response
# ==========================================================

class ClientAdminResponse(BaseModel):
    id: str

    client_id: str

    full_name: str

    email: EmailStr

    phone: str

    employee_id: Optional[str] = None

    profile_image: Optional[str] = None

    is_active: bool

    last_login: Optional[datetime] = None

    created_by: str

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Login Response
# ==========================================================

class ClientAdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    user: ClientAdminResponse


# ==========================================================
# List Response
# ==========================================================

class ClientAdminListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool

    items: List[ClientAdminResponse]


# ==========================================================
# Count Response
# ==========================================================

class ClientAdminCountResponse(BaseModel):
    total: int