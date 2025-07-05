import os
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from repository.attachment_repository import AttachmentRepo
from db.models import User, Attachment, Project, ProjectParticipant
from schemas.attachment_schemas import AttachmentCreateResponse
import aiofiles
from pathlib import Path
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class AttachmentServices:
    def __init__(self, db: Session, repo: AttachmentRepo = None):
        self.db = db
        self.repo = repo or AttachmentRepo(db)
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
        self.UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads/attachments"))
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.ALLOWED_FILE_TYPES = {
            "image/jpeg", "image/png", "image/gif",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

    async def save_attachment(
        self,
        file: UploadFile,
        current_user: User,
    ) -> AttachmentCreateResponse:
        # Проверка размера файла
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {self.MAX_FILE_SIZE / (1024 * 1024)} MB limit"
            )

        # Проверка типа файла
        if file.content_type not in self.ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Генерация имени файла
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"attachment_{os.urandom(8).hex()}.{file_extension}"
        filepath = self.UPLOAD_DIR / unique_filename

        # Сохранение файла
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        # Сохранение в базе
        attachment = self.repo.create_attachment(
            filename=file.filename,
            filepath=str(filepath),
            content_type=file.content_type,
        )

        logger.info(f"Saved attachment {file.filename} by user {current_user.id}")
        return AttachmentCreateResponse.from_orm(attachment)

    async def get_attachment(self, attachment_id: int, current_user: User) -> AttachmentCreateResponse:
        allowed_image_types = {"image/jpeg", "image/png", "image/gif"}

        attachment = await self.repo.get_attachment_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")

        if not Path(attachment.filepath).exists():
            raise HTTPException(status_code=404, detail="File not found on server")

        if attachment.content_type not in allowed_image_types:
            raise HTTPException(status_code=400, detail="File type not allowed")

        return AttachmentCreateResponse.from_orm(attachment)

    async def delete_attachment(self, attachment_id: int, current_user: User) -> dict:
        attachment = await self.get_attachment(attachment_id, current_user)

        if Path(attachment.filepath).exists():
            Path(attachment.filepath).unlink(missing_ok=True)

        if self.repo.delete_attachment(attachment_id):
            logger.info(f"Deleted attachment {attachment_id}")
            return {"message": "Attachment deleted"}
        raise HTTPException(status_code=404, detail="Attachment not found")

    async def get_attachment_file(self, attachment_id: int, current_user: User) -> Tuple[str, str]:
        attachment = await self.get_attachment(attachment_id, current_user)
        return attachment.filepath, attachment.content_type