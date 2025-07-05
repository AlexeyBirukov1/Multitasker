from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.database import Base

class RoleEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class ProjectStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class PriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ProjectParticipant(Base):
    __tablename__ = "project_participants"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)

class ProjectCategory(Base):
    __tablename__ = "project_categories"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

# Новая таблица для связи проектов и вложений
class ProjectAttachment(Base):
    __tablename__ = "project_attachments"
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    attachment_id = Column(Integer, ForeignKey("attachments.id"), primary_key=True)

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String)
    reset_token = Column(String, nullable=True)
    avatar_id = Column(Integer, ForeignKey("attachments.id"), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    avatar = relationship("Attachment", foreign_keys=[avatar_id], uselist=False, single_parent=True)
    tasks_assigned = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    tasks_created = relationship("Task", back_populates="author", foreign_keys="Task.author_id")
    subtasks_assigned = relationship("Subtask", back_populates="assignee", foreign_keys="Subtask.assignee_id")
    subtasks_created = relationship("Subtask", back_populates="author", foreign_keys="Subtask.author_id")
    projects = relationship("Project", back_populates="author")
    participating_projects = relationship("Project", secondary="project_participants", back_populates="participants")
    categories = relationship("Category", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="categories")
    projects = relationship("Project", secondary="project_categories", back_populates="categories")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deadline = Column(DateTime, nullable=True, index=True)
    status = Column(Enum(ProjectStatusEnum), default=ProjectStatusEnum.ACTIVE, index=True)

    tasks = relationship("Task", back_populates="project")
    attachments = relationship("Attachment", secondary="project_attachments", single_parent=True)
    author = relationship("User", back_populates="projects")
    participants = relationship("User", secondary="project_participants", back_populates="participating_projects")
    categories = relationship("Category", secondary="project_categories", back_populates="projects")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deadline = Column(DateTime, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    tag = Column(String, nullable=True)
    description = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])
    author = relationship("User", back_populates="tasks_created", foreign_keys=[author_id])
    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task")

class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deadline = Column(DateTime, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    tag = Column(String, nullable=True)
    description = Column(String, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    assignee = relationship("User", back_populates="subtasks_assigned", foreign_keys=[assignee_id])
    author = relationship("User", back_populates="subtasks_created", foreign_keys=[author_id])
    task = relationship("Task", back_populates="subtasks")