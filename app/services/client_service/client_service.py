from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client.client import Client
from app.models.service.service import Service
from app.models.client_services.client_services import ClientService as ClientServiceModel

from app.schemas.client_service.client_services import (
    ClientServiceAssign,
    ClientServiceResponse,
    ClientServiceListResponse,
)


class ClientServiceService:
    """Service class for Client Service operations"""

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
    def _validate_service(
        db: Session,
        service_id: str,
    ) -> Service:
        """
        Validate that service exists
        
        Args:
            db: Database session
            service_id: Service ID
        
        Returns:
            Service object
        
        Raises:
            HTTPException: If service not found
        """
        service = (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_id}' not found."
            )

        return service

    @staticmethod
    def _validate_service_by_code(
        db: Session,
        service_code: str,
    ) -> Service:
        """
        Validate that service exists by service code
        
        Args:
            db: Database session
            service_code: Service code
        
        Returns:
            Service object
        
        Raises:
            HTTPException: If service not found
        """
        service = (
            db.query(Service)
            .filter(Service.service_code == service_code)
            .first()
        )

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with code '{service_code}' not found."
            )

        return service

    @staticmethod
    def _validate_service_assignment(
        db: Session,
        client_id: str,
        service_id: str,
    ) -> ClientServiceModel:
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
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_id == service_id,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not assigned to this client."
            )

        return client_service

    # ==================== CRUD OPERATIONS ====================

    @staticmethod
    def assign_services(
        db: Session,
        client_id: str,
        payload: ClientServiceAssign,
        created_by: str,
    ) -> ClientServiceListResponse:
        """
        Assign services to a client
        
        Args:
            db: Database session
            client_id: Client ID
            payload: Services to assign (using service codes)
            created_by: ID of user assigning services
        
        Returns:
            ClientServiceListResponse with assigned services
        
        Raises:
            HTTPException: If client not found or service not found
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Remove all existing service assignments
        db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id
        ).delete()
        db.commit()

        assigned = []
        service_codes = payload.services if isinstance(payload.services, list) else [payload.services]

        for service_code in service_codes:
            # Validate service exists and get it
            service = ClientServiceService._validate_service_by_code(
                db,
                service_code,
            )

            # Create client service assignment
            client_service = ClientServiceModel(
                id=str(uuid4()),
                client_id=client_id,
                service_id=service.id,
                service_code=service.service_code,
                service_name=service.service_name,
                created_by=created_by,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(client_service)
            assigned.append(client_service)

        db.commit()

        # Refresh assigned items
        for item in assigned:
            db.refresh(item)

        return ClientServiceListResponse(
            total=len(assigned),
            items=assigned,
        )

    @staticmethod
    def assign_services_by_ids(
        db: Session,
        client_id: str,
        service_ids: List[str],
        created_by: str,
    ) -> ClientServiceListResponse:
        """
        Assign services to a client using service IDs
        
        Args:
            db: Database session
            client_id: Client ID
            service_ids: List of service IDs
            created_by: ID of user assigning services
        
        Returns:
            ClientServiceListResponse with assigned services
        
        Raises:
            HTTPException: If client not found or service not found
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Remove all existing service assignments
        db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id
        ).delete()
        db.commit()

        assigned = []

        for service_id in service_ids:
            # Validate service exists and get it
            service = ClientServiceService._validate_service(db, service_id)

            # Create client service assignment
            client_service = ClientServiceModel(
                id=str(uuid4()),
                client_id=client_id,
                service_id=service.id,
                service_code=service.service_code,
                service_name=service.service_name,
                created_by=created_by,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(client_service)
            assigned.append(client_service)

        db.commit()

        # Refresh assigned items
        for item in assigned:
            db.refresh(item)

        return ClientServiceListResponse(
            total=len(assigned),
            items=assigned,
        )

    @staticmethod
    def get_client_services(
        db: Session,
        client_id: str,
        is_active: Optional[bool] = True,
    ) -> ClientServiceListResponse:
        """
        Get all services assigned to a client
        
        Args:
            db: Database session
            client_id: Client ID
            is_active: Filter by active status
        
        Returns:
            ClientServiceListResponse with client services
        
        Raises:
            HTTPException: If client not found
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Get all services for client
        query = db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id
        )

        if is_active is not None:
            query = query.filter(ClientServiceModel.is_active == is_active)

        services = query.all()

        return ClientServiceListResponse(
            total=len(services),
            items=services,
        )

    @staticmethod
    def get_client_service_by_code(
        db: Session,
        client_id: str,
        service_code: str,
    ) -> ClientServiceResponse:
        """
        Get a specific service assigned to a client by service code
        
        Args:
            db: Database session
            client_id: Client ID
            service_code: Service code
        
        Returns:
            ClientServiceResponse
        
        Raises:
            HTTPException: If client not found or service not assigned
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_code == service_code,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_code}' not assigned to this client."
            )

        return client_service

    @staticmethod
    def get_client_service_by_id(
        db: Session,
        client_id: str,
        service_id: str,
    ) -> ClientServiceResponse:
        """
        Get a specific service assigned to a client by service ID
        
        Args:
            db: Database session
            client_id: Client ID
            service_id: Service ID
        
        Returns:
            ClientServiceResponse
        
        Raises:
            HTTPException: If client not found or service not assigned
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_id == service_id,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_id}' not assigned to this client."
            )

        return client_service

    @staticmethod
    def remove_service(
        db: Session,
        client_id: str,
        service_id: str,
    ) -> dict:
        """
        Remove a single service from a client
        
        Args:
            db: Database session
            client_id: Client ID
            service_id: Service ID
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If client not found or service not assigned
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Get and validate assignment
        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_id == service_id,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not assigned to this client."
            )

        db.delete(client_service)
        db.commit()

        return {
            "message": f"Service '{service_id}' removed successfully."
        }

    @staticmethod
    def remove_service_by_code(
        db: Session,
        client_id: str,
        service_code: str,
    ) -> dict:
        """
        Remove a single service from a client by service code
        
        Args:
            db: Database session
            client_id: Client ID
            service_code: Service code
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If client not found or service not assigned
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Get and validate assignment
        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_code == service_code,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_code}' not assigned to this client."
            )

        db.delete(client_service)
        db.commit()

        return {
            "message": f"Service '{service_code}' removed successfully."
        }

    @staticmethod
    def clear_services(
        db: Session,
        client_id: str,
    ) -> dict:
        """
        Remove all services from a client
        
        Args:
            db: Database session
            client_id: Client ID
        
        Returns:
            Success message
        
        Raises:
            HTTPException: If client not found
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Delete all services for client
        db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id
        ).delete()

        db.commit()

        return {
            "message": "All services removed successfully."
        }

    @staticmethod
    def toggle_service_status(
        db: Session,
        client_id: str,
        service_id: str,
        is_active: bool,
    ) -> ClientServiceResponse:
        """
        Toggle service status (activate/deactivate)
        
        Args:
            db: Database session
            client_id: Client ID
            service_id: Service ID
            is_active: New active status
        
        Returns:
            Updated ClientService
        
        Raises:
            HTTPException: If client not found or service not assigned
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        # Get service assignment
        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_id == service_id,
            )
            .first()
        )

        if not client_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not assigned to this client."
            )

        client_service.is_active = is_active
        client_service.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(client_service)

        return client_service

    @staticmethod
    def check_service_access(
        db: Session,
        client_id: str,
        service_code: str,
    ) -> bool:
        """
        Check if a client has access to a service
        
        Args:
            db: Database session
            client_id: Client ID
            service_code: Service code
        
        Returns:
            True if client has access, False otherwise
        """
        client_service = (
            db.query(ClientServiceModel)
            .filter(
                ClientServiceModel.client_id == client_id,
                ClientServiceModel.service_code == service_code,
                ClientServiceModel.is_active == True,
            )
            .first()
        )

        return client_service is not None

    @staticmethod
    def get_services_summary(
        db: Session,
        client_id: str,
    ) -> dict:
        """
        Get summary of client services
        
        Args:
            db: Database session
            client_id: Client ID
        
        Returns:
            Dictionary with service counts
        """
        # Validate client exists
        ClientServiceService._validate_client(db, client_id)

        total = db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id
        ).count()

        active = db.query(ClientServiceModel).filter(
            ClientServiceModel.client_id == client_id,
            ClientServiceModel.is_active == True,
        ).count()

        return {
            "total_services": total,
            "active_services": active,
            "inactive_services": total - active,
        }