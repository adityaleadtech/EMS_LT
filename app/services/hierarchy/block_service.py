from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.block import Block
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.schemas.hierarchy.block import BlockCreate, BlockUpdate, BlockListResponse


class BlockService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, assembly_id: Optional[str] = None, is_active: Optional[bool] = True) -> List[BlockListResponse]:
        query = self.db.query(Block)
        
        if assembly_id:
            query = query.filter(Block.assembly_id == assembly_id)
        
        if is_active is not None:
            query = query.filter(Block.is_active == is_active)
        
        blocks = query.offset(skip).limit(limit).all()
        
        result = []
        for block in blocks:
            ward_count = self.db.query(PanchayatWard).filter(
                PanchayatWard.block_id == block.id, 
                PanchayatWard.is_active == True
            ).count()
            assembly = self.db.query(Assembly).filter(Assembly.id == block.assembly_id).first()
            result.append(BlockListResponse(
                **block.__dict__,
                panchayat_ward_count=ward_count,
                assembly_name=assembly.name if assembly else None,
                pc_district_name=assembly.pc_district.name if assembly and assembly.pc_district else None,
                state_name=assembly.pc_district.state.name if assembly and assembly.pc_district and assembly.pc_district.state else None,
                country_name=assembly.pc_district.state.country.name if assembly and assembly.pc_district and assembly.pc_district.state and assembly.pc_district.state.country else None
            ))
        
        return result
    
    def get_by_id(self, block_id: str) -> Block:
        block = self.db.query(Block).filter(Block.id == block_id).first()
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        return block
    
    def create(self, block_data: BlockCreate) -> Block:
        assembly = self.db.query(Assembly).filter(Assembly.id == block_data.assembly_id).first()
        if not assembly:
            raise HTTPException(status_code=404, detail="Assembly not found")
        
        block = Block(**block_data.model_dump())
        self.db.add(block)
        self.db.commit()
        self.db.refresh(block)
        return block
    
    def update(self, block_id: str, block_data: BlockUpdate) -> Block:
        block = self.get_by_id(block_id)
        update_data = block_data.model_dump(exclude_unset=True)
        
        if 'assembly_id' in update_data and update_data['assembly_id']:
            assembly = self.db.query(Assembly).filter(Assembly.id == update_data['assembly_id']).first()
            if not assembly:
                raise HTTPException(status_code=404, detail="Assembly not found")
        
        for key, value in update_data.items():
            setattr(block, key, value)
        self.db.commit()
        self.db.refresh(block)
        return block
    
    def delete(self, block_id: str, soft_delete: bool = True) -> bool:
        block = self.get_by_id(block_id)
        if soft_delete:
            block.is_active = False
            self.db.commit()
        else:
            self.db.delete(block)
            self.db.commit()
        return True
    
    def get_panchayat_wards_by_block(self, block_id: str, is_active: Optional[bool] = True) -> List[PanchayatWard]:
        block = self.get_by_id(block_id)
        query = self.db.query(PanchayatWard).filter(PanchayatWard.block_id == block_id)
        if is_active is not None:
            query = query.filter(PanchayatWard.is_active == is_active)
        return query.all()