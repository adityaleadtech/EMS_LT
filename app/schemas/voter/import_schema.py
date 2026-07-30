# app/schemas/voter/import_schema.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ImportError(BaseModel):
    row: int
    voter_id: str
    error: str


class ImportResult(BaseModel):
    total_records: int = 0
    inserted_records: int = 0
    updated_records: int = 0
    failed_records: int = 0
    errors: List[ImportError] = []
    import_id: Optional[str] = None
    mapping_stats: Optional[Dict[str, int]] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 0.0
        return ((self.inserted_records + self.updated_records) / self.total_records) * 100