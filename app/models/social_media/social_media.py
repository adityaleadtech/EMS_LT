import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class SocialMedia(Base):
    __tablename__ = "social_media"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    client_id = Column(
        String(36),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    facebook = Column(Text, nullable=True)
    twitter = Column(Text, nullable=True)
    instagram = Column(Text, nullable=True)
    youtube = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    whatsapp = Column(Text, nullable=True)
    telegram = Column(Text, nullable=True)
    snapchat = Column(Text, nullable=True)
    tiktok = Column(Text, nullable=True)
    pinterest = Column(Text, nullable=True)
    reddit = Column(Text, nullable=True)
    threads = Column(Text, nullable=True)
    discord = Column(Text, nullable=True)
    clubhouse = Column(Text, nullable=True)
    quora = Column(Text, nullable=True)
    tumblr = Column(Text, nullable=True)
    flickr = Column(Text, nullable=True)
    vimeo = Column(Text, nullable=True)
    dailymotion = Column(Text, nullable=True)
    periscope = Column(Text, nullable=True)
    
    website = Column(Text, nullable=True)
    blog = Column(Text, nullable=True)
    podcast = Column(Text, nullable=True)
    newsletter = Column(Text, nullable=True)
    rss_feed = Column(Text, nullable=True)
    
    custom_field_1 = Column(Text, nullable=True)
    custom_field_2 = Column(Text, nullable=True)
    custom_field_3 = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_by = Column(
        String(36),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    client = relationship(
        "Client",
        back_populates="social_media",
        uselist=False,
        foreign_keys=[client_id]
    )