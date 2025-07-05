from typing import Any, Type

from sqlalchemy.orm import Session, joinedload
from db.models import Subtask
from schemas.subtask_schemas import SubtaskCreate

class SubtaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_subtask(self, subtask: SubtaskCreate, author_id: int) -> Subtask:
        """
        Создать новую подзадачу.
        """
        db_subtask = Subtask(**subtask.dict(), author_id=author_id)
        self.db.add(db_subtask)
        self.db.commit()
        self.db.refresh(db_subtask)
        return db_subtask

    def get_subtask_by_id(self, subtask_id: int) -> Type[Subtask] | None:
        """
        Получить подзадачу по ID с загрузкой связанных данных.
        """
        return self.db.query(Subtask).options(
            joinedload(Subtask.assignee),
            joinedload(Subtask.author)
        ).filter(Subtask.id == subtask_id).first()

    def update_subtask(self, subtask_id: int, subtask: SubtaskCreate) -> Type[Subtask] | None:
        """
        Обновить подзадачу.
        """
        db_subtask = self.db.query(Subtask).filter(Subtask.id == subtask_id).first()
        if not db_subtask:
            return None
        for key, value in subtask.dict(exclude_unset=True).items():
            setattr(db_subtask, key, value)
        self.db.commit()
        self.db.refresh(db_subtask)
        return db_subtask

    def delete_subtask(self, subtask_id: int) -> bool:
        """
        Удалить подзадачу.
        """
        db_subtask = self.db.query(Subtask).filter(Subtask.id == subtask_id).first()
        if not db_subtask:
            return False
        self.db.delete(db_subtask)
        self.db.commit()
        return True