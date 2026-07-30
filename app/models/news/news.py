import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Integer,
    func
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class NewsStatus(str, enum.Enum):
    DRAFT = "DRAFT"        # Uppercase to match database
    PUBLISHED = "PUBLISHED"  # Uppercase to match database
    ARCHIVED = "ARCHIVED"    # Uppercase to match database


class News(Base):
    __tablename__ = "news"

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

    title = Column(
        String(500),
        nullable=False,
        index=True,
    )

    slug = Column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
    )

    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)

    category = Column(
        String(100),
        nullable=True,
        index=True,
    )

    tags = Column(Text, nullable=True)

    featured_image = Column(Text, nullable=True)
    image_alt_text = Column(String(255), nullable=True)

    source = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)

    status = Column(
        Enum(NewsStatus),
        default=NewsStatus.DRAFT,
        nullable=False,
    )

    published_at = Column(DateTime, nullable=True)
    is_featured = Column(Boolean, default=False)
    is_breaking = Column(Boolean, default=False)

    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)

    view_count = Column(
        Integer,
        default=0,
        nullable=False,
    )
    share_count = Column(
        Integer,
        default=0,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
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

    # Relationships
    client = relationship(
        "Client",
        back_populates="news",
        uselist=True,
    )