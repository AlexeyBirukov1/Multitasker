from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from db.models import User
from schemas.subtask_schemas import SubtaskCreate, SubtaskResponse
from services.user_services import UserService
from services.subtask_services import SubtaskService

router = APIRouter(prefix="/subtasks", tags=["Subtasks"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_subtask_service(db: Session = Depends(get_db)) -> SubtaskService:
    return SubtaskService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.post("/", response_model=SubtaskResponse)
async def create_new_subtask(
    subtask: SubtaskCreate,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: User = Depends(get_current_user),
):
    """
    Создаёт новую подзадачу. Только автор проекта может создавать подзадачи.
    """
    return subtask_service.create_subtask(subtask, current_user)

@router.get("/{subtask_id}", response_model=SubtaskResponse)
async def get_subtask(
    subtask_id: int,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает подзадачу по ID.
    """
    return subtask_service.get_subtask(subtask_id, current_user)

@router.put("/{subtask_id}", response_model=SubtaskResponse)
async def update_existing_subtask(
    subtask_id: int,
    subtask: SubtaskCreate,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: User = Depends(get_current_user),
):
    """
    Обновляет подзадачу. Только автор проекта может обновлять.

    """
    return subtask_service.update_subtask(subtask_id, subtask, current_user)

@router.delete("/{subtask_id}")
async def delete_existing_subtask(
    subtask_id: int,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: User = Depends(get_current_user),
):
    """
    Удаляет подзадачу. Только автор проекта может удалять.
    """
    subtask_service.delete_subtask(subtask_id, current_user)
    return {"message": "Подзадача удалена"}