from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.polling_booth import PollingBooth
from app.models.hierarchy.panchayat_ward import PanchayatWard
from app.schemas.hierarchy.polling_booth import PollingBoothCreate, PollingBoothUpdate, PollingBoothListResponse


class PollingBoothService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, ward_id: Optional[str] = None, is_active: Optional[bool] = True) -> List[PollingBoothListResponse]:
        query = self.db.query(PollingBooth)
        
        if ward_id:
            query = query.filter(PollingBooth.panchayat_ward_id == ward_id)
        
        if is_active is not None:
            query = query.filter(PollingBooth.is_active == is_active)
        
        booths = query.offset(skip).limit(limit).all()
        
        result = []
        for booth in booths:
            ward = self.db.query(PanchayatWard).filter(PanchayatWard.id == booth.panchayat_ward_id).first()
            result.append(PollingBoothListResponse(
                **booth.__dict__,
                panchayat_ward_name=ward.name if ward else None,
                block_name=ward.block.name if ward and ward.block else None,
                assembly_name=ward.block.assembly.name if ward and ward.block and ward.block.assembly else None,
                pc_district_name=ward.block.assembly.pc_district.name if ward and ward.block and ward.block.assembly and ward.block.assembly.pc_district else None,
                state_name=ward.block.assembly.pc_district.state.name if ward and ward.block and ward.block.assembly and ward.block.assembly.pc_district and ward.block.assembly.pc_district.state else None,
                country_name=ward.block.assembly.pc_district.state.country.name if ward and ward.block and ward.block.assembly and ward.block.assembly.pc_district and ward.block.assembly.pc_district.state and ward.block.assembly.pc_district.state.country else None
            ))
        
        return result
    
    def get_by_id(self, booth_id: str) -> PollingBooth:
        booth = self.db.query(PollingBooth).filter(PollingBooth.id == booth_id).first()
        if not booth:
            raise HTTPException(status_code=404, detail="Polling Booth not found")
        return booth
    
    def create(self, booth_data: PollingBoothCreate) -> PollingBooth:
        ward = self.db.query(PanchayatWard).filter(PanchayatWard.id == booth_data.panchayat_ward_id).first()
        if not ward:
            raise HTTPException(status_code=404, detail="Panchayat Ward not found")
        
        booth = PollingBooth(**booth_data.model_dump())
        self.db.add(booth)
        self.db.commit()
        self.db.refresh(booth)
        return booth
    
    def update(self, booth_id: str, booth_data: PollingBoothUpdate) -> PollingBooth:
        booth = self.get_by_id(booth_id)
        update_data = booth_data.model_dump(exclude_unset=True)
        
        if 'panchayat_ward_id' in update_data and update_data['panchayat_ward_id']:
            ward = self.db.query(PanchayatWard).filter(PanchayatWard.id == update_data['panchayat_ward_id']).first()
            if not ward:
                raise HTTPException(status_code=404, detail="Panchayat Ward not found")
        
        for key, value in update_data.items():
            setattr(booth, key, value)
        self.db.commit()
        self.db.refresh(booth)
        return booth
    
    def delete(self, booth_id: str, soft_delete: bool = True) -> bool:
        booth = self.get_by_id(booth_id)
        if soft_delete:
            booth.is_active = False
            self.db.commit()
        else:
            self.db.delete(booth)
            self.db.commit()
        return True