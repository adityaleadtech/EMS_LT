from typing import Optional, List
from pydantic import BaseModel


class BaseNode(BaseModel):
    """Base node with only id and name"""
    id: str
    name: str


class CountryNode(BaseNode):
    states: List["StateNode"] = []


class StateNode(BaseNode):
    pc_districts: List["PCDistrictNode"] = []


class PCDistrictNode(BaseNode):
    assemblies: List["AssemblyNode"] = []


class AssemblyNode(BaseNode):
    blocks: List["BlockNode"] = []


class BlockNode(BaseNode):
    panchayat_wards: List["PanchayatWardNode"] = []


class PanchayatWardNode(BaseNode):
    polling_booths: List["PollingBoothNode"] = []


class PollingBoothNode(BaseNode):
    # No extra fields - just id and name from BaseNode
    pass


class HierarchyMasterResponse(BaseModel):
    total_countries: int
    countries: List[CountryNode]


class HierarchyFlatResponse(BaseModel):
    countries: List[BaseNode]
    states: List[BaseNode]
    pc_districts: List[BaseNode]
    assemblies: List[BaseNode]
    blocks: List[BaseNode]
    panchayat_wards: List[BaseNode]
    polling_booths: List[BaseNode]


# Update forward references
CountryNode.model_rebuild()
StateNode.model_rebuild()
PCDistrictNode.model_rebuild()
AssemblyNode.model_rebuild()
BlockNode.model_rebuild()
PanchayatWardNode.model_rebuild()