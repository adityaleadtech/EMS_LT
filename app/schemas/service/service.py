from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceResponse(BaseModel):
    id: str

    service_code: str

    service_name: str

    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)