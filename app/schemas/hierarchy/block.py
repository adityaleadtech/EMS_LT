from typing import Optional
from pydantic import Field
from .base import BaseHierarchySchema, BaseCreateSchema, BaseUpdateSchema


class BlockCreate(BaseCreateSchema):
    assembly_id: str
    block_number: Optional[int] = None
    block_type: Optional[str] = Field(None, max_length=20)
    area: Optional[str] = Field(None, max_length=50)


class BlockUpdate(BaseUpdateSchema):
    assembly_id: Optional[str] = None
    block_number: Optional[int] = None
    block_type: Optional[str] = Field(None, max_length=20)
    area: Optional[str] = Field(None, max_length=50)


class BlockResponse(BaseHierarchySchema):
    assembly_id: str
    block_number: Optional[int]
    block_type: Optional[str]
    area: Optional[str]


class BlockListResponse(BlockResponse):
    panchayat_ward_count: Optional[int] = 0
    assembly_name: Optional[str] = None
    pc_district_name: Optional[str] = None
    state_name: Optional[str] = None
    country_name: Optional[str] = None