import uuid

from sqlalchemy import Column, ForeignKey, String

from app.core.database import Base


class ClientMinistry(Base):
    __tablename__ = "client_ministries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    client_id = Column(
        String(36),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    ministry_id = Column(
        String(36),
        ForeignKey("ministries.id", ondelete="CASCADE"),
        nullable=False,
    )