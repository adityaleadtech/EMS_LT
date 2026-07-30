import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.models.client.client import Client
from app.models.client_users.client_users import ClientUser
from app.models.client_services.client_services import ClientService
from app.models.service.service import Service
from app.models.user_permission.user_permission import UserPermission

from app.schemas.client_user.client_user import (
    ClientUserCreate,
    ClientUserUpdate,
    ClientUserLogin,
    ClientUserResponse,
    ClientUserLoginResponse,
    ClientUserListResponse,
    PermissionResponse,
)


class ClientUserService:
    """Service class for Client User operations"""

    # ==================== VALIDATION HELPERS ====================

    @staticmethod
    def _validate_client(
        db: Session,
        client_id: str,
    ) -> Client:
        """
        Validate that client exists and is active
        
        Args:
            db: Database session
            client_id: Client ID
        
        Returns:
            Client object
        
        Raises:
            HTTPException: If client not found or inactive
        """
        client = (
            db.query(Client)
            .filter(
                Client.id == client_id,
                Client.is_active == True,
            )
            .first()
        )

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found."
            )

        return client

    @staticmethod
    def _validate_email(
        db: Session,
        email: str,
        exclude_id: Optional[str] = None,
    ):
        """
        Validate that email is unique
        
        Args:
            db: Database session
            email: Email to validate
            exclude_id: User ID to exclude from check
        
        Raises:
            HTTPException: If email already exists
        """
        query = db.query(ClientUser).filter(ClientUser.email == email)

        if exclude_id:
            query = query.filter(ClientUser.id != exclude_id)

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists."
            )

    @staticmethod
    def _validate_phone(
        db: Session,
        phone: str,
        exclude_id: Optional[str] = None,
    ):
        """
        Validate that phone number is unique
        
        Args:
            db: Database session
            phone: Phone number to validate
            exclude_id: User ID to exclude from check
        
        Raises:
            HTTPException: If phone number already exists
        """
        query = db.query(ClientUser).filter(ClientUser.phone == phone)

        if exclude_id:
            query = query.filter(ClientUser.id != exclude_id)

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists."
            )

    @staticmethod
    def _validate_client_service(
        db: Session,
        client_id: str,
        service_id: str,
    ) -> ClientService:
        """
        Validate that service is assigned to client
        
        Args:
            db: Database session
            client_id: Client ID
            service_id: Service ID
        
        Returns:
            ClientService object
        
        Raises:
            HTTPException: If service not assigned to client
        """
        client_service = (
            db.query(ClientService)
            .filter(
                ClientService.client_id == client_id,
                ClientService.service_id == service_id,
                ClientService.is_active == True,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Service is not assigned to this client."
            )

        return client_service

    @staticmethod
    def _create_permissions(
        db: Session,
        user_id: str,
        permissions: List,
        client_id: str,
    ) -> List[PermissionResponse]:
        """
        Create permissions for a client user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: List of permissions
            client_id: Client ID
        
        Returns:
            List of PermissionResponse objects
        
        Raises:
            HTTPException: If service not assigned to client
        """
        permission_response = []

        for permission in permissions:
            # Get service and validate it's assigned to client in one query
            client_service = (
                db.query(ClientService, Service)
                .join(Service, ClientService.service_id == Service.id)
                .filter(
                    ClientService.client_id == client_id,
                    ClientService.service_id == permission.service_id,
                    ClientService.is_active == True,
                    Service.is_active == True,
                )
                .first()
            )

            if not client_service:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Service '{permission.service_id}' is not assigned to this client or does not exist."
                )

            _, service = client_service

            # Create permission
            user_permission = UserPermission(
                id=str(uuid.uuid4()),
                user_type="CLIENT_USER",
                user_id=user_id,
                service_id=permission.service_id,
                can_create=permission.can_create,
                can_read=permission.can_read,
                can_update=permission.can_update,
                can_delete=permission.can_delete,
            )

            db.add(user_permission)

            permission_response.append(
                PermissionResponse(
                    service_id=service.id,
                    service_name=service.service_name,
                    service_code=service.service_code,
                    can_create=permission.can_create,
                    can_read=permission.can_read,
                    can_update=permission.can_update,
                    can_delete=permission.can_delete,
                )
            )

        return permission_response

    @staticmethod
    def _replace_permissions(
        db: Session,
        user_id: str,
        permissions: List,
        client_id: str,
    ) -> List[PermissionResponse]:
        """
        Replace all permissions for a client user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: List of new permissions
            client_id: Client ID
        
        Returns:
            List of PermissionResponse objects
        """
        # Delete existing permissions
        db.query(UserPermission).filter(
            UserPermission.user_type == "CLIENT_USER",
            UserPermission.user_id == user_id,
        ).delete(synchronize_session=False)

        # Create new permissions
        return ClientUserService._create_permissions(
            db=db,
            user_id=user_id,
            permissions=permissions,
            client_id=client_id,
        )

    @staticmethod
    def _get_user_permissions(
        db: Session,
        user_id: str,
    ) -> List[PermissionResponse]:
        """
        Get permissions for a client user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            List of PermissionResponse objects
        """
        permissions = (
            db.query(UserPermission, Service)
            .join(Service, UserPermission.service_id == Service.id)
            .filter(
                UserPermission.user_type == "CLIENT_USER",
                UserPermission.user_id == user_id,
            )
            .all()
        )

        permission_response = []

        for permission, service in permissions:
            permission_response.append(
                PermissionResponse(
                    service_id=service.id,
                    service_name=service.service_name,
                    service_code=service.service_code,
                    can_create=permission.can_create,
                    can_read=permission.can_read,
                    can_update=permission.can_update,
                    can_delete=permission.can_delete,
                )
            )

        return permission_response

    @staticmethod
    def get_available_permissions(
        db: Session,
        client_id: str,
    ) -> List[PermissionResponse]:
        """
        Get all available permissions for a client
        
        Args:
            db: Database session
            client_id: Client ID
        
        Returns:
            List of PermissionResponse objects
        
        Raises:
            HTTPException: If client not found
        """
        # Validate client exists
        ClientUserService._validate_client(db, client_id)

        # Get all services assigned to client
        client_services = (
            db.query(ClientService, Service)
            .join(Service, ClientService.service_id == Service.id)
            .filter(
                ClientService.client_id == client_id,
                ClientService.is_active == True,
                Service.is_active == True,
            )
            .all()
        )

        available_permissions = []

        for client_service, service in client_services:
            available_permissions.append(
                PermissionResponse(
                    service_id=service.id,
                    service_name=service.service_name,
                    service_code=service.service_code,
                    can_create=False,
                    can_read=False,
                    can_update=False,
                    can_delete=False,
                )
            )

        return available_permissions

    # ==================== CRUD OPERATIONS ====================

    @staticmethod
    def create_client_user(
        db: Session,
        payload: ClientUserCreate,
        created_by: str,
    ) -> ClientUserResponse:
        """
        Create a new client user
        
        Args:
            db: Database session
            payload: User creation payload
            created_by: ID of user creating this user
        
        Returns:
            Created ClientUser with permissions
        
        Raises:
            HTTPException: If validation fails or error occurs
        """
        try:
            # Validate client exists
            ClientUserService._validate_client(db, payload.client_id)

            # Validate unique fields
            ClientUserService._validate_email(db, payload.email)
            ClientUserService._validate_phone(db, payload.phone)

            # Create user
            user = ClientUser(
                id=str(uuid.uuid4()),
                client_id=payload.client_id,
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                password=hash_password(payload.password),
                designation=payload.designation,
                created_by=created_by,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(user)

            # Create permissions
            permission_response = ClientUserService._create_permissions(
                db=db,
                user_id=user.id,
                permissions=payload.permissions,
                client_id=payload.client_id,
            )

            db.commit()
            db.refresh(user)

            return ClientUserResponse(
                id=user.id,
                client_id=user.client_id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                designation=user.designation,
                is_active=user.is_active,
                permissions=permission_response,
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the client user."
            )

    @staticmethod
    def login(
        db: Session,
        payload: ClientUserLogin,
    ) -> ClientUserLoginResponse:
        """
        Login a client user
        
        Args:
            db: Database session
            payload: Login credentials
        
        Returns:
            ClientUserLoginResponse with access token and user data
        
        Raises:
            HTTPException: If credentials are invalid
        """
        user = (
            db.query(ClientUser)
            .filter(ClientUser.email == payload.email)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not verify_password(payload.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive."
            )

        # Update last login (ensure column exists in model)
        try:
            user.last_login = datetime.now(timezone.utc)
        except AttributeError:
            # If last_login column doesn't exist, skip silently
            pass

        # Get user permissions
        permission_response = ClientUserService._get_user_permissions(db, user.id)

        # Create access token
        access_token = create_access_token(
            {
                "sub": user.id,
                "email": user.email,
                "user_type": "CLIENT_USER",
                "client_id": user.client_id,
            }
        )

        db.commit()

        return ClientUserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=ClientUserResponse(
                id=user.id,
                client_id=user.client_id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                designation=user.designation,
                is_active=user.is_active,
                permissions=permission_response,
            ),
        )

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: str,
    ) -> ClientUserResponse:
        """
        Get client user by ID with permissions
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            ClientUserResponse with permissions
        
        Raises:
            HTTPException: If user not found
        """
        user = (
            db.query(ClientUser)
            .filter(ClientUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client User not found."
            )

        # Get permissions
        permission_response = ClientUserService._get_user_permissions(db, user.id)

        return ClientUserResponse(
            id=user.id,
            client_id=user.client_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            designation=user.designation,
            is_active=user.is_active,
            permissions=permission_response,
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> Optional[ClientUser]:
        """
        Get client user by email
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            ClientUser or None
        """
        return (
            db.query(ClientUser)
            .filter(ClientUser.email == email)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        client_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> ClientUserListResponse:
        """
        Get all client users with pagination, filtering, and search
        
        Args:
            db: Database session
            client_id: Filter by client ID
            skip: Number of records to skip
            limit: Maximum records to return
            is_active: Filter by active status
            search: Search term for name, email, phone, or designation
        
        Returns:
            ClientUserListResponse with pagination metadata
        """
        query = db.query(ClientUser)

        # Apply filters
        if client_id:
            query = query.filter(ClientUser.client_id == client_id)

        if is_active is not None:
            query = query.filter(ClientUser.is_active == is_active)

        # Apply search
        if search:
            query = query.filter(
                or_(
                    ClientUser.full_name.ilike(f"%{search}%"),
                    ClientUser.email.ilike(f"%{search}%"),
                    ClientUser.phone.ilike(f"%{search}%"),
                    ClientUser.designation.ilike(f"%{search}%"),
                )
            )

        total = query.count()

        users = (
            query.order_by(ClientUser.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Get permissions for each user
        items = []
        for user in users:
            permissions = ClientUserService._get_user_permissions(db, user.id)
            items.append(
                ClientUserResponse(
                    id=user.id,
                    client_id=user.client_id,
                    full_name=user.full_name,
                    email=user.email,
                    phone=user.phone,
                    designation=user.designation,
                    is_active=user.is_active,
                    permissions=permissions,
                )
            )

        return ClientUserListResponse(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
            items=items,
        )

    @staticmethod
    def count(
        db: Session,
        client_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count client users with optional filters
        
        Args:
            db: Database session
            client_id: Filter by client ID
            is_active: Filter by active status
            search: Search term
        
        Returns:
            Total count
        """
        query = db.query(ClientUser)

        if client_id:
            query = query.filter(ClientUser.client_id == client_id)

        if is_active is not None:
            query = query.filter(ClientUser.is_active == is_active)

        if search:
            query = query.filter(
                or_(
                    ClientUser.full_name.ilike(f"%{search}%"),
                    ClientUser.email.ilike(f"%{search}%"),
                    ClientUser.phone.ilike(f"%{search}%"),
                    ClientUser.designation.ilike(f"%{search}%"),
                )
            )

        return query.count()

    @staticmethod
    def update(
        db: Session,
        user_id: str,
        payload: ClientUserUpdate,
    ) -> ClientUserResponse:
        """
        Update client user
        
        Args:
            db: Database session
            user_id: User ID
            payload: Update payload
        
        Returns:
            Updated ClientUser with permissions
        
        Raises:
            HTTPException: If user not found or validation fails
        """
        try:
            user = (
                db.query(ClientUser)
                .filter(ClientUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client User not found."
                )

            # Validate unique fields if being updated
            if payload.email and payload.email != user.email:
                ClientUserService._validate_email(db, payload.email, exclude_id=user.id)

            if payload.phone and payload.phone != user.phone:
                ClientUserService._validate_phone(db, payload.phone, exclude_id=user.id)

            # Update fields
            update_data = payload.model_dump(exclude_unset=True, exclude={"permissions"})

            for key, value in update_data.items():
                setattr(user, key, value)

            user.updated_at = datetime.now(timezone.utc)

            # Update permissions if provided
            permission_response = []
            if payload.permissions is not None:
                permission_response = ClientUserService._replace_permissions(
                    db=db,
                    user_id=user.id,
                    permissions=payload.permissions,
                    client_id=user.client_id,
                )
            else:
                permission_response = ClientUserService._get_user_permissions(db, user.id)

            db.commit()
            db.refresh(user)

            return ClientUserResponse(
                id=user.id,
                client_id=user.client_id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                designation=user.designation,
                is_active=user.is_active,
                permissions=permission_response,
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the client user."
            )

    @staticmethod
    def delete(
        db: Session,
        user_id: str,
    ) -> dict:
        """
        Soft delete client user (deactivate)
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If user not found or already inactive
        """
        try:
            user = (
                db.query(ClientUser)
                .filter(ClientUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client User not found."
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client User is already inactive."
                )

            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)

            db.commit()

            return {"message": "Client User deactivated successfully."}

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deactivating the client user."
            )

    @staticmethod
    def restore(
        db: Session,
        user_id: str,
    ) -> ClientUserResponse:
        """
        Restore a soft-deleted client user (reactivate)
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Restored ClientUser with permissions
        
        Raises:
            HTTPException: If user not found or already active
        """
        try:
            user = (
                db.query(ClientUser)
                .filter(ClientUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client User not found."
                )

            if user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Client User is already active."
                )

            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(user)

            # Get permissions
            permission_response = ClientUserService._get_user_permissions(db, user.id)

            return ClientUserResponse(
                id=user.id,
                client_id=user.client_id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                designation=user.designation,
                is_active=user.is_active,
                permissions=permission_response,
            )

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while restoring the client user."
            )

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> dict:
        """
        Change client user password
        
        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If user not found or password validation fails
        """
        try:
            user = (
                db.query(ClientUser)
                .filter(ClientUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client User not found."
                )

            # Verify current password
            if not verify_password(current_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect."
                )

            # Check if new password is same as current
            if verify_password(new_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password cannot be the same as the current password."
                )

            # Update password
            user.password = hash_password(new_password)
            user.updated_at = datetime.now(timezone.utc)

            db.commit()

            return {"message": "Password changed successfully."}

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing the password."
            )

    @staticmethod
    def update_permissions(
        db: Session,
        user_id: str,
        permissions: List,
    ) -> List[PermissionResponse]:
        """
        Update permissions for a client user
        
        Args:
            db: Database session
            user_id: User ID
            permissions: List of new permissions
        
        Returns:
            List of PermissionResponse objects
        
        Raises:
            HTTPException: If user not found
        """
        try:
            user = (
                db.query(ClientUser)
                .filter(ClientUser.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client User not found."
                )

            permission_response = ClientUserService._replace_permissions(
                db=db,
                user_id=user.id,
                permissions=permissions,
                client_id=user.client_id,
            )

            db.commit()
            return permission_response

        except HTTPException:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating permissions."
            )

    @staticmethod
    def get_permissions(
        db: Session,
        user_id: str,
    ) -> List[PermissionResponse]:
        """
        Get permissions for a client user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            List of PermissionResponse objects
        
        Raises:
            HTTPException: If user not found
        """
        user = (
            db.query(ClientUser)
            .filter(ClientUser.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client User not found."
            )

        return ClientUserService._get_user_permissions(db, user.id)