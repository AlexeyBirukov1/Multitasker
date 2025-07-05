from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db.models import User
from schemas.attachment_schemas import AttachmentCreateResponse
from schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectFilter, ProjectMinimalResponse
from schemas.user_schemas import UserResponse
from services.attachment_services import AttachmentServices
from services.user_services import UserService
from services.project_services import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])

def get_attach_service(db: Session = Depends(get_db)) -> AttachmentServices:
    return AttachmentServices(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.get("/", response_model=List[ProjectMinimalResponse])
def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
    filters: ProjectFilter = Depends(),
    skip: int = 0,
    limit: int = 100
):
    """
    Получить список всех проектов, в которых пользователь является участником, с фильтрацией.

    - **name**: Фильтр по названию проекта (частичное совпадение).
    - **category_id**: Фильтр по категории.
    - **deadline_from**: Дедлайн: начало диапазона.
    - **deadline_to**: Дедлайн: конец диапазона.
    - **participant_id**: Фильтр по участнику.
    - **status**: Фильтр по статусу проекта (active, completed, archived).
    - **skip**: Пропустить первые N записей (для пагинации).
    - **limit**: Максимальное количество записей для возврата (для пагинации).
    """
    return project_service.get_all_projects(current_user, filters, skip, limit)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает проект по ID с его задачами и участниками.
    """
    return project_service.get_project(project_id, current_user)

@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Создаёт новый проект.
    """
    return project_service.create_project(project, current_user)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    project_id: int,
    project: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Обновляет проект. Только автор может обновлять.
    """
    return project_service.update_project(project_id, project, current_user)

@router.delete("/{project_id}")
def delete_existing_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет проект. Только автор может удалять.
    """
    if project_service.delete_project(project_id, current_user):
        return {"detail": "Проект удалён"}
    raise HTTPException(status_code=404, detail="Проект не найден")

@router.post("/{project_id}/participants")
def add_participant(
    project_id: int,
    user_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Добавляет участника в проект. Только автор может добавлять.
    """
    project_service.add_participant(project_id, user_id, current_user)
    return {"message": "Участник добавлен"}

@router.delete("/{project_id}/participants/{user_id}")
def remove_participant(
    project_id: int,
    user_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Удаляет участника из проекта. Только автор может удалять.
    """
    project_service.remove_participant(project_id, user_id, current_user)
    return {"message": "Участник удалён"}

@router.get("/{project_id}/participants", response_model=List[UserResponse])
def get_participants(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает список участников проекта.
    """
    return project_service.get_participants(project_id, current_user)

@router.post("/{project_id}/categories/{category_id}")
def add_project_to_category(
    project_id: int,
    category_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Добавить проект в категорию текущего пользователя.
    """
    project_service.add_project_to_category(project_id, category_id, current_user)
    return {"message": "Проект добавлен в категорию"}

@router.delete("/{project_id}/categories/{category_id}")
def remove_project_from_category(
    project_id: int,
    category_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить проект из категории текущего пользователя.
    """
    project_service.remove_project_from_category(project_id, category_id, current_user)
    return {"message": "Проект удален из категории"}

@router.post("/{project_id}/attachments/{attachment_id}", response_model=AttachmentCreateResponse)
async def add_attachment_to_project(
    project_id: int,
    attachment_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """Add an attachment to a project."""
    return project_service.add_attachment_to_project(current_user, project_id, attachment_id)

@router.delete("/{project_id}/attachments/{attachment_id}")
async def remove_attachment_from_project(
    project_id: int,
    attachment_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    """Remove an attachment from a project."""
    project_service.remove_attach(current_user, project_id, attachment_id)
    return {"message": "Attachment removed"}