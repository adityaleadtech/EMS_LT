from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from uuid import uuid4
from datetime import datetime
import re

from app.models.client.client import Client
from app.models.news.news import News, NewsStatus
from app.schemas.news.news import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsListResponse,
    NewsFilterParams
)
from app.core.exceptions import NotFoundException, DuplicateEntryException, DatabaseException


class NewsService:
    def __init__(self, db: Session):
        self.db = db

    def generate_slug(self, title: str) -> str:
        """Generate URL friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def get_client(self, client_id: str = None, client_code: str = None) -> Client:
        """Get client by ID or code"""
        if client_id:
            client = self.db.query(Client).filter(
                Client.id == client_id,
                Client.is_active == True
            ).first()
        elif client_code:
            client = self.db.query(Client).filter(
                Client.client_code == client_code,
                Client.is_active == True
            ).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either client_id or client_code is required"
            )
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return client

    def get_by_id(self, news_id: str) -> News:
        """Get news by ID"""
        news = self.db.query(News).filter(News.id == news_id).first()
        if not news:
            raise NotFoundException("News", news_id)
        return news

    def get_by_slug(self, slug: str) -> News:
        """Get news by slug"""
        news = self.db.query(News).filter(News.slug == slug).first()
        if not news:
            raise NotFoundException("News", slug)
        return news

    def get_all(self, skip: int = 0, limit: int = 100, 
                filters: Optional[NewsFilterParams] = None) -> List[NewsListResponse]:
        """Get all news with filters"""
        try:
            query = self.db.query(News)
            
            if filters:
                if filters.client_id:
                    query = query.filter(News.client_id == filters.client_id)
                elif filters.client_code:
                    client = self.db.query(Client).filter(
                        Client.client_code == filters.client_code,
                        Client.is_active == True
                    ).first()
                    if client:
                        query = query.filter(News.client_id == client.id)
                    else:
                        return []
                
                if filters.status:
                    query = query.filter(News.status == filters.status)
                
                if filters.category:
                    query = query.filter(News.category == filters.category)
                
                if filters.is_featured is not None:
                    query = query.filter(News.is_featured == filters.is_featured)
                
                if filters.is_breaking is not None:
                    query = query.filter(News.is_breaking == filters.is_breaking)
                
                if filters.is_active is not None:
                    query = query.filter(News.is_active == filters.is_active)
                
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.filter(
                        or_(
                            News.title.ilike(search_term),
                            News.content.ilike(search_term),
                            News.summary.ilike(search_term),
                            News.tags.ilike(search_term),
                            News.category.ilike(search_term)
                        )
                    )
                
                if filters.from_date:
                    query = query.filter(News.created_at >= filters.from_date)
                if filters.to_date:
                    query = query.filter(News.created_at <= filters.to_date)
            
            query = query.order_by(News.created_at.desc())
            
            results = query.offset(skip).limit(limit).all()
            
            response = []
            for item in results:
                client = self.db.query(Client).filter(Client.id == item.client_id).first()
                response.append(NewsListResponse(
                    id=item.id,
                    client_id=item.client_id,
                    client_name=client.client_name if client else None,
                    client_code=client.client_code if client else None,
                    title=item.title,
                    slug=item.slug,
                    summary=item.summary,
                    category=item.category,
                    status=item.status,
                    is_featured=item.is_featured,
                    is_breaking=item.is_breaking,
                    featured_image=item.featured_image,
                    published_at=item.published_at,
                    view_count=item.view_count,
                    created_at=item.created_at
                ))
            
            return response
            
        except Exception as e:
            raise DatabaseException(f"Failed to fetch news: {str(e)}")

    def create(self, news_data: NewsCreate, admin_id: str) -> NewsResponse:
        """Create new news"""
        try:
            # Check if client exists
            client = self.db.query(Client).filter(
                Client.id == news_data.client_id,
                Client.is_active == True
            ).first()
            
            if not client:
                raise NotFoundException("Client", news_data.client_id)
            
            # Generate slug if not provided
            slug = news_data.slug or self.generate_slug(news_data.title)
            
            # Check for duplicate slug
            existing = self.db.query(News).filter(News.slug == slug).first()
            if existing:
                slug = f"{slug}-{str(uuid4())[:8]}"
            
            # Convert status to UPPERCASE ENUM value
            status_value = "DRAFT"  # Default
            
            if news_data.status:
                if isinstance(news_data.status, str):
                    # Convert to uppercase
                    status_value = news_data.status.upper()
                elif hasattr(news_data.status, 'value'):
                    # If it's an enum, get its value and uppercase it
                    status_value = news_data.status.value.upper()
                else:
                    status_value = str(news_data.status).upper()
            
            # Map to enum
            if status_value == "PUBLISHED":
                status = NewsStatus.PUBLISHED
            elif status_value == "ARCHIVED":
                status = NewsStatus.ARCHIVED
            else:
                status = NewsStatus.DRAFT
            
            # Create news
            news = News(
                id=str(uuid4()),
                client_id=news_data.client_id,
                created_by=admin_id,
                title=news_data.title,
                slug=slug,
                summary=news_data.summary or "",
                content=news_data.content,
                category=news_data.category,
                tags=news_data.tags,
                featured_image=news_data.featured_image,
                image_alt_text=news_data.image_alt_text,
                source=news_data.source,
                source_url=news_data.source_url,
                author=news_data.author,
                status=status,
                is_featured=news_data.is_featured or False,
                is_breaking=news_data.is_breaking or False,
                meta_title=news_data.meta_title,
                meta_description=news_data.meta_description,
                meta_keywords=news_data.meta_keywords,
                is_active=news_data.is_active if news_data.is_active is not None else True
            )
            
            # If status is published and no published_at, set it
            if status == NewsStatus.PUBLISHED and not news.published_at:
                news.published_at = datetime.utcnow()
            
            self.db.add(news)
            self.db.commit()
            self.db.refresh(news)
            
            return NewsResponse(**news.__dict__)
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            print(f"Error creating news: {str(e)}")
            import traceback
            traceback.print_exc()
            raise DatabaseException(f"Failed to create news: {str(e)}")

    def update(self, news_id: str, news_data: NewsUpdate, admin_id: str) -> NewsResponse:
        """Update existing news"""
        try:
            news = self.get_by_id(news_id)
            
            # Update fields
            update_data = news_data.model_dump(exclude_unset=True)
            
            if 'title' in update_data and update_data['title']:
                if 'slug' not in update_data or not update_data['slug']:
                    slug = self.generate_slug(update_data['title'])
                    update_data['slug'] = slug
                else:
                    slug = update_data['slug']
                    existing = self.db.query(News).filter(
                        News.slug == slug,
                        News.id != news_id
                    ).first()
                    if existing:
                        slug = f"{slug}-{str(uuid4())[:8]}"
                        update_data['slug'] = slug
            
            # Handle status update - convert to uppercase
            if 'status' in update_data and update_data['status']:
                if isinstance(update_data['status'], str):
                    status_value = update_data['status'].upper()
                    if status_value == "PUBLISHED":
                        update_data['status'] = NewsStatus.PUBLISHED
                    elif status_value == "ARCHIVED":
                        update_data['status'] = NewsStatus.ARCHIVED
                    else:
                        update_data['status'] = NewsStatus.DRAFT
                else:
                    update_data['status'] = update_data['status']
            
            # If status is changing to published, set published_at
            if 'status' in update_data and update_data['status'] == NewsStatus.PUBLISHED:
                if not news.published_at:
                    update_data['published_at'] = datetime.utcnow()
            
            for key, value in update_data.items():
                setattr(news, key, value)
            
            self.db.commit()
            self.db.refresh(news)
            
            return NewsResponse(**news.__dict__)
            
        except NotFoundException:
            raise
        except DuplicateEntryException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to update news: {str(e)}")

    def delete(self, news_id: str, soft_delete: bool = True) -> bool:
        """Delete news"""
        try:
            news = self.get_by_id(news_id)
            
            if soft_delete:
                news.is_active = False
                self.db.commit()
            else:
                self.db.delete(news)
                self.db.commit()
            
            return True
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to delete news: {str(e)}")

    def increment_view_count(self, news_id: str) -> bool:
        """Increment view count for news"""
        try:
            news = self.get_by_id(news_id)
            news.view_count += 1
            self.db.commit()
            return True
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to increment view count: {str(e)}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for news"""
        try:
            total_news = self.db.query(News).filter(News.is_active == True).count()
            draft_count = self.db.query(News).filter(
                News.status == NewsStatus.DRAFT,
                News.is_active == True
            ).count()
            published_count = self.db.query(News).filter(
                News.status == NewsStatus.PUBLISHED,
                News.is_active == True
            ).count()
            archived_count = self.db.query(News).filter(
                News.status == NewsStatus.ARCHIVED,
                News.is_active == True
            ).count()
            
            featured_count = self.db.query(News).filter(
                News.is_featured == True,
                News.is_active == True
            ).count()
            breaking_count = self.db.query(News).filter(
                News.is_breaking == True,
                News.is_active == True
            ).count()
            
            total_views = self.db.query(News).filter(
                News.is_active == True
            ).with_entities(
                func.sum(News.view_count)
            ).scalar() or 0
            
            return {
                'total_news': total_news,
                'draft_count': draft_count,
                'published_count': published_count,
                'archived_count': archived_count,
                'featured_count': featured_count,
                'breaking_count': breaking_count,
                'total_views': total_views,
                'average_views': round(total_views / total_news if total_news > 0 else 0, 2)
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to get summary: {str(e)}")

    def get_by_client(self, client_id: str = None, client_code: str = None, 
                      status: Optional[NewsStatus] = None) -> List[NewsListResponse]:
        """Get news by client"""
        client = self.get_client(client_id, client_code)
        
        query = self.db.query(News).filter(News.client_id == client.id)
        
        if status:
            query = query.filter(News.status == status)
        
        query = query.filter(News.is_active == True)
        query = query.order_by(News.created_at.desc())
        
        results = query.all()
        
        response = []
        for item in results:
            response.append(NewsListResponse(
                id=item.id,
                client_id=item.client_id,
                client_name=client.client_name,
                client_code=client.client_code,
                title=item.title,
                slug=item.slug,
                summary=item.summary,
                category=item.category,
                status=item.status,
                is_featured=item.is_featured,
                is_breaking=item.is_breaking,
                featured_image=item.featured_image,
                published_at=item.published_at,
                view_count=item.view_count,
                created_at=item.created_at
            ))
        
        return response