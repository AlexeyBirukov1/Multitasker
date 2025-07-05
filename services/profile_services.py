from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.models import User
from schemas.profile_schemas import ProfileUpdate, ProfileResponse
from schemas.user_schemas import UserResponse
from repository.profile_repository import ProfileRepository
import os
import logging
from pathlib import Path

from services.attachment_services import AttachmentServices
from services.user_services import UserService

logger = logging.getLogger(__name__)

AVATAR_DIR = "uploads/avatars/"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProfileRepository(db)
        self.attach = AttachmentServices(db)
        self.user_service = UserService(db)

    def get_profile(self, current_user: User) -> ProfileResponse:
        """
        Получить профиль текущего пользователя.
        """
        user = self.repo.get_user_by_id(current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return ProfileResponse.from_orm(user)

    def get_profile_by_id(self, user_id: int, current_user: User) -> UserResponse:
        """
        Получить профиль пользователя по ID. Доступно только для владельца или администратора.
        """
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return UserResponse.from_orm(user)

    def update_profile(self, current_user: User, profile_update: ProfileUpdate) -> ProfileResponse:
        """
        Обновить профиль текущего пользователя.
        """
        if not profile_update.dict(exclude_unset=True):
            raise HTTPException(status_code=400, detail="Не указаны данные для обновления")
        user = self.repo.update_user(current_user.id, profile_update)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return ProfileResponse.from_orm(user)

    async def upload_avatar(self, current_user: User, attachment_id=None):
        """
        Загрузить аватар для текущего пользователя.
        """
        user_id = current_user.id
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to set avatar for this user")

        attachment = await self.attach.get_attachment(attachment_id, current_user)

        """old_avatar = current_user.avatar
        if old_avatar:
            if Path(old_avatar.filepath).exists():
                Path(old_avatar.filepath).unlink(missing_ok=True)
            self.user_service.db.delete(old_avatar)
            self.user_service.db.commit()"""

        current_user.avatar_id = attachment_id
        self.user_service.db.commit()
        self.user_service.db.refresh(current_user)
        return attachment

    def delete_avatar(self, current_user: User):
        """
        Удалить аватар текущего пользователя.
        """
        if not current_user.avatar_id:
            raise HTTPException(status_code=404, detail="Аватар не найден")
        try:
            with self.db.begin():
                self.repo.delete_avatar(current_user.avatar_id)
        except Exception as e:
            logger.error(f"Ошибка удаления аватара: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка удаления аватара")



def ensure_avatar_dir():
    if not os.path.exists(AVATAR_DIR):
        os.makedirs(AVATAR_DIR)