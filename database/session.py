from database.base import session_local


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
