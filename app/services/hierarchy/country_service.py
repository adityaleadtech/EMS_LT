from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import status
from app.models.hierarchy.country import Country
from app.models.hierarchy.state import State
from app.schemas.hierarchy.country import CountryCreate, CountryUpdate, CountryListResponse
from app.services.hierarchy.base_service import BaseService
from app.core.exceptions import DuplicateEntryException, DatabaseException


class CountryService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self, skip: int = 0, limit: int = 100, 
                is_active: Optional[bool] = True, 
                search: Optional[str] = None) -> List[CountryListResponse]:
        """Get all countries with search"""
        try:
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
        except Exception as e:
            raise DatabaseException(f"Failed to fetch countries: {str(e)}")

    def get_by_id(self, country_id: str) -> Country:
        """Get country by ID"""
        return self.get_or_404(Country, country_id, "Country")

    def create(self, country_data: CountryCreate) -> Country:
        """Create a new country"""
        try:
            # Check for duplicate code
            existing = self.db.query(Country).filter(
                Country.code == country_data.code
            ).first()
            if existing:
                raise DuplicateEntryException("Country", "code", country_data.code)
            
            # Check for duplicate name
            existing_name = self.db.query(Country).filter(
                Country.name == country_data.name
            ).first()
            if existing_name:
                raise DuplicateEntryException("Country", "name", country_data.name)
            
            return super().create(Country, country_data.model_dump(), "Country")
        except DuplicateEntryException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to create country: {str(e)}")

    def update(self, country_id: str, country_data: CountryUpdate) -> Country:
        """Update a country"""
        try:
            # Check if country exists
            country = self.get_by_id(country_id)
            
            # Check for duplicate code if code is being updated
            if country_data.code and country_data.code != country.code:
                existing = self.db.query(Country).filter(
                    Country.code == country_data.code
                ).first()
                if existing:
                    raise DuplicateEntryException("Country", "code", country_data.code)
            
            return super().update(Country, country_id, 
                                   country_data.model_dump(exclude_unset=True), 
                                   "Country")
        except DuplicateEntryException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update country: {str(e)}")

    def delete(self, country_id: str, soft_delete: bool = True) -> bool:
        """Delete a country"""
        return super().delete(Country, country_id, "Country", soft_delete)

    def get_states_by_country(self, country_id: str, is_active: Optional[bool] = True) -> List[State]:
        """Get states by country"""
        try:
            country = self.get_by_id(country_id)
            query = self.db.query(State).filter(State.country_id == country_id)
            if is_active is not None:
                query = query.filter(State.is_active == is_active)
            return query.all()
        except Exception as e:
            raise DatabaseException(f"Failed to fetch states for country: {str(e)}")