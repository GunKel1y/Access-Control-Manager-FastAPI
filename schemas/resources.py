
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID



class BaseResources(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RequestsResources(BaseResources):
    name: Annotated[str, Field(..., title='Название ресурса', min_length=2, max_length=100)]
    description: Annotated[str, Field(title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[bool, Field(True, title='Признак активности ресурса')]


class RequestResourceToUpdate(BaseResources):
    description: Annotated[str, Field(None, title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[bool, Field(None, title='Признак активности ресурса')]


class ResponsesResources(BaseResources):
    id: Annotated[UUID, Field(title='ID ресурса')]
    name: Annotated[str, Field(title='Название ресурса', min_length=2, max_length=100)]
    description: Annotated[Optional[str], Field("", title='Описание ресурса', max_length=2000)]
    is_enabled: Annotated[bool, Field(title='Признак активности ресурса')]