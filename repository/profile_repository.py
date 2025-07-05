from typing import Any, Type

from sqlalchemy.orm import Session
from db.models import User, Attachment
from schemas.profile_schemas import ProfileUpdate
import os

class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Type[User] | None:
        """
        Получить пользователя по ID.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: int, profile_update: ProfileUpdate) -> Type[User] | None:
        """
        Обновить данные пользователя.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for key, value in profile_update.dict(exclude_unset=True).items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_avatar(self, filename: str, filepath: str, content_type: str, user_id: int) -> Attachment:
        """
        Создать запись об аватаре и привязать к пользователю.
        """
        attachment = Attachment(
            filename=filename,
            filepath=filepath,
            content_type=content_type,
            project_id=None
        )
        self.db.add(attachment)
        self.db.flush()  # Получить ID attachment без коммита
        user = self.db.query(User).filter(User.id == user_id).first()
        user.avatar_id = attachment.id
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def delete_avatar(self, avatar_id: int):
        """
        Удалить аватар и очистить avatar_id у пользователя.
        """
        attachment = self.db.query(Attachment).filter(Attachment.id == avatar_id).first()
        if not attachment:
            return
        if os.path.exists(attachment.filepath):
            os.remove(attachment.filepath)
        self.db.delete(attachment)
        user = self.db.query(User).filter(User.avatar_id == avatar_id).first()
        if user:
            user.avatar_id = None
        self.db.commit()