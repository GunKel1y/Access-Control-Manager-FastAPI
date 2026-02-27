from fastapi import HTTPException

from repository.resources_repository import ResourcesRepository



class ResourcesService:

    def __init__(self, db):
        self.db = db
        self.repo = ResourcesRepository(db)

    def get_by_id(self, resource_id):
        resource = self.repo.get_by_id(resource_id)

        if resource is None:
            raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID не найден")

        return resource

    def get_all_resource(self, *, name = None, is_enabled = None):
        return self.repo.get_all(name, is_enabled)

    def create_resource(self, create_data):
        resource = self.repo.is_duplicate_name(create_data.name)
        if resource:
            raise HTTPException(status_code=409, detail="Ресурс с указанным названием уже существует")

        resource = self.repo.create_resource(create_data)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def update_resource(self, *, resource_id, update_data):

        resource = self.repo.get_by_id(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail=f"Ресурс с указанным ID {resource_id} не найден")

        if update_data.description is not None:
            resource.description = update_data.description
        if update_data.is_enabled is not None:
            resource.is_enabled = update_data.is_enabled

        self.db.commit()
        self.db.refresh(resource)
        return resource

    def check_resource_for_access(self, resource_id):
        resource = self.repo.get_by_id(resource_id)

        if resource is None:
            raise HTTPException(status_code=404, detail="Ресурс с указанным ID не найден")
        if resource == "not enabled":
            raise HTTPException(status_code=422, detail="Ресурс с указанным ID неактивен")

        return resource