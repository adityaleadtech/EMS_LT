from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from uuid import uuid4

from app.models.client.client import Client
from app.models.social_media.social_media import SocialMedia
from app.schemas.social_media.social_media import (
    SocialMediaCreate,
    SocialMediaUpdate,
    SocialMediaResponse,
    SocialMediaListResponse
)
from app.core.exceptions import NotFoundException, DuplicateEntryException, DatabaseException


class SocialMediaService:
    def __init__(self, db: Session):
        self.db = db

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

    def get_or_create_social_media(self, client_id: str) -> SocialMedia:
        """Get existing social media or create empty one for client"""
        social_media = self.db.query(SocialMedia).filter(
            SocialMedia.client_id == client_id
        ).first()
        
        if not social_media:
            # Create empty social media record
            social_media = SocialMedia(
                id=str(uuid4()),
                client_id=client_id,
                created_by="system",
                is_active=True
            )
            self.db.add(social_media)
            self.db.commit()
            self.db.refresh(social_media)
        
        return social_media

    def get_by_client(self, client_id: str = None, client_code: str = None) -> SocialMediaResponse:
        """Get social media by client ID or code"""
        client = self.get_client(client_id, client_code)
        
        social_media = self.db.query(SocialMedia).filter(
            SocialMedia.client_id == client.id
        ).first()
        
        if not social_media:
            # Return empty social media object
            return SocialMediaResponse(
                id=None,
                client_id=client.id,
                created_by="system",
                created_at=None,
                updated_at=None,
                is_active=True
            )
        
        return SocialMediaResponse(**social_media.__dict__)

    def get_all(self, skip: int = 0, limit: int = 100, 
                is_active: Optional[bool] = True,
                client_id: Optional[str] = None,
                client_code: Optional[str] = None,
                has_facebook: Optional[bool] = None,
                has_twitter: Optional[bool] = None,
                has_instagram: Optional[bool] = None,
                has_youtube: Optional[bool] = None) -> List[SocialMediaListResponse]:
        """Get all social media records with filters"""
        try:
            # Start with social media query
            query = self.db.query(SocialMedia)
            
            # Apply filters
            if is_active is not None:
                query = query.filter(SocialMedia.is_active == is_active)
            
            if client_id:
                query = query.filter(SocialMedia.client_id == client_id)
            
            if client_code:
                # Get client by code first
                client = self.db.query(Client).filter(
                    Client.client_code == client_code,
                    Client.is_active == True
                ).first()
                if client:
                    query = query.filter(SocialMedia.client_id == client.id)
                else:
                    # Return empty list if client not found
                    return []
            
            # Filter by platform presence (without joining clients)
            if has_facebook is not None:
                if has_facebook:
                    query = query.filter(SocialMedia.facebook.isnot(None))
                else:
                    query = query.filter(SocialMedia.facebook.is_(None))
            
            if has_twitter is not None:
                if has_twitter:
                    query = query.filter(SocialMedia.twitter.isnot(None))
                else:
                    query = query.filter(SocialMedia.twitter.is_(None))
            
            if has_instagram is not None:
                if has_instagram:
                    query = query.filter(SocialMedia.instagram.isnot(None))
                else:
                    query = query.filter(SocialMedia.instagram.is_(None))
            
            if has_youtube is not None:
                if has_youtube:
                    query = query.filter(SocialMedia.youtube.isnot(None))
                else:
                    query = query.filter(SocialMedia.youtube.is_(None))
            
            # Order by created_at descending
            query = query.order_by(SocialMedia.created_at.desc())
            
            results = query.offset(skip).limit(limit).all()
            
            response = []
            for item in results:
                # Get client info
                client = self.db.query(Client).filter(Client.id == item.client_id).first()
                response.append(SocialMediaListResponse(
                    id=item.id,
                    client_id=item.client_id,
                    client_name=client.client_name if client else None,
                    client_code=client.client_code if client else None,
                    facebook=item.facebook,
                    twitter=item.twitter,
                    instagram=item.instagram,
                    youtube=item.youtube,
                    linkedin=item.linkedin,
                    whatsapp=item.whatsapp,
                    website=item.website,
                    is_active=item.is_active,
                    created_at=item.created_at
                ))
            
            return response
            
        except Exception as e:
            print(f"Error in get_all: {str(e)}")
            import traceback
            traceback.print_exc()
            raise DatabaseException(f"Failed to fetch social media: {str(e)}")

    def create(self, social_media_data: SocialMediaCreate, admin_id: str) -> SocialMediaResponse:
        """Create new social media for a client"""
        try:
            # Check if client exists
            client = self.db.query(Client).filter(
                Client.id == social_media_data.client_id,
                Client.is_active == True
            ).first()
            
            if not client:
                raise NotFoundException("Client", social_media_data.client_id)
            
            # Check if social media already exists for this client
            existing = self.db.query(SocialMedia).filter(
                SocialMedia.client_id == social_media_data.client_id
            ).first()
            
            if existing:
                raise DuplicateEntryException(
                    "Social Media", 
                    "client_id", 
                    social_media_data.client_id
                )
            
            # Create new social media
            social_media = SocialMedia(
                id=str(uuid4()),
                client_id=social_media_data.client_id,
                created_by=admin_id,
                **social_media_data.model_dump(exclude={'client_id'})
            )
            
            self.db.add(social_media)
            self.db.commit()
            self.db.refresh(social_media)
            
            return SocialMediaResponse(**social_media.__dict__)
            
        except DuplicateEntryException:
            raise
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to create social media: {str(e)}")

    def update(self, social_media_id: str, social_media_data: SocialMediaUpdate, admin_id: str) -> SocialMediaResponse:
        """Update existing social media"""
        try:
            social_media = self.db.query(SocialMedia).filter(
                SocialMedia.id == social_media_id
            ).first()
            
            if not social_media:
                raise NotFoundException("Social Media", social_media_id)
            
            # Update fields
            update_data = social_media_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(social_media, key, value)
            
            self.db.commit()
            self.db.refresh(social_media)
            
            return SocialMediaResponse(**social_media.__dict__)
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to update social media: {str(e)}")

    def upsert(self, client_id: str, social_media_data: SocialMediaCreate, admin_id: str) -> SocialMediaResponse:
        """Create or update social media for a client"""
        try:
            # Check if client exists
            client = self.db.query(Client).filter(
                Client.id == client_id,
                Client.is_active == True
            ).first()
            
            if not client:
                raise NotFoundException("Client", client_id)
            
            # Check if social media exists
            existing = self.db.query(SocialMedia).filter(
                SocialMedia.client_id == client_id
            ).first()
            
            if existing:
                # Update existing
                update_data = social_media_data.model_dump(exclude={'client_id'}, exclude_unset=False)
                for key, value in update_data.items():
                    setattr(existing, key, value)
                self.db.commit()
                self.db.refresh(existing)
                return SocialMediaResponse(**existing.__dict__)
            else:
                # Create new
                social_media = SocialMedia(
                    id=str(uuid4()),
                    client_id=client_id,
                    created_by=admin_id,
                    **social_media_data.model_dump(exclude={'client_id'})
                )
                self.db.add(social_media)
                self.db.commit()
                self.db.refresh(social_media)
                return SocialMediaResponse(**social_media.__dict__)
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to upsert social media: {str(e)}")

    def delete(self, social_media_id: str, soft_delete: bool = True) -> bool:
        """Delete social media"""
        try:
            social_media = self.db.query(SocialMedia).filter(
                SocialMedia.id == social_media_id
            ).first()
            
            if not social_media:
                raise NotFoundException("Social Media", social_media_id)
            
            if soft_delete:
                social_media.is_active = False
                self.db.commit()
            else:
                self.db.delete(social_media)
                self.db.commit()
            
            return True
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to delete social media: {str(e)}")

    def delete_by_client(self, client_id: str, soft_delete: bool = True) -> bool:
        """Delete social media by client ID"""
        try:
            social_media = self.db.query(SocialMedia).filter(
                SocialMedia.client_id == client_id
            ).first()
            
            if not social_media:
                raise NotFoundException("Social Media for Client", client_id)
            
            if soft_delete:
                social_media.is_active = False
                self.db.commit()
            else:
                self.db.delete(social_media)
                self.db.commit()
            
            return True
            
        except NotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to delete social media: {str(e)}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for social media"""
        try:
            total_clients = self.db.query(Client).filter(Client.is_active == True).count()
            total_with_social = self.db.query(SocialMedia).filter(
                SocialMedia.is_active == True
            ).count()
            
            # Count clients with each platform
            platform_counts = {
                'facebook': self.db.query(SocialMedia).filter(
                    SocialMedia.facebook.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'twitter': self.db.query(SocialMedia).filter(
                    SocialMedia.twitter.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'instagram': self.db.query(SocialMedia).filter(
                    SocialMedia.instagram.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'youtube': self.db.query(SocialMedia).filter(
                    SocialMedia.youtube.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'linkedin': self.db.query(SocialMedia).filter(
                    SocialMedia.linkedin.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'whatsapp': self.db.query(SocialMedia).filter(
                    SocialMedia.whatsapp.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
                'website': self.db.query(SocialMedia).filter(
                    SocialMedia.website.isnot(None),
                    SocialMedia.is_active == True
                ).count(),
            }
            
            return {
                'total_clients': total_clients,
                'clients_with_social_media': total_with_social,
                'platform_counts': platform_counts,
                'coverage_percentage': round((total_with_social / total_clients * 100) if total_clients > 0 else 0, 2)
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to get summary: {str(e)}")