from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.auth import admin_required
from app.models.platform_admin.platform_admin import PlatformAdmin
from app.services.news.news_service import NewsService
from app.schemas.news.news import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsListResponse,
    NewsFilterParams,
    NewsStatus
)
from app.core.exceptions import NotFoundException, DuplicateEntryException, DatabaseException

router = APIRouter(prefix="/api/v1/news", tags=["News"])


@router.post(
    "/",
    response_model=NewsResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "News created successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client not found"},
        409: {"description": "Duplicate slug"},
        500: {"description": "Internal server error"}
    }
)
def create_news(
    news_data: NewsCreate,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Create news for a client.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        return service.create(news_data, admin.id)
    except DuplicateEntryException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in create_news: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.put(
    "/{news_id}",
    response_model=NewsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "News updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "News not found"},
        409: {"description": "Duplicate slug"},
        500: {"description": "Internal server error"}
    }
)
def update_news(
    news_id: str,
    news_data: NewsUpdate,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Update existing news by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        return service.update(news_id, news_data, admin.id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DuplicateEntryException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in update_news: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[NewsListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "News retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
def get_all_news(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    client_code: Optional[str] = Query(None, description="Filter by client code"),
    status: Optional[NewsStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured"),
    is_breaking: Optional[bool] = Query(None, description="Filter by breaking"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in title, content, tags"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get all news with optional filters.
    
    Requires Platform Admin authentication.
    """
    try:
        # Build filter params
        filters = NewsFilterParams(
            client_id=client_id,
            client_code=client_code,
            status=status,
            category=category,
            is_featured=is_featured,
            is_breaking=is_breaking,
            is_active=is_active,
            search=search
        )
        
        # Parse dates if provided
        if from_date:
            filters.from_date = datetime.strptime(from_date, "%Y-%m-%d")
        if to_date:
            filters.to_date = datetime.strptime(to_date, "%Y-%m-%d")
        
        service = NewsService(db)
        return service.get_all(skip, limit, filters)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in get_all_news: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/client",
    response_model=List[NewsListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "News retrieved successfully"},
        400: {"description": "Bad request - missing client identifier"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Client not found"},
        500: {"description": "Internal server error"}
    }
)
def get_news_by_client(
    client_id: Optional[str] = Query(None, description="Client ID"),
    client_code: Optional[str] = Query(None, description="Client Code"),
    status: Optional[NewsStatus] = Query(None, description="Filter by status"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get news by client ID or client code.
    
    Requires Platform Admin authentication.
    At least one of client_id or client_code must be provided.
    """
    if not client_id and not client_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either client_id or client_code is required"
        )
    
    try:
        service = NewsService(db)
        return service.get_by_client(client_id, client_code, status)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in get_news_by_client: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/{news_id}",
    response_model=NewsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "News retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "News not found"},
        500: {"description": "Internal server error"}
    }
)
def get_news_by_id(
    news_id: str,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get news by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        news = service.get_by_id(news_id)
        return NewsResponse(**news.__dict__)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in get_news_by_id: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get(
    "/slug/{slug}",
    response_model=NewsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "News retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "News not found"},
        500: {"description": "Internal server error"}
    }
)
def get_news_by_slug(
    slug: str,
    increment_view: bool = Query(True, description="Increment view count"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get news by slug.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        news = service.get_by_slug(slug)
        
        # Increment view count if requested
        if increment_view:
            service.increment_view_count(news.id)
        
        return NewsResponse(**news.__dict__)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in get_news_by_slug: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.delete(
    "/{news_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "News deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "News not found"},
        500: {"description": "Internal server error"}
    }
)
def delete_news(
    news_id: str,
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Delete news by ID.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        service.delete(news_id, soft_delete)
        return None
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in delete_news: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/{news_id}/increment-view",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "View count incremented successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "News not found"},
        500: {"description": "Internal server error"}
    }
)
def increment_news_view(
    news_id: str,
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Increment view count for news.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        service.increment_view_count(news_id)
        return {"message": "View count incremented successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in increment_news_view: {str(e)}")
        import traceback
        traceback.print_exc()
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
def get_news_summary(
    admin: PlatformAdmin = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for news.
    
    Requires Platform Admin authentication.
    """
    try:
        service = NewsService(db)
        return service.get_summary()
    except DatabaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Error in get_news_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )