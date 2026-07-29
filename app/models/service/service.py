from sqlalchemy import Column, DateTime, String, Text, func

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(String(36), primary_key=True, index=True)

    service_code = Column(String(100), unique=True, nullable=False, index=True)

    service_name = Column(String(150), nullable=False)

    description = Column(Text, nullable=True)

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