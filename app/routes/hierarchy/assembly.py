from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.assembly_service import AssemblyService
from app.schemas.hierarchy.assembly import AssemblyCreate, AssemblyUpdate, AssemblyResponse, AssemblyListResponse

router = APIRouter(prefix="/api/v1/hierarchy/assemblies", tags=["Hierarchy - Assemblies"])

@router.post("/", response_model=AssemblyResponse, status_code=201)
def create_assembly(assembly_data: AssemblyCreate, db: Session = Depends(get_db)):
    """Create a new Assembly"""
    service = AssemblyService(db)
    return service.create(assembly_data)

@router.get("/", response_model=List[AssemblyListResponse])
def get_assemblies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    pc_district_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all assemblies with optional filters"""
    service = AssemblyService(db)
    return service.get_all(skip, limit, pc_district_id, is_active)

@router.get("/{assembly_id}", response_model=AssemblyResponse)
def get_assembly(assembly_id: str, db: Session = Depends(get_db)):
    """Get a specific assembly by ID"""
    service = AssemblyService(db)
    return service.get_by_id(assembly_id)

@router.put("/{assembly_id}", response_model=AssemblyResponse)
def update_assembly(assembly_id: str, assembly_data: AssemblyUpdate, db: Session = Depends(get_db)):
    """Update an assembly"""
    service = AssemblyService(db)
    return service.update(assembly_id, assembly_data)

@router.delete("/{assembly_id}", status_code=204)
def delete_assembly(
    assembly_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete an assembly (soft or hard)"""
    service = AssemblyService(db)
    service.delete(assembly_id, soft_delete)
    return None

@router.get("/{assembly_id}/blocks", response_model=List)
def get_blocks_by_assembly(
    assembly_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all blocks for a specific assembly"""
    service = AssemblyService(db)
    return service.get_blocks_by_assembly(assembly_id, is_active)