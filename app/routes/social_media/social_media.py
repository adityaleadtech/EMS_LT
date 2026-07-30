from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.auth import admin_required
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.services.social_media.social_media_service import SocialMediaService
from app.schemas.social_media.social_media import (
    SocialMediaCreate,
    SocialMediaUpdate,
    SocialMediaResponse,
    SocialMediaListResponse
)
from app.core.exceptions import NotFoundException, DuplicateEntryException, DatabaseException

router = APIRouter(prefix="/api/v1/social-media", tags=["Social Media"])


@router.post(
    "/",
    response_model=SocialMediaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Social media created successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client not found"},
        409: {"description": "Social media already exists for this client"},
        500: {"description": "Internal server error"}
    }
)
def create_social_media(
    social_media_data: SocialMediaCreate,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Create social media for a client.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        return service.create(social_media_data, admin.id)
    except DuplicateEntryException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.put(
    "/{social_media_id}",
    response_model=SocialMediaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Social media updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Social media not found"},
        500: {"description": "Internal server error"}
    }
)
def update_social_media(
    social_media_id: str,
    social_media_data: SocialMediaUpdate,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Update existing social media by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        return service.update(social_media_id, social_media_data, admin.id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.put(
    "/client/{client_id}/upsert",
    response_model=SocialMediaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Social media created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client not found"},
        500: {"description": "Internal server error"}
    }
)
def upsert_social_media(
    client_id: str,
    social_media_data: SocialMediaCreate,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Create or update social media for a client (Upsert).
    
    If social media exists, update it. If not, create new.
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        return service.upsert(client_id, social_media_data, admin.id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[SocialMediaListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Social media retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
def get_all_social_media(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    client_code: Optional[str] = Query(None, description="Filter by client code"),
    has_facebook: Optional[bool] = Query(None, description="Filter by Facebook presence"),
    has_twitter: Optional[bool] = Query(None, description="Filter by Twitter presence"),
    has_instagram: Optional[bool] = Query(None, description="Filter by Instagram presence"),
    has_youtube: Optional[bool] = Query(None, description="Filter by YouTube presence"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get all social media records with optional filters.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        return service.get_all(
            skip=skip,
            limit=limit,
            is_active=is_active,
            client_id=client_id,
            client_code=client_code,
            has_facebook=has_facebook,
            has_twitter=has_twitter,
            has_instagram=has_instagram,
            has_youtube=has_youtube
        )
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/client",
    response_model=SocialMediaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Social media retrieved successfully"},
        400: {"description": "Bad request - missing client identifier"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client or social media not found"},
        500: {"description": "Internal server error"}
    }
)
def get_social_media_by_client(
    client_id: Optional[str] = Query(None, description="Client ID"),
    client_code: Optional[str] = Query(None, description="Client Code"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get social media by client ID or client code.
    
    Requires Platform Admin authentication.
    At least one of client_id or client_code must be provided.
    """
    if not client_id and not client_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either client_id or client_code is required"
        )
    
    try:
        service = SocialMediaService(db)
        return service.get_by_client(client_id, client_code)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/{social_media_id}",
    response_model=SocialMediaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Social media retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Social media not found"},
        500: {"description": "Internal server error"}
    }
)
def get_social_media_by_id(
    social_media_id: str,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get social media by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        from app.models.social_media import SocialMedia
        social_media = service.db.query(SocialMedia).filter(
            SocialMedia.id == social_media_id
        ).first()
        
        if not social_media:
            raise NotFoundException("Social Media", social_media_id)
        
        return SocialMediaResponse(**social_media.__dict__)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete(
    "/{social_media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Social media deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Social media not found"},
        500: {"description": "Internal server error"}
    }
)
def delete_social_media(
    social_media_id: str,
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Delete social media by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        service.delete(social_media_id, soft_delete)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete(
    "/client/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Social media deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client not found"},
        500: {"description": "Internal server error"}
    }
)
def delete_social_media_by_client(
    client_id: str,
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Delete social media by client ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        service.delete_by_client(client_id, soft_delete)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/summary/stats",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Summary retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
def get_social_media_summary(
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for social media.
    
    Requires Platform Admin authentication.
    """
    try:
        service = SocialMediaService(db)
        return service.get_summary()
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )