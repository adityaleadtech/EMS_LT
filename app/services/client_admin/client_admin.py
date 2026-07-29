from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.client.client import Client
from app.models.client_admin.client_admin import ClientAdmin
from app.schemas.client_admin.client_admin import (
    ClientAdminCreate,
    ClientAdminUpdate,
    ClientAdminLogin,
    ClientAdminLoginResponse,
    ClientAdminResponse,
    ClientAdminListResponse,
)


class ClientAdminService:
    """Service class for Client Admin operations"""

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
    def _validate_client_admin(
        db: Session,
        client_id: str,
    ):
        """
        Validate that client doesn't already have an admin
        
        Args:
            db: Database session
            client_id: Client ID
        
        Raises:
            HTTPException: If client already has an admin
        """
        exists = (
            db.query(ClientAdmin)
            .filter(
                ClientAdmin.client_id == client_id
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client already has a Client Admin."
            )

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
            exclude_id: Client Admin ID to exclude from check
        
        Raises:
            HTTPException: If email already exists
        """
        query = db.query(ClientAdmin).filter(
            ClientAdmin.email == email
        )

        if exclude_id:
            query = query.filter(
                ClientAdmin.id != exclude_id
            )

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
            exclude_id: Client Admin ID to exclude from check
        
        Raises:
            HTTPException: If phone number already exists
        """
        query = db.query(ClientAdmin).filter(
            ClientAdmin.phone == phone
        )

        if exclude_id:
            query = query.filter(
                ClientAdmin.id != exclude_id
            )

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists."
            )

    @staticmethod
    def _validate_employee_id(
        db: Session,
        employee_id: Optional[str],
        exclude_id: Optional[str] = None,
    ):
        """
        Validate that employee ID is unique
        
        Args:
            db: Database session
            employee_id: Employee ID to validate
            exclude_id: Client Admin ID to exclude from check
        
        Raises:
            HTTPException: If employee ID already exists
        """
        if not employee_id:
            return

        query = db.query(ClientAdmin).filter(
            ClientAdmin.employee_id == employee_id
        )

        if exclude_id:
            query = query.filter(
                ClientAdmin.id != exclude_id
            )

        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists."
            )

    # ==================== CRUD OPERATIONS ====================

    @staticmethod
    def create_client_admin(
        db: Session,
        payload: ClientAdminCreate,
        created_by: str,
    ) -> ClientAdminResponse:
        """
        Create a new client admin
        
        Args:
            db: Database session
            payload: Client admin creation payload
            created_by: ID of user creating this client admin
        
        Returns:
            Created ClientAdmin
        
        Raises:
            HTTPException: If validation fails or error occurs
        """
        # Validate client exists and is active
        ClientAdminService._validate_client(db, payload.client_id)

        # Validate client doesn't already have an admin
        ClientAdminService._validate_client_admin(db, payload.client_id)

        # Validate unique fields
        ClientAdminService._validate_email(db, payload.email)
        ClientAdminService._validate_phone(db, payload.phone)
        ClientAdminService._validate_employee_id(db, payload.employee_id)

        # Create client admin
        client_admin = ClientAdmin(
            id=str(uuid4()),
            client_id=payload.client_id,
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

        db.add(client_admin)
        db.commit()
        db.refresh(client_admin)

        return client_admin

    @staticmethod
    def login(
        db: Session,
        payload: ClientAdminLogin,
    ) -> ClientAdminLoginResponse:
        """
        Login a client admin
        
        Args:
            db: Database session
            payload: Login credentials
        
        Returns:
            ClientAdminLoginResponse with access token and user data
        
        Raises:
            HTTPException: If credentials are invalid
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(
                ClientAdmin.email == payload.email,
                ClientAdmin.is_active == True,
            )
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not verify_password(
            payload.password,
            client_admin.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Update last login
        client_admin.last_login = datetime.now(timezone.utc)

        db.commit()
        db.refresh(client_admin)

        # Create access token
        token = create_access_token(
            {
                "id": client_admin.id,
                "email": client_admin.email,
                "user_type": "CLIENT_ADMIN",
                "client_id": client_admin.client_id,
            }
        )

        return ClientAdminLoginResponse(
            access_token=token,
            token_type="bearer",
            user=client_admin,
        )

    @staticmethod
    def get_by_id(
        db: Session,
        client_admin_id: str,
    ) -> ClientAdminResponse:
        """
        Get client admin by ID
        
        Args:
            db: Database session
            client_admin_id: Client Admin ID
        
        Returns:
            ClientAdmin
        
        Raises:
            HTTPException: If client admin not found
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.id == client_admin_id)
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client Admin not found."
            )

        return client_admin

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> Optional[ClientAdmin]:
        """
        Get client admin by email
        
        Args:
            db: Database session
            email: Client admin email
        
        Returns:
            ClientAdmin or None
        """
        return (
            db.query(ClientAdmin)
            .filter(ClientAdmin.email == email)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> ClientAdminListResponse:
        """
        Get all client admins with pagination, filtering, and search
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            is_active: Filter by active status
            search: Search term for name, email, or phone
        
        Returns:
            ClientAdminListResponse with pagination metadata
        """
        query = db.query(ClientAdmin)

        # Apply filters
        if is_active is not None:
            query = query.filter(ClientAdmin.is_active == is_active)

        # Apply search
        if search:
            query = query.filter(
                or_(
                    ClientAdmin.full_name.ilike(f"%{search}%"),
                    ClientAdmin.email.ilike(f"%{search}%"),
                    ClientAdmin.phone.ilike(f"%{search}%"),
                )
            )

        total = query.count()

        items = (
            query.order_by(ClientAdmin.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return ClientAdminListResponse(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total,
            items=items,
        )

    @staticmethod
    def count(
        db: Session,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count client admins with optional filters
        
        Args:
            db: Database session
            is_active: Filter by active status
            search: Search term
        
        Returns:
            Total count
        """
        query = db.query(func.count(ClientAdmin.id))

        if is_active is not None:
            query = query.filter(ClientAdmin.is_active == is_active)

        if search:
            query = query.filter(
                or_(
                    ClientAdmin.full_name.ilike(f"%{search}%"),
                    ClientAdmin.email.ilike(f"%{search}%"),
                    ClientAdmin.phone.ilike(f"%{search}%"),
                )
            )

        return query.scalar()

    @staticmethod
    def update(
        db: Session,
        client_admin_id: str,
        payload: ClientAdminUpdate,
    ) -> ClientAdminResponse:
        """
        Update client admin
        
        Args:
            db: Database session
            client_admin_id: Client Admin ID
            payload: Update payload
        
        Returns:
            Updated ClientAdmin
        
        Raises:
            HTTPException: If client admin not found or validation fails
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.id == client_admin_id)
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client Admin not found."
            )

        # Validate unique fields if being updated
        if payload.email and payload.email != client_admin.email:
            ClientAdminService._validate_email(
                db,
                payload.email,
                exclude_id=client_admin.id,
            )

        if payload.phone and payload.phone != client_admin.phone:
            ClientAdminService._validate_phone(
                db,
                payload.phone,
                exclude_id=client_admin.id,
            )

        if (
            payload.employee_id is not None
            and payload.employee_id != client_admin.employee_id
        ):
            ClientAdminService._validate_employee_id(
                db,
                payload.employee_id,
                exclude_id=client_admin.id,
            )

        # Update fields
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(client_admin, field, value)

        client_admin.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(client_admin)

        return client_admin

    @staticmethod
    def delete(
        db: Session,
        client_admin_id: str,
    ) -> dict:
        """
        Soft delete client admin (deactivate)
        
        Args:
            db: Database session
            client_admin_id: Client Admin ID
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If client admin not found or already inactive
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.id == client_admin_id)
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client Admin not found."
            )

        if not client_admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client Admin is already inactive."
            )

        client_admin.is_active = False
        client_admin.updated_at = datetime.now(timezone.utc)

        db.commit()

        return {"message": "Client Admin deleted successfully."}

    @staticmethod
    def restore(
        db: Session,
        client_admin_id: str,
    ) -> ClientAdminResponse:
        """
        Restore a soft-deleted client admin (reactivate)
        
        Args:
            db: Database session
            client_admin_id: Client Admin ID
        
        Returns:
            Restored ClientAdmin
        
        Raises:
            HTTPException: If client admin not found or already active
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.id == client_admin_id)
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client Admin not found."
            )

        if client_admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client Admin is already active."
            )

        client_admin.is_active = True
        client_admin.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(client_admin)

        return client_admin

    @staticmethod
    def change_password(
        db: Session,
        client_admin_id: str,
        current_password: str,
        new_password: str,
    ) -> dict:
        """
        Change client admin password
        
        Args:
            db: Database session
            client_admin_id: Client Admin ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If client admin not found or password validation fails
        """
        client_admin = (
            db.query(ClientAdmin)
            .filter(ClientAdmin.id == client_admin_id)
            .first()
        )

        if not client_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client Admin not found."
            )

        # Verify current password
        if not verify_password(
            current_password,
            client_admin.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )

        # Update password
        client_admin.password = hash_password(new_password)
        client_admin.updated_at = datetime.now(timezone.utc)

        db.commit()

        return {"message": "Password changed successfully."}