from pydantic import BaseModel, Field
from typing import Optional
from schemas.user_schemas import UserResponse
from db.models import RoleEnum

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=255)

    class Config:
        from_attributes = True

class ProfileResponse(UserResponse):
    role: RoleEnum
    avatar_id: Optional[int] = None

    class Config:
        from_attributes = True

class AvatarResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    content_type: str

    class Config:
        from_attributes = True