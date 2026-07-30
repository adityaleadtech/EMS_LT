from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.services.hierarchy.country_service import CountryService
from app.schemas.hierarchy.country import CountryCreate, CountryUpdate, CountryResponse, CountryListResponse
from app.core.exceptions import NotFoundException, DuplicateEntryException, DatabaseException

router = APIRouter(prefix="/api/v1/hierarchy/countries", tags=["Hierarchy - Countries"])

@router.post(
    "/", 
    response_model=CountryResponse, 
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Country created successfully"},
        400: {"description": "Bad request"},
        409: {"description": "Duplicate entry"},
        500: {"description": "Internal server error"}
    }
)
def create_country(country_data: CountryCreate, db: Session = Depends(get_db)):
    """Create a new country"""
    try:
        service = CountryService(db)
        return service.create(country_data)
    except DuplicateEntryException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")

@router.get(
    "/",
    response_model=List[CountryListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Countries retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
def get_countries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, min_length=1, description="Search by name or code"),
    db: Session = Depends(get_db)
):
    """Get all countries with optional filters"""
    try:
        service = CountryService(db)
        return service.get_all(skip, limit, is_active, search)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")

@router.get(
    "/{country_id}",
    response_model=CountryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Country retrieved successfully"},
        404: {"description": "Country not found"},
        500: {"description": "Internal server error"}
    }
)
def get_country(country_id: str, db: Session = Depends(get_db)):
    """Get a specific country by ID"""
    try:
        service = CountryService(db)
        return service.get_by_id(country_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")

@router.put(
    "/{country_id}",
    response_model=CountryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Country updated successfully"},
        404: {"description": "Country not found"},
        409: {"description": "Duplicate entry"},
        500: {"description": "Internal server error"}
    }
)
def update_country(country_id: str, country_data: CountryUpdate, db: Session = Depends(get_db)):
    """Update a country"""
    try:
        service = CountryService(db)
        return service.update(country_id, country_data)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DuplicateEntryException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")

@router.delete(
    "/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Country deleted successfully"},
        404: {"description": "Country not found"},
        500: {"description": "Internal server error"}
    }
)
def delete_country(
    country_id: str, 
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    db: Session = Depends(get_db)
):
    """Delete a country (soft or hard)"""
    try:
        service = CountryService(db)
        service.delete(country_id, soft_delete)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")

@router.get(
    "/{country_id}/states",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "States retrieved successfully"},
        404: {"description": "Country not found"},
        500: {"description": "Internal server error"}
    }
)
def get_states_by_country(
    country_id: str,
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db)
):
    """Get all states for a specific country"""
    try:
        service = CountryService(db)
        return service.get_states_by_country(country_id, is_active)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Unexpected error: {str(e)}")