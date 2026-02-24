
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.params import Depends

from typing import List, Annotated
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.users import UserModel
from schemas.users import RequestsUsers, RequestUserToUpdate, ResponsesUsers
from core.database import get_db
from service.users_service import UserService




router = APIRouter(prefix="/users", tags=["Users 🧑🏻‍💻"])


@router.get("",response_model=List[ResponsesUsers])
async def get_users(search: Annotated[str, Query(title="Поиск по имени или почте пользователя")] = None,
                    is_active: Annotated[bool, Query(title="Признак активности пользователя")] = None,
                    db: Session = Depends(get_db)):


    service = UserService(db)
    users = service.get_all_users(search, is_active)

    return users


@router.get("/{user_id}", response_model=ResponsesUsers)
async def get_user(user_id: Annotated[UUID, Path(..., title="ID пользователя")],
                   db: Session = Depends(get_db)):


    service = UserService(db)

    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")

    return user


@router.post("", response_model=ResponsesUsers)
async def create_users(user_data: RequestsUsers, db: Session = Depends(get_db)):


    service = UserService(db)
    user = service.create_user(user_data)

    if user == "email":
        raise HTTPException(status_code=409, detail='Пользователь с указанным значением email уже существует')
    if user == "full_name":
        raise HTTPException(status_code=409, detail='Пользователь с указанным значением full_name уже существует')

    return user


@router.patch('/{user_id}', response_model=ResponsesUsers)
async def partial_update_user(
        user_id: Annotated[UUID, Path(title="ID пользователя")],
        update_user_data: RequestUserToUpdate,
        db: Session = Depends(get_db)):


    service = UserService(db)

    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")

    if update_user_data.is_active is not None:
        service.update_user(user_id, update_user_data)

    return user

