from sqlalchemy.orm import Session
from typing import Optional, List, Type, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import status

from app.core.exceptions import (
    NotFoundException,
    DuplicateEntryException,
    DatabaseException,
    ValidationException
)


class BaseService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, model: Type, id: str, resource_name: str = "Resource") -> Any:
        """Get resource by ID with error handling"""
        try:
            obj = self.db.query(model).filter(model.id == id).first()
            if not obj:
                raise NotFoundException(resource_name, id)
            return obj
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to fetch {resource_name}: {str(e)}")

    def get_all(self, model: Type, skip: int = 0, limit: int = 100, 
                is_active: Optional[bool] = True, **filters) -> List[Any]:
        """Get all resources with filtering"""
        try:
            query = self.db.query(model)
            
            if is_active is not None:
                query = query.filter(model.is_active == is_active)
            
            # Apply additional filters
            for key, value in filters.items():
                if hasattr(model, key) and value is not None:
                    query = query.filter(getattr(model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"Failed to fetch resources: {str(e)}")

    def create(self, model: Type, data: Dict[str, Any], resource_name: str = "Resource") -> Any:
        """Create a new resource with error handling"""
        try:
            obj = model(**data)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            if "Duplicate entry" in str(e):
                # Extract field and value from error
                error_msg = str(e)
                field = "field"
                value = "value"
                if "Duplicate entry" in error_msg:
                    parts = error_msg.split("'")
                    if len(parts) >= 2:
                        value = parts[1]
                raise DuplicateEntryException(resource_name, field, value)
            raise DatabaseException(f"Failed to create {resource_name}: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to create {resource_name}: {str(e)}")

    def update(self, model: Type, id: str, data: Dict[str, Any], 
               resource_name: str = "Resource") -> Any:
        """Update a resource with error handling"""
        try:
            obj = self.get_by_id(model, id, resource_name)
            for key, value in data.items():
                if value is not None and hasattr(obj, key):
                    setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except NotFoundException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            if "Duplicate entry" in str(e):
                raise DuplicateEntryException(resource_name, "field", "value")
            raise DatabaseException(f"Failed to update {resource_name}: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to update {resource_name}: {str(e)}")

    def delete(self, model: Type, id: str, resource_name: str = "Resource", 
               soft_delete: bool = True) -> bool:
        """Delete a resource with error handling"""
        try:
            obj = self.get_by_id(model, id, resource_name)
            if soft_delete:
                obj.is_active = False
                self.db.commit()
            else:
                self.db.delete(obj)
                self.db.commit()
            return True
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to delete {resource_name}: {str(e)}")

    def check_existence(self, model: Type, **filters) -> bool:
        """Check if a resource exists"""
        try:
            query = self.db.query(model)
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            return query.first() is not None
        except Exception as e:
            raise DatabaseException(f"Failed to check existence: {str(e)}")

    def get_or_404(self, model: Type, id: str, resource_name: str = "Resource") -> Any:
        """Get resource or raise 404"""
        return self.get_by_id(model, id, resource_name)