from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import admin_required
from app.models.platform_admin.platform_admin import PlatformAdmin

from app.schemas.services.services import ServiceListResponse
from app.services.service.service import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="Get Services",
)
def get_services(
    db: Session = Depends(get_db),
    admin: PlatformAdmin = Depends(admin_required),
):
    return ServiceService.get_services(db)