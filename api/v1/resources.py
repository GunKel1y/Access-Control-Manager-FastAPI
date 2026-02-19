
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.params import Depends

from typing import List, Annotated
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from models.resources import ResourcesModel
from schemas.resources import RequestsResources, RequestResourceToUpdate, ResponsesResources
from core.database import get_db




router = APIRouter(prefix="/resources", tags=["Resources 🛠️"])


@router.get("", response_model=List[ResponsesResources])
async def get_resources(name: Annotated[str, Query(title="Название ресурса")] = None,
                        is_enabled: Annotated[bool, Query(title="Признак активности ресурса")] = None,
                        db: Session = Depends(get_db)):


    query = db.query(ResourcesModel)

    if is_enabled is not None:
        query = query.filter(ResourcesModel.is_enabled == is_enabled)

    if name is not None:
        query = query.filter(ResourcesModel.name == name)

    return query.all()


@router.get("/{resource_id}", response_model=ResponsesResources)
async def get_resources_item(resource_id: Annotated[UUID, Path(..., title="ID ресурса")],
                             db: Session = Depends(get_db)):


    query = db.query(ResourcesModel)

    resource = query.filter(ResourcesModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID не найден")

    return resource


@router.post("", response_model=ResponsesResources)
async def create_resources(resources_data: RequestsResources, db: Session = Depends(get_db)):


    query = db.query(ResourcesModel)

    duplicate_resource = query.filter(func.lower(ResourcesModel.name) == resources_data.name.lower()).first()
    if duplicate_resource is not None:
        raise HTTPException(status_code=409, detail="Ресурс с указанным названием уже существует")

    append_resource = ResourcesModel(
        name=resources_data.name,
        description=resources_data.description,
        is_enabled=resources_data.is_enabled)

    db.add(append_resource)
    db.commit()
    db.refresh(append_resource)

    return append_resource


@router.patch("/{resource_id}", response_model=ResponsesResources)
async def partial_update_resource(resource_id: UUID,
                                  update_resource_data: RequestResourceToUpdate,
                                  db: Session = Depends(get_db)):


    query = db.query(ResourcesModel)

    resource = query.filter(ResourcesModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID {resource_id} не найден")

    if update_resource_data.is_enabled is None:
        resource.is_enabled = update_resource_data.is_enabled

    db.commit()
    db.refresh(resource)

    return resource