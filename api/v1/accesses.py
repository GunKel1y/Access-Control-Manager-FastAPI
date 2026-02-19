
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.params import Depends

from sqlalchemy.orm import Session

from typing import List, Annotated
from uuid import UUID

from datetime import datetime
from time import timezone

from models.accesses import AccessModel
from models.users import UserModel
from models.resources import ResourcesModel
from schemas.accesses import RequestsAccesses, RequestAccessToUpdate, ResponsesAccesses, AccessStatus
from core.database import get_db




router = APIRouter(prefix="/access", tags=["Accesses 🗝️"])


@router.get("", response_model=List[ResponsesAccesses])
async def get_access(user_id: Annotated[UUID, Query(title="ID владельца доступа")] = None,
                     resource_id: Annotated[UUID, Query(title="ID ресурса")] = None,
                     status: Annotated[AccessStatus, Query(title="Текущее состояние доступа")] = None,
                     expires_at: Annotated[str, Query(title="Дата/время истечения доступа")] = None,
                     db: Session = Depends(get_db)):


    update_access_status(db)
    query = db.query(AccessModel)

    if user_id:
        query = query.filter(AccessModel.user_id == user_id)

    if resource_id:
        query = query.filter(AccessModel.resource_id == resource_id)

    if status:
        query = query.filter(AccessModel.status == status)

    if expires_at:
        date_format = "%d.%m.%Y %H:%M"
        try:
            expires_at_dt = datetime.strptime(expires_at, date_format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Неверный формат даты. Требуемый формат: {date_format}")
        query = query.filter(AccessModel.expires_at <= expires_at_dt)

    return query.all()


@router.get("/{access_id}", response_model=ResponsesAccesses)
async def get_access_item(access_id: Annotated[UUID, Path(title="ID доступа")], db: Session = Depends(get_db)):


    update_access_status(db)
    query = db.query(AccessModel)

    access = query.filter(AccessModel.id == access_id).first()
    if access is None:
        raise HTTPException(status_code=404, detail=f"Доступ с указанным ID не найден")

    return access


@router.post("", response_model=ResponsesAccesses)
async def create_access(access_data: RequestsAccesses, db: Session = Depends(get_db)):


    user = db.query(UserModel).filter(UserModel.id == access_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")
    if not user.is_active:
        raise HTTPException(status_code=400, detail=f"Пользователь с указанным ID неактивен")


    resource = db.query(ResourcesModel).filter(ResourcesModel.id == access_data.resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Ресурс с указанным ID не найден")
    if resource.is_enabled == False:
        raise HTTPException(status_code=400, detail="Ресурс с указанным ID неактивен")


    all_user_accesses = db.query(AccessModel).filter(AccessModel.user_id == access_data.user_id)
    for access in all_user_accesses:
        if access.resource_id == access_data.resource_id:
            raise HTTPException(status_code=400,
                                detail=f"Для указанного пользователя уже имеется доступ к данному ресурсу.")


    granted_at = datetime.now(timezone.utc)
    expires_at = access_data.expires_at

    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

    if  access_data.expires_at <= granted_at:
        raise HTTPException(status_code=400, detail="Дата окончания не может быть раньше или равна дате выдачи доступа")


    access_db = AccessModel(user_id=user.id,
                            resource_id=resource.id,
                            expires_at=expires_at,
                            status=access_data.status,
                            comment=access_data.comment)

    db.add(access_db)
    db.commit()
    db.refresh(access_db)

    return access_db


@router.patch("/{access_id}", response_model=ResponsesAccesses)
async def partial_update_access(access_id: Annotated[UUID, Path(title="ID доступа")],
                                update_access_data: RequestAccessToUpdate,
                                db: Session = Depends(get_db)):


    query = db.query(AccessModel)

    access = query.filter(AccessModel.id == access_id).first()
    if access is None:
        raise HTTPException(status_code=404, detail=f"Доступ с указанным ID {access_id} не найден")

    if access.status != AccessStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Статус доступа не активен, внести изменения невозможно")

    now = datetime.now(timezone.utc)
    expires_at = update_access_data.expires_at

    if update_access_data.expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if expires_at < now and update_access_data.status == AccessStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="При указанном статусе дата окончания не может быть раньше текущей даты"
            )
        access.expires_at = expires_at


    if update_access_data.status:
        if update_access_data.status == AccessStatus.REVOKED:
            access.expires_at = now
        if access.status == AccessStatus.ACTIVE and update_access_data.status == AccessStatus.EXPIRED:
            if update_access_data.expires_at > now:
                raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в истекший")
        if access.status == AccessStatus.EXPIRED and update_access_data.status == AccessStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Нельзя активировать истекший доступ")
        if access.status == AccessStatus.REVOKED and update_access_data.status == AccessStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в активный")
        if access.status == AccessStatus.EXPIRED and update_access_data.status == AccessStatus.REVOKED:
            raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в отозван")


    if update_access_data.comment:
        access.comment = update_access_data.comment

    db.commit()
    db.refresh(access)

    return access


def update_access_status(db: Session):
    from models.accesses import AccessModel
    from schemas.accesses import AccessStatus

    query = db.query(AccessModel)
    now = datetime.now()
    query.filter(
        (AccessModel.expires_at <= now) &
        (AccessModel.status != AccessStatus.REVOKED) &
        (AccessModel.status != AccessStatus.EXPIRED)).update(
                                                {AccessModel.status: AccessStatus.EXPIRED},
                                                        synchronize_session=False
                                                        )
    db.commit()

