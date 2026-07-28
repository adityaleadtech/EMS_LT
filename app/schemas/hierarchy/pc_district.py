from typing import Optional
from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class PCDistrictCreate(BaseCreateSchema):
    state_id: str
    district_number: Optional[int] = None
    total_assemblies: Optional[int] = None
    area: Optional[str] = Field(None, max_length=50)
    population: Optional[str] = Field(None, max_length=50)
    district_type: Optional[str] = Field(None, max_length=20)


class PCDistrictUpdate(BaseUpdateSchema):
    state_id: Optional[str] = None
    district_number: Optional[int] = None
    total_assemblies: Optional[int] = None
    area: Optional[str] = Field(None, max_length=50)
    population: Optional[str] = Field(None, max_length=50)
    district_type: Optional[str] = Field(None, max_length=20)


class PCDistrictResponse(BaseHierarchySchema):
    state_id: str
    district_number: Optional[int]
    total_assemblies: Optional[int]
    area: Optional[str]
    population: Optional[str]
    district_type: Optional[str]


class PCDistrictListResponse(PCDistrictResponse):
    assembly_count: Optional[int] = 0
    state_name: Optional[str] = None
    country_name: Optional[str] = None