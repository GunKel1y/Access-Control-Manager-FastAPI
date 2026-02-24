
from models.users import UserModel
from sqlalchemy import or_



class UsersRepository:

    def __init__(self, database):
        self.database = database

    def get_all(self, search, is_active):
        query = self.database.query(UserModel)

        if search:
            query = query.filter(
                or_(
                    UserModel.full_name.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            query = query.filter(UserModel.is_active == is_active)

        return query.all()

    def get_by_id(self, user_id):
        return self.database.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email):
        return self.database.query(UserModel).filter(UserModel.email == email).first()

    def get_by_name(self, name):
        return self.database.query(UserModel).filter(UserModel.full_name == name).first()

    def create_user(self, create_data):
        user = UserModel(
            email=create_data.email.strip(),
            full_name=create_data.full_name.strip(),
            is_active=create_data.is_active
        )

        self.database.add(user)
        self.database.flush()
        return user