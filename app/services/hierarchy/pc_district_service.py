from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.pc_district import PCDistrict
from app.models.hierarchy.assembly import Assembly
from app.models.hierarchy.state import State
from app.schemas.hierarchy.pc_district import PCDistrictCreate, PCDistrictUpdate, PCDistrictListResponse


class PCDistrictService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, state_id: Optional[str] = None, is_active: Optional[bool] = True) -> List[PCDistrictListResponse]:
        query = self.db.query(PCDistrict)
        
        if state_id:
            query = query.filter(PCDistrict.state_id == state_id)
        
        if is_active is not None:
            query = query.filter(PCDistrict.is_active == is_active)
        
        pc_districts = query.offset(skip).limit(limit).all()
        
        result = []
        for pc in pc_districts:
            assembly_count = self.db.query(Assembly).filter(
                Assembly.pc_district_id == pc.id, 
                Assembly.is_active == True
            ).count()
            state = self.db.query(State).filter(State.id == pc.state_id).first()
            result.append(PCDistrictListResponse(
                **pc.__dict__,
                assembly_count=assembly_count,
                state_name=state.name if state else None,
                country_name=state.country.name if state and state.country else None
            ))
        
        return result
    
    def get_by_id(self, pc_district_id: str) -> PCDistrict:
        pc = self.db.query(PCDistrict).filter(PCDistrict.id == pc_district_id).first()
        if not pc:
            raise HTTPException(status_code=404, detail="PC District not found")
        return pc
    
    def create(self, pc_data: PCDistrictCreate) -> PCDistrict:
        state = self.db.query(State).filter(State.id == pc_data.state_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
        
        pc = PCDistrict(**pc_data.model_dump())
        self.db.add(pc)
        self.db.commit()
        self.db.refresh(pc)
        return pc
    
    def update(self, pc_district_id: str, pc_data: PCDistrictUpdate) -> PCDistrict:
        pc = self.get_by_id(pc_district_id)
        update_data = pc_data.model_dump(exclude_unset=True)
        
        if 'state_id' in update_data and update_data['state_id']:
            state = self.db.query(State).filter(State.id == update_data['state_id']).first()
            if not state:
                raise HTTPException(status_code=404, detail="State not found")
        
        for key, value in update_data.items():
            setattr(pc, key, value)
        self.db.commit()
        self.db.refresh(pc)
        return pc
    
    def delete(self, pc_district_id: str, soft_delete: bool = True) -> bool:
        pc = self.get_by_id(pc_district_id)
        if soft_delete:
            pc.is_active = False
            self.db.commit()
        else:
            self.db.delete(pc)
            self.db.commit()
        return True
    
    def get_assemblies_by_pc_district(self, pc_district_id: str, is_active: Optional[bool] = True) -> List[Assembly]:
        pc = self.get_by_id(pc_district_id)
        query = self.db.query(Assembly).filter(Assembly.pc_district_id == pc_district_id)
        if is_active is not None:
            query = query.filter(Assembly.is_active == is_active)
        return query.all()