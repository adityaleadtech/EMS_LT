from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================================
# CREATE CLIENT ADMIN
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
# UPDATE CLIENT ADMIN
# ==========================================================
from typing import List


class ClientAdminListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool
    items: List[ClientAdminResponse]


class ClientAdminCountResponse(BaseModel):
    total: int

class ClientAdminUpdate(BaseModel):
    full_name: Optional[str] = None

    email: Optional[EmailStr] = None

    phone: Optional[str] = None

    employee_id: Optional[str] = None

    profile_image: Optional[str] = None

    is_active: Optional[bool] = None


# ==========================================================
# LOGIN
# ==========================================================

class ClientAdminLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

class ClientAdminChangePassword(BaseModel):
    current_password: str
    new_password: str


# ==========================================================
# CLIENT ADMIN RESPONSE
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
# CLIENT ADMIN LIST RESPONSE
# ==========================================================

class ClientAdminListResponse(BaseModel):
    total: int

    skip: int

    limit: int

    has_more: bool

    items: List[ClientAdminResponse]


# ==========================================================
# CLIENT ADMIN COUNT RESPONSE
# ==========================================================

class ClientAdminCountResponse(BaseModel):
    total: int


# ==========================================================
# LOGIN RESPONSE
# ==========================================================

class ClientAdminLoginResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"

    user: ClientAdminResponse