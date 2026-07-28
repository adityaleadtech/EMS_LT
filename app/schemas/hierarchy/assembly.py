from typing import Optional
from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class AssemblyCreate(BaseCreateSchema):
    pc_district_id: str
    assembly_number: Optional[int] = None
    constituency_type: Optional[str] = Field(None, max_length=20)
    population: Optional[str] = Field(None, max_length=50)


class AssemblyUpdate(BaseUpdateSchema):
    pc_district_id: Optional[str] = None
    assembly_number: Optional[int] = None
    constituency_type: Optional[str] = Field(None, max_length=20)
    population: Optional[str] = Field(None, max_length=50)


class AssemblyResponse(BaseHierarchySchema):
    pc_district_id: str
    assembly_number: Optional[int]
    constituency_type: Optional[str]
    population: Optional[str]


class AssemblyListResponse(AssemblyResponse):
    block_count: Optional[int] = 0
    pc_district_name: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None