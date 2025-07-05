from typing import Type, Any

from sqlalchemy.orm import Session, joinedload

from db.models import Project, ProjectParticipant, ProjectCategory, User, Task
from schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectFilter, ProjectResponse

class ProjectRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_projects(self, user_id: int, skip: int = 0, limit: int = 100, filters: ProjectFilter = None) -> list[Type[ProjectResponse]]:
        query = self.db.query(Project).join(ProjectParticipant).filter(
            ProjectParticipant.user_id == user_id
        )

        if filters:
            if filters.name:
                query = query.filter(Project.name.ilike(f"%{filters.name}%"))
            if filters.deadline_from:
                query = query.filter(Project.deadline >= filters.deadline_from)
            if filters.deadline_to:
                query = query.filter(Project.deadline <= filters.deadline_to)
            if filters.participant_id:
                query = query.filter(Project.participants.any(id=filters.participant_id))
            if filters.status:
                query = query.filter(Project.status == filters.status)
            if filters.category_id:
                query = query.join(ProjectCategory).filter(
                    ProjectCategory.category_id == filters.category_id,
                    ProjectCategory.user_id == user_id
                )

        query = query.options(
            joinedload(Project.tasks).joinedload(Task.assignee),
            joinedload(Project.tasks).joinedload(Task.author),
            joinedload(Project.participants),
            joinedload(Project.attachments),
            joinedload(Project.categories)
        )

        return query.offset(skip).limit(limit).all()

    def get_project_by_id(self, project_id: int) -> Project | None:
        return self.db.query(Project).options(
            joinedload(Project.tasks).joinedload(Task.assignee),
            joinedload(Project.tasks).joinedload(Task.author),
            joinedload(Project.participants),
            joinedload(Project.attachments),
            joinedload(Project.categories)
        ).filter(
            Project.id == project_id
        ).first()

    def create_project(self, project: ProjectCreate, author_id: int) -> Project:
        db_project = Project(**project.dict(), author_id=author_id)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        participant = ProjectParticipant(user_id=author_id, project_id=db_project.id)
        self.db.add(participant)
        self.db.commit()
        return db_project

    def update_project(self, project_id: int, project: ProjectUpdate) -> Type[Project] | None:
        db_project = self.db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return None
        for key, value in project.dict(exclude_unset=True).items():
            setattr(db_project, key, value)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int) -> bool:
        db_project = self.db.query(Project).filter(Project.id == project_id).first()
        if not db_project:
            return False
        self.db.delete(db_project)
        self.db.commit()
        return True

    def has_access_to_project(self, project_id: int, user_id: int) -> bool:
        return self.db.query(ProjectParticipant).filter(
            ProjectParticipant.project_id == project_id,
            ProjectParticipant.user_id == user_id
        ).first() is not None

    def add_participant(self, project_id: int, user_id: int) -> bool:
        participant = ProjectParticipant(user_id=user_id, project_id=project_id)
        self.db.add(participant)
        self.db.commit()
        return True

    def remove_participant(self, project_id: int, user_id: int) -> bool:
        participant = self.db.query(ProjectParticipant).filter(
            ProjectParticipant.project_id == project_id,
            ProjectParticipant.user_id == user_id
        ).first()
        if not participant:
            return False
        self.db.delete(participant)
        self.db.commit()
        return True

    def get_participants(self, project_id: int) -> list[User]:
        project = self.db.query(Project).options(
            joinedload(Project.participants)
        ).filter(Project.id == project_id).first()
        if not project:
            return []
        return project.participants

    def add_project_to_category(self, category_id: int, project_id: int, user_id: int) -> bool:
        # Проверяем, существует ли категория и принадлежит ли она пользователю
        category = self.db.query(ProjectCategory).filter(
            ProjectCategory.category_id == category_id,
            ProjectCategory.user_id == user_id
        ).first()
        if not category:
            # Если категории нет, создаем новую связь
            category = ProjectCategory(category_id=category_id, project_id=project_id, user_id=user_id)
            self.db.add(category)
            self.db.commit()
            return True
        return False

    def remove_project_from_category(self, category_id: int, project_id: int, user_id: int) -> bool:
        category = self.db.query(ProjectCategory).filter(
            ProjectCategory.category_id == category_id,
            ProjectCategory.project_id == project_id,
            ProjectCategory.user_id == user_id
        ).first()
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True