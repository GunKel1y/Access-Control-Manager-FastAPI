
from fastapi import FastAPI
from core.database import Base, engine
from api.v1.router import router
import os
import uvicorn


app = FastAPI(title="Access Control Manager",
              description="API для управления пользователями, ресурсами и доступами к ним. \
              Поддерживает создание, частичное редактирование, поиск и фильтрацию. \
              Предназначен для внутренних сотрудников, без удаления данных.",)
Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    port = int(os.getenv("APIPORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)