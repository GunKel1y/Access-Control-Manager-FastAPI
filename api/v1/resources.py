
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.params import Depends

from typing import List, Annotated
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.resources import ResourcesModel
from service.resources_service import ResourcesService
from schemas.resources import RequestsResources, RequestResourceToUpdate, ResponsesResources
from core.database import get_db




router = APIRouter(prefix="/resources", tags=["Resources 🛠️"])


@router.get("", response_model=List[ResponsesResources])
async def get_resources(name: Annotated[str, Query(title="Название ресурса")] = None,
                        is_enabled: Annotated[bool, Query(title="Признак активности ресурса")] = None,
                        db: Session = Depends(get_db)):


    service = ResourcesService(db)

    if name is not None:
        service.get_all_resource(name=name)
    if is_enabled is not None:
        service.get_all_resource(is_enabled=is_enabled)

    return service.get_all_resource(name=name, is_enabled=is_enabled)


@router.get("/{resource_id}", response_model=ResponsesResources)
async def get_resources_item(resource_id: Annotated[UUID, Path(..., title="ID ресурса")],
                             db: Session = Depends(get_db)):


    service = ResourcesService(db)

    resource = service.get_by_id(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID не найден")

    return resource


@router.post("", response_model=ResponsesResources)
async def create_resources(resources_data: RequestsResources, db: Session = Depends(get_db)):


    service = ResourcesService(db)

    if service.is_duplicate_name(resources_data.name):
        raise HTTPException(status_code=409, detail="Ресурс с указанным названием уже существует")

    resource = create_resources(resources_data)

    return resource


@router.patch("/{resource_id}", response_model=ResponsesResources)
async def partial_update_resource(resource_id: UUID,
                                  update_resource_data: RequestResourceToUpdate,
                                  db: Session = Depends(get_db)):


    service = ResourcesService(db)

    resource = service.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID {resource_id} не найден")

    service.update_resource(update_data=update_resource_data, resource_id=resource_id)

    db.commit()
    db.refresh(resource)

    return resource