from typing import Optional, Annotated

from enum import Enum

from datetime import datetime

from pydantic import BaseModel, Field

from uuid import UUID



class AccessStatus(str, Enum):
    ACTIVE = "Активный"
    EXPIRED = "Истекший"
    REVOKED = "Отозван"


class BaseUser(BaseModel):
    id: Annotated[UUID, Field(None, title='ID пользователя')] = None

    class Config:
        orm_mode = True

class BaseResources(BaseModel):
    id: Annotated[UUID, Field(None, title='ID ресурса')]

    class Config:
        orm_mode = True

class BaseAccess(BaseModel):
    id: Annotated[UUID, Field(None, title='ID доступа')]

    class Config:
        orm_mode = True
        granted_at: datetime
        expires_at: datetime
        json_encoders = {
            datetime: lambda v: v.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        }

class RequestsUsers(BaseUser):
    email: Annotated[str, Field(..., title='Электронная почта пользователя', min_length=5, max_length=255)]
    full_name: Annotated[str, Field(..., title='Ф.И.О. пользователя', min_length=5, max_length=255)]
    is_active: Annotated[bool, Field(True, title='Признак активности пользователя')]

class RequestUserToUpdate(BaseResources):
    email: Annotated[Optional[str], Field(None, title='Электронная почта пользователя', min_length=5, max_length=255)]
    full_name: Annotated[Optional[str], Field(None, title='Ф.И.О. пользователя', min_length=5, max_length=255)]
    is_active: Annotated[Optional[bool], Field(True, title='Признак активности пользователя')]

class RequestsResources(BaseResources):
    name: Annotated[str, Field(..., title='Имя ресурса', min_length=2, max_length=100)]
    description: Annotated[str, Field(title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[bool, Field(True, title='Признак активности ресурса')]

class RequestResourceToUpdate(BaseResources):
    description: Annotated[Optional[str], Field(None, title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[Optional[bool], Field(True, title='Признак активности ресурса')]

class RequestsAccesses(BaseAccess):
    user_id: Annotated[UUID, Field(..., title="ID владельца доступа")]
    resource_id: Annotated[UUID, Field(..., title="ID ресурса")]
    expires_at: Annotated[datetime | str, Field(..., title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(AccessStatus.ACTIVE, title="Текущее состояние доступа")]
    comment: Annotated[str, Field(None, title="Примечание администратора", le=2000)]

class RequestAccessToUpdate(BaseAccess):
    expires_at: Annotated[datetime | str, Field(None, title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(AccessStatus.ACTIVE, title="Текущее состояние доступа")]
    comment: Annotated[Optional[str], Field(None, title="Примечание администратора", le=2000)]



class ResponsesUsers(BaseUser):
    id: Annotated[UUID, Field(title='ID пользователя')]
    email: Annotated[str, Field( title='Электронная почта пользователя', min_length=5, max_length=255)]
    full_name: Annotated[str, Field(title='Ф.И.О. пользователя', min_length=5, max_length=255)]
    is_active: Annotated[bool, Field(title='Признак активности пользователя')]

class ResponsesResources(BaseResources):
    id: Annotated[UUID, Field(title='ID ресурса')]
    name: Annotated[str, Field(title='Имя ресурса', min_length=2, max_length=100)]
    description: Annotated[str, Field(None, title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[bool, Field(title='Признак активности ресурса')]

class ResponsesAccesses(BaseAccess):
    id: Annotated[UUID, Field(title='ID доступа')]
    user_id: Annotated[UUID, Field(title="ID владельца доступа")]
    resource_id: Annotated[UUID, Field(title="ID ресурса")]
    granted_at: Annotated[datetime | str, Field(title="Дата/время выдачи доступа")]
    expires_at: Annotated[datetime | str, Field(title="Дата/время истечения доступа")]
    status: Annotated[AccessStatus, Field(title="Текущее состояние доступа")]
    comment: Annotated[Optional[str], Field(None, title="Примечание администратора", le=2000)]

