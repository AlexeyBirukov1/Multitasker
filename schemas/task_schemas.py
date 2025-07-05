from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from db.models import PriorityEnum
from schemas.user_schemas import UserResponse
from schemas.subtask_schemas import SubtaskResponse

class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    assignee_id: Optional[int] = None
    deadline: Optional[datetime] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    tag: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    project_id: int

    class Config:
        from_attributes = True

class TaskResponse(TaskCreate):
    id: int
    author_id: int
    assignee: Optional[UserResponse] = None
    author: UserResponse
    subtasks: List[SubtaskResponse] = []

    class Config:
        from_attributes = True