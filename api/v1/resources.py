
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

    return service.get_all_resource(name=name, is_enabled=is_enabled)


@router.get("/{resource_id}", response_model=ResponsesResources)
async def get_resources_item(resource_id: Annotated[UUID, Path(..., title="ID ресурса")],
                             db: Session = Depends(get_db)):


    service = ResourcesService(db)

    return service.get_by_id(resource_id)


@router.post("", response_model=ResponsesResources)
async def create_resources(resources_data: RequestsResources, db: Session = Depends(get_db)):


    service = ResourcesService(db)

    return service.create_resource(resources_data)


@router.patch("/{resource_id}", response_model=ResponsesResources)
async def partial_update_resource(resource_id: UUID,
                                  update_resource_data: RequestResourceToUpdate,
                                  db: Session = Depends(get_db)):


    service = ResourcesService(db)

    return service.update_resource(update_data=update_resource_data, resource_id=resource_id)