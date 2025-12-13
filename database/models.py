from sqlalchemy import Column, String, ForeignKey, Boolean, func, UUID, DateTime

import uuid

from database.base import Base
from database.schemas import AccessStatus


class UserModel(Base):
    __tablename__ = "Users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    email = Column(String, index=True, unique=True, nullable=True)
    full_name = Column(String, index=True, nullable=True)
    is_active = Column(Boolean, default=True)

class ResourcesModel(Base):
    __tablename__ = "Resources"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    name = Column(String, index=True, nullable=True, unique=True)
    description = Column(String)
    is_enabled = Column(Boolean)

class AccessModel(Base):
    __tablename__ = "Accesses"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("Users.id"))
    resource_id = Column(UUID, ForeignKey("Resources.id"))
    granted_at = Column(DateTime(timezone=True), index=True, nullable=True, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), index=True, nullable=True)
    status = Column(String, default=AccessStatus.ACTIVE)
    comment = Column(String)


