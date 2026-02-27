from dns.e164 import query

from models.accesses import AccessModel
from datetime import datetime



class AccessesRepository:

    def __init__(self, database):
        self.database = database

    def get_all(self):
        return self.database.query(AccessModel).all()

    def search(self, user_id = None, resource_id = None, status = None, expires_at = None):

        query = self.database.query(AccessModel)

        if user_id is not None:
            query = query.filter(AccessModel.user_id == user_id)
        if resource_id is not None:
            query = query.filter(AccessModel.resource_id == resource_id)
        if status is not None:
            query = query.filter(AccessModel.status == status)
        if expires_at is not None:
            query = query.filter(AccessModel.expires_at <= expires_at)

        return query.all()

    def get_by_id(self, access_id):
        return self.database.query(AccessModel).filter(AccessModel.id == access_id).first()

    def create_access(self, create_data):

        access = AccessModel(
            user_id=create_data.user_id,
            resource_id=create_data.resource_id,
            expires_at=create_data.expires_at,
            status=create_data.status,
            comment=create_data.comment
        )

        self.database.add(access)
        self.database.flush()
        return access

    def update_access_status(self):
        from models.accesses import AccessModel
        from schemas.accesses import AccessStatus

        query = self.database.query(AccessModel)
        now = datetime.now()
        query.filter(
            (AccessModel.expires_at <= now) &
            (AccessModel.status != AccessStatus.REVOKED) &
            (AccessModel.status != AccessStatus.EXPIRED)).update(
            {AccessModel.status: AccessStatus.EXPIRED},
            synchronize_session=False
        )
        self.database.flush()
