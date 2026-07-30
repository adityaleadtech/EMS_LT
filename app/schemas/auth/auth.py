from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    user: Dict[str, Any]
    client_id: Optional[str] = None

    class Config:
        from_attributes = True