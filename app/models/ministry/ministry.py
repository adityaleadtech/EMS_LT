import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    func,
)

from app.core.database import Base


class Ministry(Base):
    __tablename__ = "ministries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    ministry_name = Column(String(255), unique=True, nullable=False)

    description = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )