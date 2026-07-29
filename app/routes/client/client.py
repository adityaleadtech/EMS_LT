from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import admin_required
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.schemas.client.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)
from app.services.client.client import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


# ==================== CREATE ====================

@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Client",
    description="Creates a new client (Admin only)"
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Create a new client - Requires Platform Admin authentication
    """
    try:
        return ClientService.create_client(
            db=db,
            payload=payload,
            created_by=admin.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== READ ====================

@router.get(
    "/",
    response_model=ClientListResponse,
    summary="Get All Clients",
    description="Retrieves a paginated list of all clients (Admin only)"
)
def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None, description="Search by name, code, or email"),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get all clients with pagination and filtering - Requires Platform Admin authentication
    """
    return ClientService.get_all(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )


@router.get(
    "/count",
    summary="Get Clients Count",
    description="Returns the total number of clients (Admin only)"
)
def count_clients(
    is_active: bool | None = Query(None, description="Filter by active status"),
    search: str | None = Query(None, description="Search by name, code, or email"),
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get total count of clients - Requires Platform Admin authentication
    """
    count = ClientService.count(
        db=db,
        is_active=is_active,
        search=search,
    )
    return {"total": count}


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get Client by ID",
    description="Retrieves a specific client by their UUID (Admin only)"
)
def get_client(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get client by ID - Requires Platform Admin authentication
    """
    try:
        return ClientService.get_by_id(
            db=db,
            client_id=client_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== UPDATE ====================

@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update Client",
    description="Updates a client's details (Admin only)"
)
def update_client(
    client_id: str,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Update client - Requires Platform Admin authentication
    """
    try:
        return ClientService.update(
            db=db,
            client_id=client_id,
            payload=payload,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== DELETE ====================

@router.delete(
    "/{client_id}",
    summary="Soft Delete Client",
    description="Soft deletes a client (sets is_active=False) (Admin only)"
)
def delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Soft delete client - Requires Platform Admin authentication
    """
    try:
        return ClientService.delete(
            db=db,
            client_id=client_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{client_id}/restore",
    response_model=ClientResponse,
    summary="Restore Client",
    description="Restores a soft-deleted client (Admin only)"
)
def restore_client(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Restore client - Requires Platform Admin authentication
    """
    try:
        return ClientService.restore(
            db=db,
            client_id=client_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== MINISTRIES ====================

@router.get(
    "/{client_id}/ministries",
    summary="Get Client Ministries",
    description="Retrieves all ministries associated with a client (Admin only)"
)
def get_client_ministries(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Get client ministries - Requires Platform Admin authentication
    """
    try:
        return ClientService.get_client_ministries(
            db=db,
            client_id=client_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put(
    "/{client_id}/ministries",
    summary="Update Client Ministries",
    description="Updates all ministries associated with a client (Admin only)"
)
def update_client_ministries(
    client_id: str,
    ministries: List[str],
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    """
    Update client ministries - Requires Platform Admin authentication
    """
    try:
        return ClientService.update_client_ministries(
            db=db,
            client_id=client_id,
            ministries=ministries,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )