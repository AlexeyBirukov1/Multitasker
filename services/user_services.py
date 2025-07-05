from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from schemas.attachment_schemas import AttachmentCreateResponse
from schemas.user_schemas import UserCreate, UserLogin, UserUpdate, UserResponse, Token
from db.models import User, Attachment
from repository.user_repository import UserRepo
from services.attachment_services import AttachmentServices
from services.email_service import email_service
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SECRET_KEY = '96cb5e02cadf7a47bf66e393c0ea4b7de24afa726fcc0447a7c54b7a6e8ce650'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

class UserService:
    def __init__(self, db: Session, repo: UserRepo = None, attachment_service: AttachmentServices = None):
        self.db = db
        self.repo = repo or UserRepo(db)
        self.attachment_service = attachment_service or AttachmentServices(db)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str: str = payload.get("sub")
            if not user_id_str:
                raise HTTPException(status_code=401, detail="Неверный токен")
            user = await self.repo.get_by_id(int(user_id_str))
            if not user:
                raise HTTPException(status_code=401, detail="Пользователь не найден")
            return user
        except (JWTError, ValueError):
            raise HTTPException(status_code=401, detail="Неверный токен")

    async def register(self, user: UserCreate) -> Token:
        if await self.repo.get_by_email(user.email):
            raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")
        new_user = await self.repo.create(user.email, user.name, user.password)
        access_token = jwt.encode(
            {"sub": str(new_user.id), "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return Token(access_token=access_token, token_type="bearer")

    async def login(self, user: UserLogin) -> Token:
        db_user = await self.repo.get_by_email(user.email)
        if not db_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if not pwd_context.verify(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        access_token = jwt.encode(
            {"sub": str(db_user.id), "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return Token(access_token=access_token, token_type="bearer")

    async def get_profile(self, user_id: int, current_user: User) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        return UserResponse.from_orm(user)

    async def update_profile(self, user_id: int, user_update: UserUpdate, current_user: User) -> UserResponse:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        updated_user = await self.repo.update(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return UserResponse.from_orm(updated_user)

    async def upload_avatar(self, user_id: int, file: UploadFile, current_user: User) -> AttachmentCreateResponse:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        return await self.attachment_service.save_attachment(
            file=file,
            entity_type="user",
            entity_id=user_id,
            current_user=current_user,
            is_avatar=True
        )

    async def delete_avatar(self, user_id: int, current_user: User) -> dict:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        user = await self.repo.get_by_id(user_id)
        if not user or not user.avatar_id:
            raise HTTPException(status_code=404, detail="Аватар не найден")
        attachment = self.db.query(Attachment).filter(Attachment.id == user.avatar_id).first()
        if attachment:
            if Path(attachment.filepath).exists():
                Path(attachment.filepath).unlink()
            self.db.delete(attachment)
        user.avatar_id = None
        self.db.commit()
        return {"message": "Аватар удалён"}

    async def get_avatar(self, user_id: int, current_user: User) -> tuple[str, str]:
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        user = await self.repo.get_by_id(user_id)
        if not user or not user.avatar_id:
            raise HTTPException(status_code=404, detail="Аватар не найден")
        attachment = self.attachment_service.get_attachment(user.avatar_id, current_user)
        return attachment.filepath, attachment.content_type

    async def request_password_reset(self, email: str) -> str:
        token = await self.repo.generate_reset_token(email)
        if not token:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user = await self.repo.get_by_email(email)

        if not email_service.send_password_reset(email, user, token):
            logger.error(f"Failed to send password reset email to {email}")
            raise HTTPException(status_code=500, detail="Не удалось отправить письмо")
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        if not await self.repo.reset_password(token, new_password):
            raise HTTPException(status_code=400, detail="Неверный токен")
        return True

    async def search_users_by_email(self, email: str) -> List[UserResponse]:
        users = await self.repo.search_by_email(email)
        return [UserResponse.from_orm(user) for user in users]