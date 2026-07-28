from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BaseHierarchySchema(BaseModel):
    id: Optional[str] = None
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BaseCreateSchema(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    is_active: Optional[bool] = True


class BaseUpdateSchema(BaseModel):
    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None