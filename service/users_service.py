from fastapi import HTTPException

from repository.users_repository import UsersRepository


class UserService:

    def __init__(self, database):
        self.db = database
        self.repo = UsersRepository(database)

    def create_user(self, user_data):

        if self.repo.get_by_email(user_data.email):
            return "email"

        if self.repo.get_by_name(user_data.full_name):
            return "full_name"

        user = self.repo.create_user(user_data)

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, *, user_id, update_data):

        user = self.repo.get_by_id(user_id)

        user.is_active = update_data.is_active

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id):
        return self.repo.get_by_id(user_id)

    def get_all_users(self, *, search, is_active):
        return self.repo.get_all(search, is_active)

    def check_user_for_access(self, user_id):
        user = self.repo.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail=f"Пользователь с указанным ID не найден")
        if user == "not active":
            raise HTTPException(status_code=422, detail=f"Пользователь с указанным ID неактивен")

        return "not active"

