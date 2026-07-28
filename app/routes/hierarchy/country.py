from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.config.database import get_db
from app.services.hierarchy.country_service import CountryService
from app.schemas.hierarchy.country import CountryCreate, CountryUpdate, CountryResponse, CountryListResponse

router = APIRouter(prefix="/api/v1/hierarchy/countries", tags=["Hierarchy - Countries"])

@router.post("/", response_model=CountryResponse, status_code=201)
def create_country(country_data: CountryCreate, db: Session = Depends(get_db)):
    """Create a new country"""
    service = CountryService(db)
    return service.create(country_data)

@router.get("/", response_model=List[CountryListResponse])
def get_countries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db)
):
    """Get all countries with optional filters"""
    service = CountryService(db)
    return service.get_all(skip, limit, is_active, search)

@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: str, db: Session = Depends(get_db)):
    """Get a specific country by ID"""
    service = CountryService(db)
    return service.get_by_id(country_id)

@router.put("/{country_id}", response_model=CountryResponse)
def update_country(country_id: str, country_data: CountryUpdate, db: Session = Depends(get_db)):
    """Update a country"""
    service = CountryService(db)
    return service.update(country_id, country_data)

@router.delete("/{country_id}", status_code=204)
def delete_country(
    country_id: str, 
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    db: Session = Depends(get_db)
):
    """Delete a country (soft or hard)"""
    service = CountryService(db)
    service.delete(country_id, soft_delete)
    return None

@router.get("/{country_id}/states", response_model=List)
def get_states_by_country(
    country_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all states for a specific country"""
    service = CountryService(db)
    return service.get_states_by_country(country_id, is_active)