from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.models.hierarchy.block import Block
from app.models.hierarchy.polling_booth import PollingBooth
from app.schemas.hierarchy.panchayat_ward import PanchayatWardCreate, PanchayatWardUpdate, PanchayatWardListResponse


class PanchayatWardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, block_id: Optional[str] = None, is_active: Optional[bool] = True) -> List[PanchayatWardListResponse]:
        query = self.db.query(PanchayatWard)
        
        if block_id:
            query = query.filter(PanchayatWard.block_id == block_id)
        
        if is_active is not None:
            query = query.filter(PanchayatWard.is_active == is_active)
        
        wards = query.offset(skip).limit(limit).all()
        
        result = []
        for ward in wards:
            booth_count = self.db.query(PollingBooth).filter(
                PollingBooth.panchayat_ward_id == ward.id, 
                PollingBooth.is_active == True
            ).count()
            block = self.db.query(Block).filter(Block.id == ward.block_id).first()
            result.append(PanchayatWardListResponse(
                **ward.__dict__,
                polling_booth_count=booth_count,
                block_name=block.name if block else None,
                assembly_name=block.assembly.name if block and block.assembly else None,
                pc_district_name=block.assembly.pc_district.name if block and block.assembly and block.assembly.pc_district else None,
                state_name=block.assembly.pc_district.state.name if block and block.assembly and block.assembly.pc_district and block.assembly.pc_district.state else None,
                country_name=block.assembly.pc_district.state.country.name if block and block.assembly and block.assembly.pc_district and block.assembly.pc_district.state and block.assembly.pc_district.state.country else None
            ))
        
        return result
    
    def get_by_id(self, ward_id: str) -> PanchayatWard:
        ward = self.db.query(PanchayatWard).filter(PanchayatWard.id == ward_id).first()
        if not ward:
            raise HTTPException(status_code=404, detail="Panchayat Ward not found")
        return ward
    
    def create(self, ward_data: PanchayatWardCreate) -> PanchayatWard:
        block = self.db.query(Block).filter(Block.id == ward_data.block_id).first()
        if not block:
            raise HTTPException(status_code=404, detail="Block not found")
        
        ward = PanchayatWard(**ward_data.model_dump())
        self.db.add(ward)
        self.db.commit()
        self.db.refresh(ward)
        return ward
    
    def update(self, ward_id: str, ward_data: PanchayatWardUpdate) -> PanchayatWard:
        ward = self.get_by_id(ward_id)
        update_data = ward_data.model_dump(exclude_unset=True)
        
        if 'block_id' in update_data and update_data['block_id']:
            block = self.db.query(Block).filter(Block.id == update_data['block_id']).first()
            if not block:
                raise HTTPException(status_code=404, detail="Block not found")
        
        for key, value in update_data.items():
            setattr(ward, key, value)
        self.db.commit()
        self.db.refresh(ward)
        return ward
    
    def delete(self, ward_id: str, soft_delete: bool = True) -> bool:
        ward = self.get_by_id(ward_id)
        if soft_delete:
            ward.is_active = False
            self.db.commit()
        else:
            self.db.delete(ward)
            self.db.commit()
        return True
    
    def get_polling_booths_by_ward(self, ward_id: str, is_active: Optional[bool] = True) -> List[PollingBooth]:
        ward = self.get_by_id(ward_id)
        query = self.db.query(PollingBooth).filter(PollingBooth.panchayat_ward_id == ward_id)
        if is_active is not None:
            query = query.filter(PollingBooth.is_active == is_active)
        return query.all()