from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.services.services import ServiceListResponse


class ServiceService:

    @staticmethod
    def get_services(db: Session):
        services = (
            db.query(Service)
            .all()
        )

        return ServiceListResponse(services=services)