from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


# ==========================================================
# ASSIGN SERVICES
# ==========================================================

class ClientServiceAssign(BaseModel):
    services: List[str]


# ==========================================================
# CLIENT SERVICE RESPONSE
# ==========================================================

class ClientServiceResponse(BaseModel):
    id: str

    client_id: str

    service_id: str

    is_active: bool

    created_by: str

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# CLIENT SERVICE LIST RESPONSE
# ==========================================================

class ClientServiceListResponse(BaseModel):
    total: int

    items: List[ClientServiceResponse]