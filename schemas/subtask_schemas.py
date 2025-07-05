from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from db.models import PriorityEnum
from schemas.user_schemas import UserResponse

class SubtaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    assignee_id: Optional[int] = None
    deadline: Optional[datetime] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    tag: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    task_id: int

    class Config:
        from_attributes = True

class SubtaskResponse(SubtaskCreate):
    id: int
    author_id: int
    assignee: Optional[UserResponse] = None
    author: UserResponse

    class Config:
        from_attributes = True