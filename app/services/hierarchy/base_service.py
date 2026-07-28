from sqlalchemy.orm import Session
from typing import Optional, List, Type, Dict, Any
from fastapi import HTTPException


class BaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, model: Type, id: str) -> Any:
        obj = self.db.query(model).filter(model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj
    
    def get_all(self, model: Type, skip: int = 0, limit: int = 100, is_active: Optional[bool] = True) -> List[Any]:
        query = self.db.query(model)
        if is_active is not None:
            query = query.filter(model.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    def create(self, model: Type, data: Dict[str, Any]) -> Any:
        obj = model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, model: Type, id: str, data: Dict[str, Any]) -> Any:
        obj = self.get_by_id(model, id)
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, model: Type, id: str, soft_delete: bool = True) -> bool:
        obj = self.get_by_id(model, id)
        if soft_delete:
            obj.is_active = False
            self.db.commit()
        else:
            self.db.delete(obj)
            self.db.commit()
        return True