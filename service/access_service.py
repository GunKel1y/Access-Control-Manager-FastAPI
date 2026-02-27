
from fastapi import HTTPException

from repository.accesses_repository import AccessesRepository
from schemas.accesses import AccessStatus
from datetime import timezone, datetime


class AccessesService:

    def __init__(self, db):
        self.db = db
        self.repo = AccessesRepository(db)

    def get_by_id(self, access_id):
        access = self.repo.get_by_id(access_id)
        if access is None:
            raise HTTPException(status_code=404, detail=f"Доступ с указанным ID не найден")
        return access

    def search(self, *, user_id = None, resource_id = None, status = None, expires_at = None):
        return self.repo.search(user_id, resource_id, status, expires_at)

    def update_access_status(self):
        self.repo.update_access_status()

    def is_duplicate_access(self, *, user_id, resource_id):
        accesses = self.repo.search(user_id=user_id)

        for access in accesses:
            if access.resource_id == resource_id:
                raise HTTPException(status_code=400,
                                    detail=f"Для указанного пользователя уже имеется доступ к данному ресурсу.")

    def create_access(self, create_data):
        granted_at = datetime.now(timezone.utc)

        if create_data.expires_at.tzinfo is None:
            create_data.expires_at = create_data.expires_at.replace(tzinfo=timezone.utc)
        if create_data.expires_at <= granted_at:
            raise HTTPException(status_code=400,
                                detail="Дата окончания не может быть раньше или равна дате выдачи доступа")

        access = self.repo.create_access(create_data)

        self.db.commit()
        self.db.refresh(access)
        return access

    def update_access(self, *, access_id, update_data):
        access = self.repo.get_by_id(access_id)
        now = datetime.now(timezone.utc)

        if access is None:
            raise HTTPException(status_code=404, detail=f"Доступ с указанным ID не найден")
        if access.status != AccessStatus.ACTIVE:
            raise HTTPException(status_code=400, detail=f"Статус доступа не активен, внести изменения невозможно")


        if update_data.status == AccessStatus.REVOKED:
            access.expires_at = now
        if access.status == AccessStatus.ACTIVE and update_data.status == AccessStatus.EXPIRED:
            if update_data.expires_at > now:
                raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в истекший")
        if access.status == AccessStatus.EXPIRED and update_data.status == AccessStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Нельзя активировать истекший доступ")
        if access.status == AccessStatus.REVOKED and update_data.status == AccessStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в активный")
        if access.status == AccessStatus.EXPIRED and update_data.status == AccessStatus.REVOKED:
            raise HTTPException(status_code=400, detail="Текущий статус нельзя перевести в отозван")


        if update_data.expires_at:
            if update_data.expires_at.tzinfo is None:
                update_data.expires_at = update_data.expires_at.replace(tzinfo=timezone.utc)
            if update_data.expires_at < now and update_data.status == AccessStatus.ACTIVE:
                raise HTTPException(
                    status_code=400,
                    detail="При указанном статусе дата окончания не может быть раньше текущей даты"
                )
            if update_data.expires_at.tzinfo is None:
                update_data.expires_at = update_data.expires_at.replace(tzinfo=timezone.utc)


        access.expires_at = update_data.expires_at
        access.status = update_data.status
        access.comment = update_data.comment

        self.db.commit()
        self.db.refresh(access)
        return access



