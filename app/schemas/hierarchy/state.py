from typing import Optional
from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class StateCreate(BaseCreateSchema):
    country_id: str
    state_code: Optional[str] = Field(None, max_length=10)
    capital: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    area: Optional[str] = Field(None, max_length=50)
    population: Optional[str] = Field(None, max_length=50)


class StateUpdate(BaseUpdateSchema):
    country_id: Optional[str] = None
    state_code: Optional[str] = Field(None, max_length=10)
    capital: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    area: Optional[str] = Field(None, max_length=50)
    population: Optional[str] = Field(None, max_length=50)


class StateResponse(BaseHierarchySchema):
    country_id: str
    state_code: Optional[str]
    capital: Optional[str]
    region: Optional[str]
    area: Optional[str]
    population: Optional[str]


class StateListResponse(StateResponse):
    pc_district_count: Optional[int] = 0
    country_name: Optional[str] = None