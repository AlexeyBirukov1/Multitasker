from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from db.models import RoleEnum
import re

PASSWORD_REGEX = r'^[A-Za-z0-9!#$%&*+\-.<=>?@^_]+$'

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=16)
    password_confirm: str

    @validator('password')
    def password_rules(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError("Пароль должен содержать только буквы, цифры и разрешенные символы")
        return v

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError("Пароли не совпадают")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: RoleEnum
    avatar_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=16)

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=16)
    new_password_confirm: str

    @validator('new_password')
    def new_password_rules(cls, v):
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError("Пароль должен содержать только буквы, цифры и разрешенные символы")
        return v

    @validator('new_password_confirm')
    def new_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError("Новые пароли не совпадают")
        return v