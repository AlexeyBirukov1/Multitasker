from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas.task_schemas import TaskCreate, TaskResponse
from services.user_services import UserService
from services.task_services import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.post("/", response_model=TaskResponse)
async def create_new_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Создаёт новую задачу."""
    return task_service.create_task(task, current_user)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Возвращает задачу по ID."""
    return task_service.get_task(task_id, current_user)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: int,
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Обновляет задачу."""
    return task_service.update_task(task_id, task, current_user)

@router.delete("/{task_id}")
async def delete_existing_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Удаляет задачу."""
    task_service.delete_task(task_id, current_user)
    return {"message": "Задача удалена"}