from uuid import UUID
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.params import Depends

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from typing import List, Annotated

from email_validator import validate_email, EmailNotValidError

from database.base import Base, engine, update_access_status
from database.session import get_db
from database.models import UserModel, ResourcesModel, AccessModel
from database.schemas import AccessStatus, RequestsUsers, RequestsResources, \
    RequestsAccesses, RequestAccessToUpdate, ResponsesUsers, ResponsesResources, ResponsesAccesses, RequestUserToUpdate, \
    RequestResourceToUpdate



app = FastAPI(title="Access Control Manager")
Base.metadata.create_all(bind=engine)



@app.get("/users", response_model=List[ResponsesUsers])
async def get_users(search: Annotated[str, Query(title="Поиск по имени или почте пользователя")] = None,
                    is_active: Annotated[bool, Query(title="Признак активности пользователя")] = None,
                    db: Session = Depends(get_db)):

    query = db.query(UserModel)


    if search:
        query = query.filter(or_(UserModel.full_name.ilike(f"%{search}%"), UserModel.email.ilike(f"%{search}%")))

    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)


    users = query.all()
    if not users:
        raise HTTPException(status_code=404, detail="Пользователи не найдены")


    return users

@app.get("/users/{user_id}", response_model=ResponsesUsers)
async def get_user(user_id: Annotated[UUID, Path(..., title="ID пользователя")],
                   db: Session = Depends(get_db)):

    query = db.query(UserModel)


    user = query.filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")


    return user

@app.post("/users", response_model=ResponsesUsers)
async def create_users(user_data: RequestsUsers, db: Session = Depends(get_db)):

    query = db.query(UserModel)

    user_data.email = user_data.email.strip()
    user_data.full_name = user_data.full_name.strip()

    try:
        validate_email(user_data.email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Неверный формат почты. Требуется формат: username@example.com")

    duplicate_email = query.filter(func.lower(UserModel.email) == (user_data.email).lower()).first()
    if duplicate_email:
        raise HTTPException(status_code=409, detail="Пользователь с указанным email уже существует")

    append_user = UserModel(email=user_data.email, full_name=user_data.full_name, is_active=user_data.is_active)

    db.add(append_user)
    db.commit()
    db.refresh(append_user)


    return append_user

@app.patch('/users/{user_id}', response_model=ResponsesUsers)
async def partial_update_user(
        user_id: Annotated[UUID, Path(title="ID пользователя")],
        update_user_data: RequestUserToUpdate,
        db: Session = Depends(get_db)):
    query = db.query(UserModel)

    user = query.filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")

    if update_user_data.email:
        user.email = update_user_data.email

    if update_user_data.full_name:
        user.full_name = update_user_data.full_name

    if update_user_data.is_active is not None:
        user.is_active = update_user_data.is_active

    db.commit()
    db.refresh(user)

    return user




@app.get("/resources", response_model=List[ResponsesResources])
async def get_resources(is_enabled: Annotated[bool, Query(title="Признак активности ресурса")] = None,
                        db: Session = Depends(get_db)):

    query = db.query(ResourcesModel)

    if is_enabled is not None:
        query = query.filter(ResourcesModel.is_enabled == is_enabled)

    if not query.all():
        raise HTTPException(status_code=404, detail="Ресурсы не найдены")

    return query.all()

@app.get("/resources/{resource_id}", response_model=ResponsesResources)
async def get_resources_item(resource_id: Annotated[UUID, Path(..., title="ID ресурса")], db: Session = Depends(get_db)):

    query = db.query(ResourcesModel)


    resource = query.filter(ResourcesModel.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID не найден")


    return resource

@app.post("/resources", response_model=ResponsesResources)
async def create_resources(resources_data: RequestsResources, db: Session = Depends(get_db)):

    query = db.query(ResourcesModel)


    duplicate_resource = query.filter(func.lower(ResourcesModel.name) == resources_data.name.lower()).first()
    if duplicate_resource is not None:
        raise HTTPException(status_code=409, detail="Ресурс с указанным названием уже существует")
    append_resource = ResourcesModel(name=resources_data.name, description=resources_data.description, is_enabled=resources_data.is_enabled)


    db.add(append_resource)
    db.commit()
    db.refresh(append_resource)


    return append_resource

@app.patch("/resources/{resource_id}", response_model=ResponsesResources)
async def partial_update_resource(resource_id: UUID | None,
                                  update_resource_data: RequestResourceToUpdate,
                                  db: Session = Depends(get_db)):

    query = db.query(ResourcesModel)

    resource = query.filter(ResourcesModel.id == resource_id).first()

    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID {resource_id} не найден")

    if update_resource_data.name:
        raise HTTPException(status_code=400, detail="Невозможно изменить название ресурса")

    if update_resource_data.description:
        raise HTTPException(status_code=400, detail="Невозможно изменить описание ресурса")

    if update_resource_data.is_enabled is None:
        raise HTTPException(status_code=400, detail="Обязательный параметр 'is_enabled' не был передан")

    resource.is_enabled = update_resource_data.is_enabled
    db.commit()
    db.refresh(resource)

    return resource




@app.get("/access", response_model=List[ResponsesAccesses])
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

@app.get("/access/{access_id}", response_model=ResponsesAccesses)
async def get_access_item(access_id: Annotated[UUID, Path(title="ID доступа")], db: Session = Depends(get_db)):
    update_access_status(db)

    query = db.query(AccessModel)

    access = query.filter(AccessModel.id == access_id).first()
    if access is None:
        raise HTTPException(status_code=404, detail=f"Доступ с указанным ID {access_id} не найден")

    return access

@app.post("/access", response_model=ResponsesAccesses)
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

@app.patch("/access/{access_id}", response_model=ResponsesAccesses)
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
            raise HTTPException(status_code=400, detail="При указанном статусе дата окончания не может быть раньше текущей даты")
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




