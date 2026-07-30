# app/schemas/export.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============ Export Schemas ============

class ExportRequest(BaseModel):
    client_id: str = Field(..., description="Client UUID")
    export_type: str = Field("EXCEL", description="EXCEL, CSV, PDF")
    format: Optional[str] = Field("xlsx", description="File format extension")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters to apply")
    columns: Optional[List[str]] = Field(None, description="Columns to export")
    group_id: Optional[str] = Field(None, description="Export only this group")

class ExportResponse(BaseModel):
    export_id: str
    filename: str
    total_records: int
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None

# ============ Export Log Schemas ============

class ExportLogBase(BaseModel):
    client_id: str
    export_type: str
    filename: str
    total_records: int
    filter_criteria: Optional[Dict[str, Any]] = None

class ExportLogCreate(ExportLogBase):
    exported_by: Optional[str] = None

class ExportLogResponse(ExportLogBase):
    id: str
    exported_by: Optional[str]
    exported_at: datetime
    
    class Config:
        from_attributes = True