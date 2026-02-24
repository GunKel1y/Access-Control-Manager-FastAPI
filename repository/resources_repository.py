
from models.resources import ResourcesModel
from sqlalchemy import func



class ResourcesRepository:

    def __init__(self, database):
        self.database = database

    def get_all(self, name, is_enabled):

        query = self.database.query(ResourcesModel)

        if name:
            query = self.database.query(ResourcesModel).filter(ResourcesModel.name.ilike(f"%{name}%"))
        if is_enabled is not None:
            query = self.database.query(ResourcesModel).filter(ResourcesModel.is_enabled == is_enabled)

        return query.all()

    def get_by_id(self, resource_id):
        return self.database.query(ResourcesModel).filter(ResourcesModel.id == resource_id).first()

    def create_resource(self, create_data):

        resource = ResourcesModel(
            name = create_data.name,
            description = create_data.description,
            is_enabled = create_data.is_enabled
        )

        self.database.add(resource)
        self.database.flush()
        return resource

    def is_duplicate_name(self, name):
        if self.database.query(ResourcesModel).filter(func.lower(ResourcesModel.name) == name.lower()).first() is None:
            return False
        return True