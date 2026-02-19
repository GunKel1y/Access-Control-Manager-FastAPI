
from sqlalchemy import Column, String, Boolean, UUID
from core.database import Base
import uuid





class ResourcesModel(Base):
    __tablename__ = "Resources"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    name = Column(String, index=True, nullable=True, unique=True)
    description = Column(String)
    is_enabled = Column(Boolean, default=True)