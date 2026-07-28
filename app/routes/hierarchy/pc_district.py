from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.pc_district_service import PCDistrictService
from app.schemas.hierarchy.pc_district import PCDistrictCreate, PCDistrictUpdate, PCDistrictResponse, PCDistrictListResponse

router = APIRouter(prefix="/api/v1/hierarchy/pc-districts", tags=["Hierarchy - PC Districts"])

@router.post("/", response_model=PCDistrictResponse, status_code=201)
def create_pc_district(pc_data: PCDistrictCreate, db: Session = Depends(get_db)):
    """Create a new PC District"""
    service = PCDistrictService(db)
    return service.create(pc_data)

@router.get("/", response_model=List[PCDistrictListResponse])
def get_pc_districts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all PC districts with optional filters"""
    service = PCDistrictService(db)
    return service.get_all(skip, limit, state_id, is_active)

@router.get("/{pc_district_id}", response_model=PCDistrictResponse)
def get_pc_district(pc_district_id: str, db: Session = Depends(get_db)):
    """Get a specific PC district by ID"""
    service = PCDistrictService(db)
    return service.get_by_id(pc_district_id)

@router.put("/{pc_district_id}", response_model=PCDistrictResponse)
def update_pc_district(pc_district_id: str, pc_data: PCDistrictUpdate, db: Session = Depends(get_db)):
    """Update a PC district"""
    service = PCDistrictService(db)
    return service.update(pc_district_id, pc_data)

@router.delete("/{pc_district_id}", status_code=204)
def delete_pc_district(
    pc_district_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete a PC district (soft or hard)"""
    service = PCDistrictService(db)
    service.delete(pc_district_id, soft_delete)
    return None

@router.get("/{pc_district_id}/assemblies", response_model=List)
def get_assemblies_by_pc_district(
    pc_district_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all assemblies for a specific PC district"""
    service = PCDistrictService(db)
    return service.get_assemblies_by_pc_district(pc_district_id, is_active)