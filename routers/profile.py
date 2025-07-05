from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas.profile_schemas import ProfileResponse, ProfileUpdate, AvatarResponse
from schemas.user_schemas import UserResponse
from services.attachment_services import AttachmentServices
from services.user_services import UserService
from services.profile_services import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)

def get_attach_service(db: Session = Depends(get_db)) -> AttachmentServices:
    return AttachmentServices(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.get("/", response_model=ProfileResponse)
async def get_current_user_profile(
    profile_service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    """
    Получить профиль текущего пользователя.

    **Возможные ошибки**:
    - 401: Неверный токен.
    - 404: Пользователь не найден.
    """
    return profile_service.get_profile(current_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile_by_id(
    user_id: int,
    profile_service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    """
    Получить профиль пользователя по ID. Доступно только для самого пользователя или администратора.

    **Возможные ошибки**:
    - 401: Неверный токен.
    - 403: Доступ запрещён (если не администратор и не владелец профиля).
    - 404: Пользователь не найден.
    """
    return profile_service.get_profile_by_id(user_id, current_user)

@router.put("/", response_model=ProfileResponse)
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    profile_service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить профиль текущего пользователя.

    **Возможные ошибки**:
    - 401: Неверный токен.
    - 404: Пользователь не найден.
    - 400: Неверные данные (например, пустое обновление).
    """
    return profile_service.update_profile(current_user, profile_update)

@router.post("/avatar", response_model=AvatarResponse)
async def set_user_avatar(
    attachment_id: int,
    profile_service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user)
):
    """Set an attachment as the user's avatar."""

    attachment = await profile_service.upload_avatar(current_user, attachment_id)
    return attachment

@router.delete("/avatar")
async def delete_user_avatar(
    profile_service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить аватар текущего пользователя.

    **Возможные ошибки**:
    - 401: Неверный токен.
    - 404: Аватар не найден.
    - 500: Ошибка удаления аватара.
    """
    profile_service.delete_avatar(current_user)
    return {"message": "Аватар удалён"}