
from sqlalchemy import Column, String, Boolean, UUID
from core.database import Base
import uuid





class UserModel(Base):
    __tablename__ = "Users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    email = Column(String, index=True, unique=True, nullable=True)
    full_name = Column(String, index=True, nullable=True)
    is_active = Column(Boolean, default=True)