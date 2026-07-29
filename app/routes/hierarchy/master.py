from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.hierarchy.master_service import MasterService
from app.schemas.hierarchy.master import HierarchyMasterResponse, HierarchyFlatResponse

router = APIRouter(prefix="/api/v1/hierarchy/master", tags=["Hierarchy - Master"])

@router.get("/tree", response_model=HierarchyMasterResponse)
def get_hierarchy_tree(
    country_id: Optional[str] = Query(None, description="Filter by country ID"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get complete hierarchical tree with only id and name.
    
    Returns nested structure:
    Country → State → PC District → Assembly → Block → Panchayat Ward → Polling Booth
    Each node contains only: id, name
    """
    service = MasterService(db)
    return service.get_complete_hierarchy(country_id, is_active)

@router.get("/flat", response_model=HierarchyFlatResponse)
def get_flat_hierarchy(
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get flat lists of all items with only id and name.
    
    Returns separate arrays for each hierarchy level.
    Each item contains only: id, name
    """
    service = MasterService(db)
    return service.get_flat_hierarchy(is_active)

@router.get("/country/{country_id}/tree", response_model=HierarchyMasterResponse)
def get_country_hierarchy_tree(
    country_id: str,
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get hierarchical tree for a specific country with only id and name.
    """
    service = MasterService(db)
    return service.get_complete_hierarchy(country_id, is_active)