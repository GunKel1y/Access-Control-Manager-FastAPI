
from typing import Optional, Annotated
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum



class AccessStatus(str, Enum):
    ACTIVE = "Активный"
    EXPIRED = "Истекший"
    REVOKED = "Отозван"


class BaseAccess(BaseModel):
    granted_at: datetime
    expires_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        }


class RequestsAccesses(BaseAccess):
    user_id: Annotated[UUID, Field(..., title="ID владельца доступа")]
    resource_id: Annotated[UUID, Field(..., title="ID ресурса")]
    expires_at: Annotated[datetime, Field(..., title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(AccessStatus.ACTIVE, title="Текущее состояние доступа")]
    comment: Annotated[str, Field(None, title="Примечание администратора", max_length=2000)]


class RequestAccessToUpdate(BaseAccess):
    expires_at: Annotated[datetime, Field(None, title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(AccessStatus.ACTIVE, title="Текущее состояние доступа")]
    comment: Annotated[str, Field(None, title="Примечание администратора", max_length=2000)]


class ResponsesAccesses(BaseAccess):
    id: Annotated[UUID, Field(title='ID доступа')]
    user_id: Annotated[UUID, Field(title="ID владельца доступа")]
    resource_id: Annotated[UUID, Field(title="ID ресурса")]
    granted_at: Annotated[datetime, Field(title="Дата/время выдачи доступа")]
    expires_at: Annotated[datetime, Field(title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(title="Текущее состояние доступа")]
    comment: Annotated[Optional[str], Field(None, title="Примечание администратора", max_length=2000)]
