from typing import Optional
from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class PanchayatWardCreate(BaseCreateSchema):
    block_id: str
    ward_number: Optional[int] = None
    ward_type: Optional[str] = Field(None, max_length=20)
    population: Optional[int] = None
    area: Optional[float] = None
    pincode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PanchayatWardUpdate(BaseUpdateSchema):
    block_id: Optional[str] = None
    ward_number: Optional[int] = None
    ward_type: Optional[str] = Field(None, max_length=20)
    population: Optional[int] = None
    area: Optional[float] = None
    pincode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PanchayatWardResponse(BaseHierarchySchema):
    block_id: str
    ward_number: Optional[int]
    ward_type: Optional[str]
    population: Optional[int]
    area: Optional[float]
    pincode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class PanchayatWardListResponse(PanchayatWardResponse):
    polling_booth_count: Optional[int] = 0
    block_name: Optional[str] = None
    assembly_name: Optional[str] = None
    pc_district_name: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None