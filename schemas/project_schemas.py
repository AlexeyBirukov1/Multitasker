from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.user_schemas import UserResponse
from schemas.attachment_schemas import AttachmentCreateResponse
from schemas.task_schemas import TaskResponse
from schemas.category_schemas import CategoryResponse
from db.models import ProjectStatusEnum

class ProjectMinimalResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    author_id: int

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatusEnum] = ProjectStatusEnum.ACTIVE

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatusEnum] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    author_id: int
    status: Optional[ProjectStatusEnum] = None
    participants: List[UserResponse] = []
    attachments: List[AttachmentCreateResponse] = []
    tasks: List[TaskResponse] = []
    categories: List[CategoryResponse] = []

    class Config:
        orm_mode = True

class ProjectFilter(BaseModel):
    name: Optional[str] = None
    deadline_from: Optional[datetime] = None
    deadline_to: Optional[datetime] = None
    participant_id: Optional[int] = None
    status: Optional[ProjectStatusEnum] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    category_id: Optional[int] = None