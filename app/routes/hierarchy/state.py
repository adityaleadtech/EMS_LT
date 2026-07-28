from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.state_service import StateService
from app.schemas.hierarchy.state import StateCreate, StateUpdate, StateResponse, StateListResponse

router = APIRouter(prefix="/api/v1/hierarchy/states", tags=["Hierarchy - States"])

@router.post("/", response_model=StateResponse, status_code=201)
def create_state(state_data: StateCreate, db: Session = Depends(get_db)):
    """Create a new state"""
    service = StateService(db)
    return service.create(state_data)

@router.get("/", response_model=List[StateListResponse])
def get_states(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db)
):
    """Get all states with optional filters"""
    service = StateService(db)
    return service.get_all(skip, limit, country_id, is_active, search)

@router.get("/{state_id}", response_model=StateResponse)
def get_state(state_id: str, db: Session = Depends(get_db)):
    """Get a specific state by ID"""
    service = StateService(db)
    return service.get_by_id(state_id)

@router.put("/{state_id}", response_model=StateResponse)
def update_state(state_id: str, state_data: StateUpdate, db: Session = Depends(get_db)):
    """Update a state"""
    service = StateService(db)
    return service.update(state_id, state_data)

@router.delete("/{state_id}", status_code=204)
def delete_state(
    state_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete a state (soft or hard)"""
    service = StateService(db)
    service.delete(state_id, soft_delete)
    return None

@router.get("/{state_id}/pc-districts", response_model=List)
def get_pc_districts_by_state(
    state_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all PC districts for a specific state"""
    service = StateService(db)
    return service.get_pc_districts_by_state(state_id, is_active)