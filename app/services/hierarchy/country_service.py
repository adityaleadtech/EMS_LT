from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException
from app.models.hierarchy.country import Country
from app.models.hierarchy import State
from app.schemas.hierarchy.country import CountryCreate, CountryUpdate, CountryListResponse


class CountryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = True, search: Optional[str] = None) -> List[CountryListResponse]:
        query = self.db.query(Country)
        
        if is_active is not None:
            query = query.filter(Country.is_active == is_active)
        
        if search:
            query = query.filter(
                (Country.name.ilike(f"%{search}%")) | 
                (Country.code.ilike(f"%{search}%")) |
                (Country.iso_code.ilike(f"%{search}%"))
            )
        
        countries = query.offset(skip).limit(limit).all()
        
        result = []
        for country in countries:
            state_count = self.db.query(State).filter(
                State.country_id == country.id, 
                State.is_active == True
            ).count()
            result.append(CountryListResponse(
                **country.__dict__,
                state_count=state_count
            ))
        
        return result
    
    def get_by_id(self, country_id: str) -> Country:
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        return country
    
    def create(self, country_data: CountryCreate) -> Country:
        country = Country(**country_data.model_dump())
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def update(self, country_id: str, country_data: CountryUpdate) -> Country:
        country = self.get_by_id(country_id)
        update_data = country_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(country, key, value)
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def delete(self, country_id: str, soft_delete: bool = True) -> bool:
        country = self.get_by_id(country_id)
        if soft_delete:
            country.is_active = False
            self.db.commit()
        else:
            self.db.delete(country)
            self.db.commit()
        return True
    
    def get_states_by_country(self, country_id: str, is_active: Optional[bool] = True) -> List[State]:
        country = self.get_by_id(country_id)
        query = self.db.query(State).filter(State.country_id == country_id)
        if is_active is not None:
            query = query.filter(State.is_active == is_active)
        return query.all()