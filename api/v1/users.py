
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




router = APIRouter(prefix="/users", tags=["Users 🧑🏻‍💻"])


@router.get("",response_model=List[ResponsesUsers])
async def get_users(search: Annotated[str, Query(title="Поиск по имени или почте пользователя")] = None,
                    is_active: Annotated[bool, Query(title="Признак активности пользователя")] = None,
                    db: Session = Depends(get_db)):


    query = db.query(UserModel)

    if search:
        query = query.filter(or_(UserModel.full_name.ilike(f"%{search}%"), UserModel.email.ilike(f"%{search}%")))

    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)

    users = query.all()

    return users


@router.get("/{user_id}", response_model=ResponsesUsers)
async def get_user(user_id: Annotated[UUID, Path(..., title="ID пользователя")],
                   db: Session = Depends(get_db)):


    query = db.query(UserModel)

    user = query.filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")

    return user


@router.post("", response_model=ResponsesUsers)
async def create_users(user_data: RequestsUsers, db: Session = Depends(get_db)):


    user_data.full_name = user_data.full_name.strip()

    append_user = UserModel(email=user_data.email, full_name=user_data.full_name, is_active=user_data.is_active)

    try:
        db.add(append_user)
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Пользователь с указанным email уже существует")

    db.refresh(append_user)

    return append_user


@router.patch('/{user_id}', response_model=ResponsesUsers)
async def partial_update_user(
        user_id: Annotated[UUID, Path(title="ID пользователя")],
        update_user_data: RequestUserToUpdate,
        db: Session = Depends(get_db)):


    query = db.query(UserModel)

    user = query.filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")

    if update_user_data.is_active is not None:
        user.is_active = update_user_data.is_active

    db.commit()
    db.refresh(user)

    return user

