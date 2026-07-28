from typing import Optional
from pydantic import Field
from enum import Enum
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class PollingStationType(str, Enum):
    PERMANENT = "Permanent"
    TEMPORARY = "Temporary"
    MOBILE = "Mobile"


class PollingBoothCreate(BaseCreateSchema):
    panchayat_ward_id: str
    booth_number: int
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    polling_station_type: Optional[PollingStationType] = PollingStationType.PERMANENT
    capacity: Optional[int] = None
    facilities: Optional[str] = None
    is_accessible: Optional[bool] = True


class PollingBoothUpdate(BaseUpdateSchema):
    panchayat_ward_id: Optional[str] = None
    booth_number: Optional[int] = None
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    polling_station_type: Optional[PollingStationType] = None
    capacity: Optional[int] = None
    facilities: Optional[str] = None
    is_accessible: Optional[bool] = None


class PollingBoothResponse(BaseHierarchySchema):
    panchayat_ward_id: str
    booth_number: int
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    polling_station_type: Optional[PollingStationType]
    capacity: Optional[int]
    facilities: Optional[str]
    is_accessible: Optional[bool]


class PollingBoothListResponse(PollingBoothResponse):
    panchayat_ward_name: Optional[str] = None
    block_name: Optional[str] = None
    assembly_name: Optional[str] = None
    pc_district_name: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None