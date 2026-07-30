from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.models.platform_users.platform_users import PlatformUser
from app.models.client_admin.client_admin import ClientAdmin
from app.models.client_users.client_users import ClientUser
from app.schemas.auth.auth import LoginRequest, LoginResponse


class AuthService:
    """Unified Authentication Service"""

    @staticmethod
    def _get_user_response(user, user_type: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Build user response dict"""
        response = {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
        }
        
        # Add phone if exists
        if hasattr(user, "phone"):
            response["phone"] = user.phone
        
        # Add client_id if exists
        if hasattr(user, "client_id") and user.client_id:
            response["client_id"] = user.client_id
        
        # Add employee_id if exists (for platform users)
        if hasattr(user, "employee_id") and user.employee_id:
            response["employee_id"] = user.employee_id
        
        # Add designation if exists (for client users)
        if hasattr(user, "designation") and user.designation:
            response["designation"] = user.designation
        
        # Add profile_image if exists
        if hasattr(user, "profile_image") and user.profile_image:
            response["profile_image"] = user.profile_image
        
        # Add is_active
        response["is_active"] = user.is_active
        
        return response

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> LoginResponse:
        """
        Unified login - checks all user types in order:
        1. Platform Admin
        2. Platform User
        3. Client Admin
        4. Client User
        """
        
        # ============================================================
        # 1. Check Platform Admin
        # ============================================================
        platform_admin = (
            db.query(PlatformAdmin)
            .filter(PlatformAdmin.email == payload.email)
            .first()
        )
        
        if platform_admin:
            # Verify password
            if not verify_password(payload.password, platform_admin.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password."
                )
            
            # Check active status
            if not platform_admin.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive. Please contact support."
                )
            
            # Update last login
            from datetime import datetime, timezone
            platform_admin.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create token
            access_token = create_access_token({
                "sub": str(platform_admin.id),
                "email": platform_admin.email,
                "user_type": "PLATFORM_ADMIN",
                "client_id": None,
            })
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user_type="PLATFORM_ADMIN",
                user=AuthService._get_user_response(platform_admin, "PLATFORM_ADMIN"),
                client_id=None,
            )
        
        # ============================================================
        # 2. Check Platform User
        # ============================================================
        platform_user = (
            db.query(PlatformUser)
            .filter(PlatformUser.email == payload.email)
            .first()
        )
        
        if platform_user:
            # Verify password
            if not verify_password(payload.password, platform_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password."
                )
            
            # Check active status
            if not platform_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive. Please contact support."
                )
            
            # Update last login
            from datetime import datetime, timezone
            platform_user.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create token
            access_token = create_access_token({
                "sub": str(platform_user.id),
                "email": platform_user.email,
                "user_type": "PLATFORM_USER",
                "client_id": None,
            })
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user_type="PLATFORM_USER",
                user=AuthService._get_user_response(platform_user, "PLATFORM_USER"),
                client_id=None,
            )
        
        # ============================================================
        # 3. Check Client Admin
        # ============================================================
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.email == payload.email)
            .first()
        )
        
        if client_admin:
            # Verify password
            if not verify_password(payload.password, client_admin.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password."
                )
            
            # Check active status
            if not client_admin.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive. Please contact support."
                )
            
            # Update last login
            from datetime import datetime, timezone
            client_admin.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create token
            access_token = create_access_token({
                "sub": str(client_admin.id),
                "email": client_admin.email,
                "user_type": "CLIENT_ADMIN",
                "client_id": client_admin.client_id,
            })
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user_type="CLIENT_ADMIN",
                user=AuthService._get_user_response(client_admin, "CLIENT_ADMIN"),
                client_id=client_admin.client_id,
            )
        
        # ============================================================
        # 4. Check Client User
        # ============================================================
        client_user = (
            db.query(ClientUser)
            .filter(ClientUser.email == payload.email)
            .first()
        )
        
        if client_user:
            # Verify password
            if not verify_password(payload.password, client_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password."
                )
            
            # Check active status
            if not client_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive. Please contact support."
                )
            
            # Update last login
            from datetime import datetime, timezone
            client_user.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create token
            access_token = create_access_token({
                "sub": str(client_user.id),
                "email": client_user.email,
                "user_type": "CLIENT_USER",
                "client_id": client_user.client_id,
            })
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user_type="CLIENT_USER",
                user=AuthService._get_user_response(client_user, "CLIENT_USER"),
                client_id=client_user.client_id,
            )
        
        # ============================================================
        # 5. No user found
        # ============================================================
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )