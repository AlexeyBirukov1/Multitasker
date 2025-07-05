from fastapi import FastAPI

from db.database import engine, Base
# Эндпоинты
from routers import user, tasks, profile, project, category, attachment, subtask

app = FastAPI()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app.include_router(attachment.router)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(tasks.router)
app.include_router(subtask.router)
app.include_router(project.router)
app.include_router(category.router)

@app.get("/")
def root():
    return {"message": "Добро пожаловать в Multitasker!"}