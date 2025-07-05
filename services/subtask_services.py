from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models import User, Task
from schemas.subtask_schemas import SubtaskCreate, SubtaskResponse
from repository.subtask_repository import SubtaskRepository
from services.project_services import ProjectService
import logging

logger = logging.getLogger(__name__)

class SubtaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SubtaskRepository(db)
        self.project_service = ProjectService(db)

    def create_subtask(self, subtask: SubtaskCreate, current_user: User) -> SubtaskResponse:
        """
        Создать новую подзадачу. Только автор проекта может создавать.
        """
        task = self.db.query(Task).filter(Task.id == subtask.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        project = self.project_service.get_project(task.project_id, current_user)
        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может создавать подзадачи")

        try:
            with self.db.begin():
                db_subtask = self.repo.create_subtask(subtask, author_id=current_user.id)
                return SubtaskResponse.from_orm(db_subtask)
        except Exception as e:
            logger.error(f"Ошибка создания подзадачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка создания подзадачи")

    def get_subtask(self, subtask_id: int, current_user: User) -> SubtaskResponse:
        """
        Получить подзадачу по ID с проверкой доступа.
        """
        subtask = self.repo.get_subtask_by_id(subtask_id)
        if not subtask:
            raise HTTPException(status_code=404, detail="Подзадача не найдена")

        task = self.db.query(Task).filter(Task.id == subtask.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        if not self.project_service.has_access_to_project(task.project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к проекту")

        return SubtaskResponse.from_orm(subtask)

    def update_subtask(self, subtask_id: int, subtask: SubtaskCreate, current_user: User) -> SubtaskResponse:
        """
        Обновить подзадачу. Только автор проекта может обновлять.
        """
        db_subtask = self.repo.get_subtask_by_id(subtask_id)
        if not db_subtask:
            raise HTTPException(status_code=404, detail="Подзадача не найдена")

        task = self.db.query(Task).filter(Task.id == db_subtask.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        project = self.project_service.get_project(task.project_id, current_user)
        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может обновлять подзадачи")

        try:
            with self.db.begin():
                updated_subtask = self.repo.update_subtask(subtask_id, subtask)
                if not updated_subtask:
                    raise HTTPException(status_code=404, detail="Подзадача не найдена")
                return SubtaskResponse.from_orm(updated_subtask)
        except Exception as e:
            logger.error(f"Ошибка обновления подзадачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка обновления подзадачи")

    def delete_subtask(self, subtask_id: int, current_user: User):
        """
        Удалить подзадачу. Только автор проекта может удалять.
        """
        db_subtask = self.repo.get_subtask_by_id(subtask_id)
        if not db_subtask:
            raise HTTPException(status_code=404, detail="Подзадача не найдена")

        task = self.db.query(Task).filter(Task.id == db_subtask.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        project = self.project_service.get_project(task.project_id, current_user)
        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор проекта может удалять подзадачи")

        try:
            with self.db.begin():
                if not self.repo.delete_subtask(subtask_id):
                    raise HTTPException(status_code=404, detail="Подзадача не найдена")
        except Exception as e:
            logger.error(f"Ошибка удаления подзадачи: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка удаления подзадачи")