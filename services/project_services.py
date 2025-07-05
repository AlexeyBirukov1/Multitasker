from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Type
from db.models import Project, User, ProjectParticipant
from schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectFilter, ProjectResponse
from repository.project_repository import (ProjectRepo)
from services.attachment_services import AttachmentServices
from services.email_service import email_service


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepo(db)
        self.attach_service = AttachmentServices(self.db)

    def get_all_projects(
            self, current_user: User, filters: ProjectFilter, skip: int = 0, limit: int = 100
    ) -> list[Type[ProjectResponse]]:
        """
        Получить список всех проектов, в которых пользователь является участником, с фильтрацией.
        """
        projects = self.repo.get_projects(user_id=current_user.id, skip=skip, limit=limit, filters=filters)

        # Фильтруем категории, чтобы показывать только те, которые принадлежат текущему пользователю
        for project in projects:
            project.categories = [
                category for category in project.categories
                if category.user_id == current_user.id
            ]
        return projects

    def get_project(self, project_id: int, current_user: User) -> Project:
        """
        Получить проект по ID с проверкой доступа.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if not  self.repo.has_access_to_project(project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")

        return project

    def create_project(self, project: ProjectCreate, current_user: User) -> Project:
        """
        Создать новый проект.
        """
        return  self.repo.create_project(project, author_id=current_user.id)

    def update_project(self, project_id: int, project: ProjectUpdate, current_user: User) -> Type[Project]:
        """
        Обновить проект. Только автор может обновлять.
        """
        db_project =  self.repo.get_project_by_id(project_id)
        if not db_project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if db_project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор может обновлять проект")

        updated_project =  self.repo.update_project(project_id, project)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        return updated_project

    def delete_project(self, project_id: int, current_user: User) -> bool:
        """
        Удалить проект. Только автор может удалять.
        """
        db_project =  self.repo.get_project_by_id(project_id)
        if not db_project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if db_project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор может удалять проект")

        return  self.repo.delete_project(project_id)

    def add_participant(self, project_id: int, user_id: int, current_user: User) -> bool:
        """
        Добавить участника в проект. Только автор может добавлять.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор может добавлять участников")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if  self.repo.has_access_to_project(project_id, user_id):
            raise HTTPException(status_code=400, detail="Пользователь уже является участником проекта")

        self.repo.add_participant(project_id, user_id)

        # Отправляем email-уведомление
        subject = f"Вас добавили в проект: {project.name}"
        body = (
            f"Здравствуйте, {user.name}!\n\n"
            f"Вы были добавлены в проект '{project.name}'.\n"
            f"Описание проекта: {project.description or 'Нет описания'}.\n"
            f"Перейдите в приложение, чтобы ознакомиться с деталями: [ссылка_на_проект].\n\n"
            f"С уважением,\nMultitasker_TUSUR"
        )
        if not email_service.send_email(user.email, subject, body):
            print(f"Не удалось отправить письмо пользователю {user.email}")

        return True

    def remove_participant(self, project_id: int, user_id: int, current_user: User) -> bool:
        """
        Удалить участника из проекта. Только автор может удалять.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только автор может удалять участников")

        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Автор не может удалить сам себя")

        if not  self.repo.remove_participant(project_id, user_id):
            raise HTTPException(status_code=404, detail="Участник не найден в проекте")

        return True

    def get_participants(self, project_id: int, current_user: User) -> List[User]:
        """
        Получить список участников проекта.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if not  self.repo.has_access_to_project(project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")

        return  self.repo.get_participants(project_id)

    def add_project_to_category(self, project_id: int, category_id: int, current_user: User) -> bool:
        """
        Добавить проект в категорию текущего пользователя.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if not  self.repo.has_access_to_project(project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")

        if not  self.repo.add_project_to_category(category_id, project_id, current_user.id):
            raise HTTPException(status_code=404, detail="Категория не найдена или не принадлежит вам")

        return True

    def remove_project_from_category(self, project_id: int, category_id: int, current_user: User) -> bool:
        """
        Удалить проект из категории текущего пользователя.
        """
        project =  self.repo.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        if not  self.repo.has_access_to_project(project_id, current_user.id):
            raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")

        if not  self.repo.remove_project_from_category(category_id, project_id, current_user.id):
            raise HTTPException(status_code=404, detail="Категория не найдена или не принадлежит вам")

        return True

    def has_access_to_project(self, project_id: int, user_id: int) -> bool:
        """Check if user has access to the project (author or participant)."""
        project = self.repo.get_project_by_id(project_id)
        if not project:
            return False
        if project.author_id == user_id:
            return True
        return self.db.query(ProjectParticipant).filter_by(project_id=project_id, user_id=user_id).first() is not None

    def add_attachment_to_project(self, current_user, project_id, attachment_id):
        project = self.repo.get_project_by_id(project_id)
        if not project or project.author_id != current_user.id:
            raise HTTPException(status_code=404, detail="Project not found or not authorized")

        attachment = self.attach_service.repo.get_attachment_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")

        if attachment not in project.attachments:
            project.attachments.append(attachment)
            self.db.commit()

        return attachment

    def remove_attach(self, current_user, project_id, attachment_id=None):
        project = self.get_project(project_id, current_user)

        if project.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only project author can remove attachments")

        attachment = self.attach_service.get_attachment(attachment_id, current_user)
        if attachment not in project.attachments:
            raise HTTPException(status_code=404, detail="Attachment not found in project")
        project.attachments.remove(attachment)
        self.db.commit()
