from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SocialMediaBase(BaseModel):
    """Base Social Media schema"""
    
    # Social Media Platforms
    facebook: Optional[str] = Field(None, description="Facebook URL or username")
    twitter: Optional[str] = Field(None, description="Twitter/X URL or username")
    instagram: Optional[str] = Field(None, description="Instagram URL or username")
    youtube: Optional[str] = Field(None, description="YouTube URL or channel ID")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL or profile ID")
    whatsapp: Optional[str] = Field(None, description="WhatsApp number or link")
    telegram: Optional[str] = Field(None, description="Telegram handle or link")
    snapchat: Optional[str] = Field(None, description="Snapchat username or link")
    tiktok: Optional[str] = Field(None, description="TikTok URL or username")
    pinterest: Optional[str] = Field(None, description="Pinterest URL or username")
    reddit: Optional[str] = Field(None, description="Reddit username or subreddit")
    threads: Optional[str] = Field(None, description="Threads URL or username")
    discord: Optional[str] = Field(None, description="Discord server link or ID")
    clubhouse: Optional[str] = Field(None, description="Clubhouse handle or link")
    quora: Optional[str] = Field(None, description="Quora profile URL or username")
    tumblr: Optional[str] = Field(None, description="Tumblr blog URL")
    flickr: Optional[str] = Field(None, description="Flickr URL or username")
    vimeo: Optional[str] = Field(None, description="Vimeo URL or username")
    dailymotion: Optional[str] = Field(None, description="Dailymotion URL or username")
    periscope: Optional[str] = Field(None, description="Periscope URL or username")
    
    # Additional links
    website: Optional[str] = Field(None, description="Official website URL")
    blog: Optional[str] = Field(None, description="Blog URL")
    podcast: Optional[str] = Field(None, description="Podcast URL or feed")
    newsletter: Optional[str] = Field(None, description="Newsletter signup link")
    rss_feed: Optional[str] = Field(None, description="RSS feed URL")
    
    # Custom fields
    custom_field_1: Optional[str] = Field(None, description="Custom field 1")
    custom_field_2: Optional[str] = Field(None, description="Custom field 2")
    custom_field_3: Optional[str] = Field(None, description="Custom field 3")
    
    # Notes
    notes: Optional[str] = Field(None, description="Additional notes")
    
    is_active: Optional[bool] = True


class SocialMediaCreate(SocialMediaBase):
    """Social Media creation schema"""
    client_id: str = Field(..., description="Client ID")


class SocialMediaUpdate(SocialMediaBase):
    """Social Media update schema"""
    pass


class SocialMediaResponse(SocialMediaBase):
    """Social Media response schema"""
    id: Optional[str] = None
    client_id: str
    created_by: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class SocialMediaListResponse(BaseModel):
    """Social Media list response schema"""
    id: str
    client_id: str
    client_name: Optional[str] = None
    client_code: Optional[str] = None
    
    # Only show major platforms in list view
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    whatsapp: Optional[str] = None
    
    website: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SocialMediaBulkCreate(BaseModel):
    """Bulk create/update social media for multiple clients"""
    client_id: str
    social_media: SocialMediaCreate


class SocialMediaFilterParams(BaseModel):
    """Filter parameters for social media"""
    client_id: Optional[str] = None
    client_code: Optional[str] = None
    is_active: Optional[bool] = True
    has_facebook: Optional[bool] = None
    has_twitter: Optional[bool] = None
    has_instagram: Optional[bool] = None
    has_youtube: Optional[bool] = None