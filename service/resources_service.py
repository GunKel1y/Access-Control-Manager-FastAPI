
from repository.resources_repository import ResourcesRepository



class ResourcesService:

    def __init__(self, db):
        self.db = db
        self.repo = ResourcesRepository(db)

    def get_by_id(self, resource_id):
        return self.repo.get_by_id(resource_id)

    def get_all_resource(self, *, name = None, is_enabled = None):
        return self.repo.get_all(name, is_enabled)

    def create_resource(self, create_data):
        return self.repo.create_resource(create_data)

    def is_duplicate_name(self, name):
        return self.repo.is_duplicate_name(name)

    def update_resource(self, *, resource_id, update_data):

        resource = self.repo.get_by_id(resource_id)

        if update_data.description is not None:
            resource.description = update_data.description
        if update_data.is_enabled is not None:
            resource.is_enabled = update_data.is_enabled

        self.db.commit()
        self.db.refresh(resource)
        return resource