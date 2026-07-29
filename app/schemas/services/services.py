from pydantic import BaseModel
from typing import List


class ServiceResponse(BaseModel):
    id: str
    service_name: str
    service_code: str
    route: str | None = None
    display_order: int

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    services: List[ServiceResponse]