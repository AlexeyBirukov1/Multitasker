from typing import Type, Any

from sqlalchemy.orm import Session, joinedload
from db.models import Task
from schemas.task_schemas import TaskCreate

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: TaskCreate, author_id: int) -> Task:
        db_task = Task(**task.dict(), author_id=author_id)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_task_by_id(self, task_id: int) -> Type[Task] | None:
        return self.db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.author),
            joinedload(Task.subtasks)
        ).filter(Task.id == task_id).first()

    def update_task(self, task_id: int, task: TaskCreate) -> Type[Task] | None:
        db_task = self.db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return None
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: int) -> bool:
        db_task = self.db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return False
        self.db.delete(db_task)
        self.db.commit()
        return True