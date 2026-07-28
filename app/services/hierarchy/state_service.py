from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.state import State
from app.models.hierarchy.pc_district import PCDistrict
from app.models.hierarchy.country import Country
from app.schemas.hierarchy.state import StateCreate, StateUpdate, StateListResponse


class StateService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, country_id: Optional[str] = None, is_active: Optional[bool] = True, search: Optional[str] = None) -> List[StateListResponse]:
        query = self.db.query(State)
        
        if country_id:
            query = query.filter(State.country_id == country_id)
        
        if is_active is not None:
            query = query.filter(State.is_active == is_active)
        
        if search:
            query = query.filter(
                (State.name.ilike(f"%{search}%")) | 
                (State.code.ilike(f"%{search}%")) |
                (State.state_code.ilike(f"%{search}%"))
            )
        
        states = query.offset(skip).limit(limit).all()
        
        result = []
        for state in states:
            pc_count = self.db.query(PCDistrict).filter(
                PCDistrict.state_id == state.id, 
                PCDistrict.is_active == True
            ).count()
            country = self.db.query(Country).filter(Country.id == state.country_id).first()
            result.append(StateListResponse(
                **state.__dict__,
                pc_district_count=pc_count,
                country_name=country.name if country else None
            ))
        
        return result
    
    def get_by_id(self, state_id: str) -> State:
        state = self.db.query(State).filter(State.id == state_id).first()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
        return state
    
    def create(self, state_data: StateCreate) -> State:
        country = self.db.query(Country).filter(Country.id == state_data.country_id).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        state = State(**state_data.model_dump())
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        return state
    
    def update(self, state_id: str, state_data: StateUpdate) -> State:
        state = self.get_by_id(state_id)
        update_data = state_data.model_dump(exclude_unset=True)
        
        if 'country_id' in update_data and update_data['country_id']:
            country = self.db.query(Country).filter(Country.id == update_data['country_id']).first()
            if not country:
                raise HTTPException(status_code=404, detail="Country not found")
        
        for key, value in update_data.items():
            setattr(state, key, value)
        self.db.commit()
        self.db.refresh(state)
        return state
    
    def delete(self, state_id: str, soft_delete: bool = True) -> bool:
        state = self.get_by_id(state_id)
        if soft_delete:
            state.is_active = False
            self.db.commit()
        else:
            self.db.delete(state)
            self.db.commit()
        return True
    
    def get_pc_districts_by_state(self, state_id: str, is_active: Optional[bool] = True) -> List[PCDistrict]:
        state = self.get_by_id(state_id)
        query = self.db.query(PCDistrict).filter(PCDistrict.state_id == state_id)
        if is_active is not None:
            query = query.filter(PCDistrict.is_active == is_active)
        return query.all()