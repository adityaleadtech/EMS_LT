import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.service import Service
from app.models.user_permission import UserPermission
from app.schemas.platform_users import (
    PlatformUserCreate,
    PlatformUserLogin,
    PlatformUserUpdate,
    PlatformUserChangePassword,
    PlatformUserResponse,
    PlatformUserListResponse,
)
from app.models.platform_users.platform_users import PlatformUser


class PlatformUserService:
    """Service class for Platform User operations"""

    @staticmethod
    def _validate_email(db: Session, email: str, exclude_user_id: Optional[str] = None):
        """
        Validate that email is unique
        
        Args:
            db: Database session
            email: Email to validate
            exclude_user_id: User ID to exclude from check (for updates)
        
        Raises:
            HTTPException: If email already exists
        """
        query = db.query(PlatformUser).filter(PlatformUser.email == email)
        
        if exclude_user_id:
            query = query.filter(PlatformUser.id != exclude_user_id)
        
        existing = query.first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )

    @staticmethod
    def _validate_employee_id(
        db: Session, 
        employee_id: Optional[str],
        exclude_user_id: Optional[str] = None
    ):
        """
        Validate that employee ID is unique
        
        Args:
            db: Database session
            employee_id: Employee ID to validate
            exclude_user_id: User ID to exclude from check (for updates)
        
        Raises:
            HTTPException: If employee ID already exists
        """
        if not employee_id:
            return

        query = db.query(PlatformUser).filter(
            PlatformUser.employee_id == employee_id
        )
        
        if exclude_user_id:
            query = query.filter(PlatformUser.id != exclude_user_id)
        
        existing = query.first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists."
            )

    @staticmethod
    def _validate_phone(
        db: Session, 
        phone: Optional[str],
        exclude_user_id: Optional[str] = None
    ):
        """
        Validate that phone number is unique
        
        Args:
            db: Database session
            phone: Phone number to validate
            exclude_user_id: User ID to exclude from check (for updates)
        
        Raises:
            HTTPException: If phone number already exists
        """
        if not phone:
            return

        query = db.query(PlatformUser).filter(
            PlatformUser.phone == phone
        )
        
        if exclude_user_id:
            query = query.filter(PlatformUser.id != exclude_user_id)
        
        existing = query.first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists."
            )

    @staticmethod
    def _create_permissions(
        db: Session,
        user_id: str,
        permissions: List[Dict[str, Any]],
    ):
        """
        Create permissions for a user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: List of permission dicts
        
        Raises:
            HTTPException: If service code is invalid
        """
        for permission in permissions:
            service = (
                db.query(Service)
                .filter(Service.service_code == permission.service_code)
                .first()
            )

            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invalid service code '{permission.service_code}'"
                )

            permission_row = UserPermission(
                id=str(uuid.uuid4()),
                user_type="PLATFORM_USER",
                user_id=user_id,
                service_id=service.id,
                can_create=permission.can_create,
                can_read=permission.can_read,
                can_update=permission.can_update,
                can_delete=permission.can_delete,
            )

            db.add(permission_row)

    @staticmethod
    def _replace_permissions(
        db: Session,
        user_id: str,
        permissions: List[Dict[str, Any]],
    ):
        """
        Replace all permissions for a user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: List of new permissions
        """
        # Delete existing permissions
        (
            db.query(UserPermission)
            .filter(
                UserPermission.user_type == "PLATFORM_USER",
                UserPermission.user_id == user_id,
            )
            .delete(synchronize_session=False)
        )

        # Create new permissions
        PlatformUserService._create_permissions(
            db=db,
            user_id=user_id,
            permissions=permissions,
        )

    @staticmethod
    def create_platform_user(
        db: Session,
        payload: PlatformUserCreate,
        created_by: str,
    ) -> PlatformUser:
        """
        Create a new platform user
        
        Args:
            db: Database session
            payload: User creation payload
            created_by: ID of user creating this user
        
        Returns:
            Created PlatformUser
        
        Raises:
            HTTPException: If validation fails or error occurs
        """
        try:
            # Validate email
            PlatformUserService._validate_email(db, payload.email)

            # Validate employee ID
            PlatformUserService._validate_employee_id(db, payload.employee_id)

            # Validate phone
            PlatformUserService._validate_phone(db, payload.phone)

            # Create user
            user = PlatformUser(
                id=str(uuid.uuid4()),
                full_name=payload.full_name,
                email=payload.email,
                password=hash_password(payload.password),
                phone=payload.phone,
                employee_id=payload.employee_id,
                profile_image=payload.profile_image,
                created_by=created_by,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(user)
            db.flush()

            # Create permissions if provided
            if payload.permissions:
                PlatformUserService._create_permissions(
                    db=db,
                    user_id=user.id,
                    permissions=payload.permissions,
                )

            db.commit()
            db.refresh(user)

            return user

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating platform user: {str(e)}",
            )

    @staticmethod
    def login(
        db: Session,
        payload: PlatformUserLogin,
    ) -> Dict[str, Any]:
        """
        Login a platform user
        
        Args:
            db: Database session
            payload: Login credentials
        
        Returns:
            Dict with access token and user data
        
        Raises:
            HTTPException: If credentials are invalid
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.email == payload.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support."
            )

        if not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Update last login
        user.last_login = datetime.now(timezone.utc)

        # Create access token
        token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "user_type": "PLATFORM_USER",
            }
        )

        db.commit()
        db.refresh(user)

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: str,
    ) -> PlatformUser:
        """
        Get platform user by ID
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            PlatformUser
        
        Raises:
            HTTPException: If user not found
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        return user

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> Optional[PlatformUser]:
        """
        Get platform user by email
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            PlatformUser or None
        """
        return (
            db.query(PlatformUser)
            .filter(PlatformUser.email == email)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PlatformUserListResponse:
        """
        Get all platform users with pagination, filtering, and search
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            is_active: Filter by active status
            search: Search term for name, email, or employee ID
        
        Returns:
            PlatformUserListResponse with pagination metadata
        """
        query = db.query(PlatformUser)

        # Apply filters
        if is_active is not None:
            query = query.filter(PlatformUser.is_active == is_active)

        # Apply search
        if search:
            query = query.filter(
                or_(
                    PlatformUser.full_name.ilike(f"%{search}%"),
                    PlatformUser.email.ilike(f"%{search}%"),
                    PlatformUser.employee_id.ilike(f"%{search}%"),
                    PlatformUser.phone.ilike(f"%{search}%"),
                )
            )

        total = query.count()

        users = (
            query.order_by(PlatformUser.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return PlatformUserListResponse(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
            items=users,
        )

    @staticmethod
    def update(
        db: Session,
        user_id: str,
        payload: PlatformUserUpdate,
    ) -> PlatformUser:
        """
        Update platform user
        
        Args:
            db: Database session
            user_id: User ID
            payload: Update payload
        
        Returns:
            Updated PlatformUser
        
        Raises:
            HTTPException: If user not found or validation fails
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        try:
            # Validate email if being updated
            if payload.email and payload.email != user.email:
                PlatformUserService._validate_email(
                    db, 
                    payload.email, 
                    exclude_user_id=user.id
                )

            # Validate employee ID if being updated
            if payload.employee_id and payload.employee_id != user.employee_id:
                PlatformUserService._validate_employee_id(
                    db,
                    payload.employee_id,
                    exclude_user_id=user.id
                )

            # Validate phone if being updated
            if payload.phone and payload.phone != user.phone:
                PlatformUserService._validate_phone(
                    db,
                    payload.phone,
                    exclude_user_id=user.id
                )

            # Update user fields
            update_data = payload.model_dump(
                exclude_unset=True,
                exclude={"permissions"},
            )

            for key, value in update_data.items():
                setattr(user, key, value)

            user.updated_at = datetime.now(timezone.utc)

            # Update permissions if provided
            if payload.permissions is not None:
                PlatformUserService._replace_permissions(
                    db=db,
                    user_id=user.id,
                    permissions=payload.permissions,
                )

            db.commit()
            db.refresh(user)

            return user

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating platform user: {str(e)}",
            )

    @staticmethod
    def delete(
        db: Session,
        user_id: str,
    ) -> Dict[str, str]:
        """
        Soft delete platform user (deactivate)
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If user not found or already inactive
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform User is already inactive."
            )

        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)

        db.commit()

        return {"message": "Platform User deleted successfully."}

    @staticmethod
    def restore(
        db: Session,
        user_id: str,
    ) -> PlatformUser:
        """
        Restore a soft-deleted platform user (reactivate)
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Restored PlatformUser
        
        Raises:
            HTTPException: If user not found or already active
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform User is already active."
            )

        user.is_active = True
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        payload: PlatformUserChangePassword,
    ) -> Dict[str, str]:
        """
        Change platform user password
        
        Args:
            db: Database session
            user_id: User ID
            payload: Password change payload
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If user not found or password validation fails
        """
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        # Verify current password
        if not verify_password(payload.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )

        # Check if new password is same as current
        if verify_password(payload.new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as the current password."
            )

        # Update password
        user.password = hash_password(payload.new_password)
        user.updated_at = datetime.now(timezone.utc)

        db.commit()

        return {"message": "Password changed successfully."}

    @staticmethod
    def get_permissions(
        db: Session,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get permissions for a platform user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            List of permissions with service details
        
        Raises:
            HTTPException: If user not found
        """
        # Verify user exists
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        # Get permissions with service details
        permissions = (
            db.query(UserPermission, Service)
            .join(Service, UserPermission.service_id == Service.id)
            .filter(
                UserPermission.user_type == "PLATFORM_USER",
                UserPermission.user_id == user_id,
            )
            .all()
        )

        result = []
        for permission, service in permissions:
            result.append({
                "service_code": service.service_code,
                "service_name": service.service_name,
                "can_create": permission.can_create,
                "can_read": permission.can_read,
                "can_update": permission.can_update,
                "can_delete": permission.can_delete,
            })

        return result

    @staticmethod
    def update_permissions(
        db: Session,
        user_id: str,
        permissions: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """
        Update permissions for a platform user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: New permissions list
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If user not found
        """
        # Verify user exists
        user = (
            db.query(PlatformUser)
            .filter(PlatformUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform User not found."
            )

        try:
            PlatformUserService._replace_permissions(
                db=db,
                user_id=user_id,
                permissions=permissions,
            )

            db.commit()

            return {"message": "Permissions updated successfully."}

        except HTTPException:
            db.rollback()
            raise

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating permissions: {str(e)}",
            )

    @staticmethod
    def count(
        db: Session,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count platform users with optional filters
        
        Args:
            db: Database session
            is_active: Filter by active status
            search: Search term
        
        Returns:
            Total count
        """
        query = db.query(PlatformUser)

        if is_active is not None:
            query = query.filter(PlatformUser.is_active == is_active)

        if search:
            query = query.filter(
                or_(
                    PlatformUser.full_name.ilike(f"%{search}%"),
                    PlatformUser.email.ilike(f"%{search}%"),
                    PlatformUser.employee_id.ilike(f"%{search}%"),
                    PlatformUser.phone.ilike(f"%{search}%"),
                )
            )

        return query.count()