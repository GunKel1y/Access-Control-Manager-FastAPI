from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from datetime import datetime

SQL_DB_URL = "postgresql://postgres:K12lgACC8@localhost/ACM_FastAPI"

engine = create_engine(SQL_DB_URL)

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def update_access_status(db: Session):
    from database.models import AccessModel
    from database.schemas import AccessStatus

    query = db.query(AccessModel)

    now = datetime.now()

    query.filter((AccessModel.expires_at <= now) & (AccessModel.status != AccessStatus.REVOKED) & (AccessModel.status != AccessStatus.EXPIRED)).update({AccessModel.status: AccessStatus.EXPIRED}, synchronize_session=False)

    db.commit()