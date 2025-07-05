from sqlalchemy.orm import Session
from db.models import User
from schemas.user_schemas import UserUpdate
from services.auth_services import get_password_hash
import secrets
from typing import Optional, List, Type


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    async def create(self, email: str, name: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        db_user = User(email=email, name=name, hashed_password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def generate_reset_token(self, email: str) -> Optional[str]:
        user = await self.get_by_email(email)
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        self.db.commit()
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        user = self.db.query(User).filter(User.reset_token == token).first()
        if not user:
            return False
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        self.db.commit()
        return True

    async def search_by_email(self, email: str) -> list[Type[User]]:
        return self.db.query(User).filter(User.email.ilike(f"%{email}%")).all()