from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class NewsStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class NewsBase(BaseModel):
    """Base News schema"""
    
    title: str = Field(..., max_length=500, description="News title")
    slug: str = Field(..., max_length=500, description="URL friendly slug")
    summary: Optional[str] = Field(None, description="Short summary")
    content: str = Field(..., description="Full news content")
    
    category: Optional[str] = Field(None, max_length=100, description="News category")
    tags: Optional[str] = Field(None, description="Comma separated tags")
    
    featured_image: Optional[str] = Field(None, description="Featured image URL")
    image_alt_text: Optional[str] = Field(None, max_length=255, description="Image alt text")
    
    source: Optional[str] = Field(None, max_length=255, description="News source")
    source_url: Optional[str] = Field(None, description="Source URL")
    author: Optional[str] = Field(None, max_length=255, description="Author name")
    
    status: Optional[NewsStatus] = NewsStatus.DRAFT
    published_at: Optional[datetime] = None
    is_featured: Optional[bool] = False
    is_breaking: Optional[bool] = False
    
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO meta title")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, description="SEO meta keywords")
    
    is_active: Optional[bool] = True


class NewsCreate(NewsBase):
    """News creation schema"""
    client_id: str = Field(..., description="Client ID")
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Convert status to uppercase if it's a string"""
        if isinstance(v, str):
            v = v.upper()
            if v not in ["DRAFT", "PUBLISHED", "ARCHIVED"]:
                v = "DRAFT"
        return v


class NewsUpdate(BaseModel):
    """News update schema"""
    title: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = None
    featured_image: Optional[str] = None
    image_alt_text: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    status: Optional[NewsStatus] = None
    published_at: Optional[datetime] = None
    is_featured: Optional[bool] = None
    is_breaking: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Convert status to uppercase if it's a string"""
        if isinstance(v, str):
            v = v.upper()
            if v not in ["DRAFT", "PUBLISHED", "ARCHIVED"]:
                v = "DRAFT"
        return v


class NewsResponse(NewsBase):
    """News response schema"""
    id: str
    client_id: str
    created_by: str
    view_count: int
    share_count: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """News list response schema"""
    id: str
    client_id: str
    client_name: Optional[str] = None
    client_code: Optional[str] = None
    
    title: str
    slug: str
    summary: Optional[str]
    category: Optional[str]
    status: NewsStatus
    is_featured: bool
    is_breaking: bool
    featured_image: Optional[str]
    published_at: Optional[datetime]
    view_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NewsFilterParams(BaseModel):
    """Filter parameters for news"""
    client_id: Optional[str] = None
    client_code: Optional[str] = None
    status: Optional[NewsStatus] = None
    category: Optional[str] = None
    is_featured: Optional[bool] = None
    is_breaking: Optional[bool] = None
    is_active: Optional[bool] = True
    search: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None