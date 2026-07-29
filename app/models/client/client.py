import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    client_code = Column(String(50), unique=True, nullable=False, index=True)
    client_name = Column(String(255), nullable=False)

    party = Column(String(150), nullable=False)

    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)

    is_mp = Column(Boolean, default=False)
    is_mla = Column(Boolean, default=False)
    is_minister = Column(Boolean, default=False)
    is_party_president = Column(Boolean, default=False)

    constituency = Column(String(255))

    office_address = Column(Text)

    state = Column(String(150))
    district = Column(String(150))
    city = Column(String(150))
    pincode = Column(String(20))

    office_logo = Column(Text)
    office_banner = Column(Text)

    description = Column(Text)

    is_active = Column(Boolean, default=True)

    created_by = Column(String(36), nullable=False)

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
    client_admin = relationship(
    "ClientAdmin",
    back_populates="client",
    uselist=False,
    cascade="all, delete-orphan",
)
    client_services = relationship(
    "ClientService",
    back_populates="client",
    cascade="all, delete-orphan",
)