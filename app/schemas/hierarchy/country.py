from typing import Optional
from datetime import datetime

from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class CountryCreate(BaseCreateSchema):
    iso_code: Optional[str] = Field(None, max_length=5)
    phone_code: Optional[str] = Field(None, max_length=10)
    currency: Optional[str] = Field(None, max_length=50)
    capital: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    sub_region: Optional[str] = Field(None, max_length=50)
    flag_url: Optional[str] = None


class CountryUpdate(BaseUpdateSchema):
    iso_code: Optional[str] = Field(None, max_length=5)
    phone_code: Optional[str] = Field(None, max_length=10)
    currency: Optional[str] = Field(None, max_length=50)
    capital: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    sub_region: Optional[str] = Field(None, max_length=50)
    flag_url: Optional[str] = None


class CountryResponse(BaseHierarchySchema):
    iso_code: Optional[str]
    phone_code: Optional[str]
    currency: Optional[str]
    capital: Optional[str]
    region: Optional[str]
    sub_region: Optional[str]
    flag_url: Optional[str]


class CountryListResponse(CountryResponse):
    state_count: Optional[int] = 0