
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.params import Depends

from sqlalchemy.orm import Session

from typing import List, Annotated
from uuid import UUID

from datetime import datetime, timezone

from models.accesses import AccessModel
from schemas.accesses import RequestsAccesses, RequestAccessToUpdate, ResponsesAccesses, AccessStatus
from service.access_service import AccessesService
from service.users_service import UserService
from service.resources_service import ResourcesService
from core.database import get_db




router = APIRouter(prefix="/accesses", tags=["Accesses 🗝️"])


@router.get("", response_model=List[ResponsesAccesses])
async def get_access(user_id: Annotated[UUID, Query(title="ID владельца доступа")] = None,
                     resource_id: Annotated[UUID, Query(title="ID ресурса")] = None,
                     status: Annotated[AccessStatus, Query(title="Текущее состояние доступа")] = None,
                     expires_at: Annotated[str, Query(title="Дата/время истечения доступа")] = None,
                     db: Session = Depends(get_db)):


    service = AccessesService(db)
    service.update_access_status()

    return service.search(
        user_id=user_id,
        resource_id=resource_id,
        status=status,
        expires_at=expires_at
    )


@router.get("/{access_id}", response_model=ResponsesAccesses)
async def get_access_item(access_id: Annotated[UUID, Path(title="ID доступа")], db: Session = Depends(get_db)):


    service = AccessesService(db)
    service.update_access_status()

    access = service.get_by_id(access_id)

    return access


@router.post("", response_model=ResponsesAccesses)
async def create_access(access_data: RequestsAccesses, db: Session = Depends(get_db)):


    user_service = UserService(db)
    resource_service = ResourcesService(db)
    access_service = AccessesService(db)

    user = user_service.check_user_for_access(access_data.user_id)
    resource = resource_service.check_resource_for_access(access_data.resource_id)
    access_service.is_duplicate_access(user_id=access_data.user_id,resource_id=access_data.resource_id)

    return access_service.create_access(access_data)


@router.patch("/{access_id}", response_model=ResponsesAccesses)
async def partial_update_access(access_id: Annotated[UUID, Path(title="ID доступа")],
                                update_access_data: RequestAccessToUpdate,
                                db: Session = Depends(get_db)):


    service = AccessesService(db)
    return service.update_access(access_id=access_id, update_data=update_access_data)


