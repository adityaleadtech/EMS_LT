from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.services.services import ServiceListResponse


class ServiceService:

    @staticmethod
    def get_services(db: Session):
        services = (
            db.query(Service)
            .filter(Service.is_active == True)
            .order_by(Service.display_order.asc())
            .all()
        )

        return ServiceListResponse(services=services)