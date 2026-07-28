from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.pc_district import PCDistrict
from app.models.hierarchy.block import Block
from app.schemas.hierarchy.assembly import AssemblyCreate, AssemblyUpdate, AssemblyListResponse


class AssemblyService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, pc_district_id: Optional[str] = None, is_active: Optional[bool] = True) -> List[AssemblyListResponse]:
        query = self.db.query(Assembly)
        
        if pc_district_id:
            query = query.filter(Assembly.pc_district_id == pc_district_id)
        
        if is_active is not None:
            query = query.filter(Assembly.is_active == is_active)
        
        assemblies = query.offset(skip).limit(limit).all()
        
        result = []
        for assembly in assemblies:
            block_count = self.db.query(Block).filter(
                Block.assembly_id == assembly.id, 
                Block.is_active == True
            ).count()
            pc = self.db.query(PCDistrict).filter(PCDistrict.id == assembly.pc_district_id).first()
            result.append(AssemblyListResponse(
                **assembly.__dict__,
                block_count=block_count,
                pc_district_name=pc.name if pc else None,
                state_name=pc.state.name if pc and pc.state else None,
                country_name=pc.state.country.name if pc and pc.state and pc.state.country else None
            ))
        
        return result
    
    def get_by_id(self, assembly_id: str) -> Assembly:
        assembly = self.db.query(Assembly).filter(Assembly.id == assembly_id).first()
        if not assembly:
            raise HTTPException(status_code=404, detail="Assembly not found")
        return assembly
    
    def create(self, assembly_data: AssemblyCreate) -> Assembly:
        pc = self.db.query(PCDistrict).filter(PCDistrict.id == assembly_data.pc_district_id).first()
        if not pc:
            raise HTTPException(status_code=404, detail="PC District not found")
        
        assembly = Assembly(**assembly_data.model_dump())
        self.db.add(assembly)
        self.db.commit()
        self.db.refresh(assembly)
        return assembly
    
    def update(self, assembly_id: str, assembly_data: AssemblyUpdate) -> Assembly:
        assembly = self.get_by_id(assembly_id)
        update_data = assembly_data.model_dump(exclude_unset=True)
        
        if 'pc_district_id' in update_data and update_data['pc_district_id']:
            pc = self.db.query(PCDistrict).filter(PCDistrict.id == update_data['pc_district_id']).first()
            if not pc:
                raise HTTPException(status_code=404, detail="PC District not found")
        
        for key, value in update_data.items():
            setattr(assembly, key, value)
        self.db.commit()
        self.db.refresh(assembly)
        return assembly
    
    def delete(self, assembly_id: str, soft_delete: bool = True) -> bool:
        assembly = self.get_by_id(assembly_id)
        if soft_delete:
            assembly.is_active = False
            self.db.commit()
        else:
            self.db.delete(assembly)
            self.db.commit()
        return True
    
    def get_blocks_by_assembly(self, assembly_id: str, is_active: Optional[bool] = True) -> List[Block]:
        assembly = self.get_by_id(assembly_id)
        query = self.db.query(Block).filter(Block.assembly_id == assembly_id)
        if is_active is not None:
            query = query.filter(Block.is_active == is_active)
        return query.all()