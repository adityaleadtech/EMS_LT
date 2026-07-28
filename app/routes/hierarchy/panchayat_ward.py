from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.panchayat_ward_service import PanchayatWardService
from app.schemas.hierarchy.panchayat_ward import PanchayatWardCreate, PanchayatWardUpdate, PanchayatWardResponse, PanchayatWardListResponse

router = APIRouter(prefix="/api/v1/hierarchy/panchayat-wards", tags=["Hierarchy - Panchayat Wards"])

@router.post("/", response_model=PanchayatWardResponse, status_code=201)
def create_panchayat_ward(ward_data: PanchayatWardCreate, db: Session = Depends(get_db)):
    """Create a new Panchayat Ward"""
    service = PanchayatWardService(db)
    return service.create(ward_data)

@router.get("/", response_model=List[PanchayatWardListResponse])
def get_panchayat_wards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all panchayat wards with optional filters"""
    service = PanchayatWardService(db)
    return service.get_all(skip, limit, block_id, is_active)

@router.get("/{ward_id}", response_model=PanchayatWardResponse)
def get_panchayat_ward(ward_id: str, db: Session = Depends(get_db)):
    """Get a specific panchayat ward by ID"""
    service = PanchayatWardService(db)
    return service.get_by_id(ward_id)

@router.put("/{ward_id}", response_model=PanchayatWardResponse)
def update_panchayat_ward(ward_id: str, ward_data: PanchayatWardUpdate, db: Session = Depends(get_db)):
    """Update a panchayat ward"""
    service = PanchayatWardService(db)
    return service.update(ward_id, ward_data)

@router.delete("/{ward_id}", status_code=204)
def delete_panchayat_ward(
    ward_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete a panchayat ward (soft or hard)"""
    service = PanchayatWardService(db)
    service.delete(ward_id, soft_delete)
    return None

@router.get("/{ward_id}/polling-booths", response_model=List)
def get_polling_booths_by_ward(
    ward_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all polling booths for a specific panchayat ward"""
    service = PanchayatWardService(db)
    return service.get_polling_booths_by_ward(ward_id, is_active)