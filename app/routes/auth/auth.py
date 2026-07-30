from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth.auth import LoginRequest, LoginResponse
from app.services.auth.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Unified Login",
    description="Login as Platform Admin, Platform User, Client Admin, or Client User"
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Unified login endpoint.
    
    Checks in order:
    1. Platform Admin
    2. Platform User
    3. Client Admin
    4. Client User
    """
    return AuthService.login(db, payload)