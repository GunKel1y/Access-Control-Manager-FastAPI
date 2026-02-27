
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID



class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RequestsUsers(BaseUser):
    email: Annotated[EmailStr, Field(..., title='Электронная почта пользователя', min_length=5, max_length=255)]
    full_name: Annotated[str, Field(..., title='Ф.И.О. пользователя', min_length=5, max_length=255)]
    is_active: Annotated[bool, Field(True, title='Признак активности пользователя')]


class RequestUserToUpdate(BaseUser):
    is_active: Annotated[bool, Field(None, title='Признак активности пользователя')]


class ResponsesUsers(BaseUser):
    id: Annotated[UUID, Field(title='ID пользователя')]
    email: Annotated[str, Field( title='Электронная почта пользователя')]
    full_name: Annotated[str, Field(title='Ф.И.О. пользователя')]
    is_active: Annotated[bool, Field(title='Признак активности пользователя')]
