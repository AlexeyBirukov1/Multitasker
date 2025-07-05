from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user_schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    PasswordResetRequest, PasswordReset
)
from services.user_services import UserService
from db.models import User

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.post("/register", response_model=Token)
async def register(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Регистрация нового пользователя."""
    return await service.register(user)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    """Авторизация пользователя."""
    user = UserLogin(email=form_data.username, password=form_data.password)
    return await service.login(user)

@router.post("/password-reset-request")
async def password_reset_request(
    reset_request: PasswordResetRequest,
    service: UserService = Depends(get_user_service)
):
    """Запрос сброса пароля."""
    await service.request_password_reset(reset_request.email)
    return {"message": "Письмо с токеном отправлено"}

@router.post("/password-reset")
async def password_reset(
    reset_data: PasswordReset,
    service: UserService = Depends(get_user_service)
):
    """Сброс пароля по токену."""
    await service.reset_password(reset_data.token, reset_data.new_password)
    return {"message": "Пароль обновлен"}

@router.get("/search", response_model=List[UserResponse])
async def search_users(
    email: str = Query(..., min_length=1, description="Частичный или полный email для поиска"),
    user_service: UserService = Depends(get_user_service),
):
    """Ищет пользователей по email."""
    return await user_service.search_users_by_email(email)

@router.get("/{user_id}", response_model=UserResponse)
async def get_profile_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """Получить профиль пользователя по ID (для админов или себя)."""
    return await service.get_profile(user_id, current_user)