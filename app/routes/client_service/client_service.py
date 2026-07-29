from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import admin_required

from app.models.platform_admin.platform_admin import PlatformAdmin

from app.schemas.client_service.client_services import (
    ClientServiceAssign,
    ClientServiceListResponse,
)

from app.services.client_service.client_service import (
    ClientServiceService,
)

router = APIRouter(
    prefix="/clients",
    tags=["Client Services"],
)


# ==========================================================
# ASSIGN SERVICES
# ==========================================================

@router.post(
    "/{client_id}/services",
    response_model=ClientServiceListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Services to Client",
    description="Assigns one or more services to a client.",
)
def assign_services(
    client_id: str,
    payload: ClientServiceAssign,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientServiceService.assign_services(
        db=db,
        client_id=client_id,
        payload=payload,
        created_by=admin.id,
    )


# ==========================================================
# GET CLIENT SERVICES
# ==========================================================

@router.get(
    "/{client_id}/services",
    response_model=ClientServiceListResponse,
    summary="Get Client Services",
    description="Returns all services assigned to a client.",
)
def get_client_services(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientServiceService.get_client_services(
        db=db,
        client_id=client_id,
    )


# ==========================================================
# UPDATE CLIENT SERVICES
# ==========================================================

@router.put(
    "/{client_id}/services",
    response_model=ClientServiceListResponse,
    summary="Replace Client Services",
    description="Replaces all services assigned to a client.",
)
def update_client_services(
    client_id: str,
    payload: ClientServiceAssign,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientServiceService.assign_services(
        db=db,
        client_id=client_id,
        payload=payload,
        created_by=admin.id,
    )


# ==========================================================
# REMOVE SERVICE
# ==========================================================

@router.delete(
    "/{client_id}/services/{service_id}",
    summary="Remove Client Service",
    description="Removes a service from a client.",
)
def remove_service(
    client_id: str,
    service_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientServiceService.remove_service(
        db=db,
        client_id=client_id,
        service_id=service_id,
    )


# ==========================================================
# CLEAR ALL SERVICES
# ==========================================================

@router.delete(
    "/{client_id}/services",
    summary="Remove All Client Services",
    description="Removes all services assigned to a client.",
)
def clear_services(
    client_id: str,
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ClientServiceService.clear_services(
        db=db,
        client_id=client_id,
    )