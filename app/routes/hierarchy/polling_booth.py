from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.polling_booth_service import PollingBoothService
from app.schemas.hierarchy.polling_booth import PollingBoothCreate, PollingBoothUpdate, PollingBoothResponse, PollingBoothListResponse

router = APIRouter(prefix="/api/v1/hierarchy/polling-booths", tags=["Hierarchy - Polling Booths"])

@router.post("/", response_model=PollingBoothResponse, status_code=201)
def create_polling_booth(booth_data: PollingBoothCreate, db: Session = Depends(get_db)):
    """Create a new Polling Booth"""
    service = PollingBoothService(db)
    return service.create(booth_data)

@router.get("/", response_model=List[PollingBoothListResponse])
def get_polling_booths(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ward_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all polling booths with optional filters"""
    service = PollingBoothService(db)
    return service.get_all(skip, limit, ward_id, is_active)

@router.get("/{booth_id}", response_model=PollingBoothResponse)
def get_polling_booth(booth_id: str, db: Session = Depends(get_db)):
    """Get a specific polling booth by ID"""
    service = PollingBoothService(db)
    return service.get_by_id(booth_id)

@router.put("/{booth_id}", response_model=PollingBoothResponse)
def update_polling_booth(booth_id: str, booth_data: PollingBoothUpdate, db: Session = Depends(get_db)):
    """Update a polling booth"""
    service = PollingBoothService(db)
    return service.update(booth_id, booth_data)

@router.delete("/{booth_id}", status_code=204)
def delete_polling_booth(
    booth_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete a polling booth (soft or hard)"""
    service = PollingBoothService(db)
    service.delete(booth_id, soft_delete)
    return None