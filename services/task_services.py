from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models import Task, User, Project
from schemas.task_schemas import TaskCreate, TaskResponse
from repository.task_repository import TaskRepository
from services.project_services import ProjectService
import logging

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)
        self.project_service = ProjectService(db)

    def create_task(self, task: TaskCreate, current_user: User) -> TaskResponse:
        project = self.project_service.get_project(task.project_id, current_user)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может создавать задачи")

        try:
            with self.db.begin():
                db_task = self.repo.create_task(task, author_id=current_user.id)
                return TaskResponse.from_orm(db_task)
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка создания задачи")

    def get_task(self, task_id: int, current_user: User) -> TaskResponse:
        task = self.repo.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        if not self.project_service.has_access_to_project(task.project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к проекту")

        return TaskResponse.from_orm(task)

    def update_task(self, task_id: int, task: TaskCreate, current_user: User) -> TaskResponse:
        db_task = self.repo.get_task_by_id(task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        project = self.project_service.get_project(db_task.project_id, current_user)
        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может обновлять задачи")

        try:
            with self.db.begin():
                updated_task = self.repo.update_task(task_id, task)
                if not updated_task:
                    raise HTTPException(status_code=404, detail="Задача не найдена")
                return TaskResponse.from_orm(updated_task)
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка обновления задачи")

    def delete_task(self, task_id: int, current_user: User):
        db_task = self.repo.get_task_by_id(task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        project = self.project_service.get_project(db_task.project_id, current_user)
        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может удалять задачи")

        try:
            with self.db.begin():
                if not self.repo.delete_task(task_id):
                    raise HTTPException(status_code=404, detail="Задача не найдена")
        except Exception as e:
            logger.error(f"Ошибка удаления задачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка удаления задачи")