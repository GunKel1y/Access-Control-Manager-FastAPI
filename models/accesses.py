
from sqlalchemy import Column, String, ForeignKey, func, UUID, DateTime
from core.database import Base
from schemas.accesses import AccessStatus
import uuid





class AccessModel(Base):
    __tablename__ = "Accesses"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("Users.id"))
    resource_id = Column(UUID, ForeignKey("Resources.id"))
    granted_at = Column(DateTime(timezone=True), index=True, nullable=True, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), index=True, nullable=True)
    status = Column(String, default=AccessStatus.ACTIVE)
    comment = Column(String)