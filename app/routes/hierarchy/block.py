from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.services.hierarchy.block_service import BlockService
from app.schemas.hierarchy.block import BlockCreate, BlockUpdate, BlockResponse, BlockListResponse

router = APIRouter(prefix="/api/v1/hierarchy/blocks", tags=["Hierarchy - Blocks"])

@router.post("/", response_model=BlockResponse, status_code=201)
def create_block(block_data: BlockCreate, db: Session = Depends(get_db)):
    """Create a new Block"""
    service = BlockService(db)
    return service.create(block_data)

@router.get("/", response_model=List[BlockListResponse])
def get_blocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    assembly_id: Optional[str] = None,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all blocks with optional filters"""
    service = BlockService(db)
    return service.get_all(skip, limit, assembly_id, is_active)

@router.get("/{block_id}", response_model=BlockResponse)
def get_block(block_id: str, db: Session = Depends(get_db)):
    """Get a specific block by ID"""
    service = BlockService(db)
    return service.get_by_id(block_id)

@router.put("/{block_id}", response_model=BlockResponse)
def update_block(block_id: str, block_data: BlockUpdate, db: Session = Depends(get_db)):
    """Update a block"""
    service = BlockService(db)
    return service.update(block_id, block_data)

@router.delete("/{block_id}", status_code=204)
def delete_block(
    block_id: str,
    soft_delete: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Delete a block (soft or hard)"""
    service = BlockService(db)
    service.delete(block_id, soft_delete)
    return None

@router.get("/{block_id}/panchayat-wards", response_model=List)
def get_panchayat_wards_by_block(
    block_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all panchayat wards for a specific block"""
    service = BlockService(db)
    return service.get_panchayat_wards_by_block(block_id, is_active)