from datetime import datetime

from sqlalchemy.orm import Session
from db.models import Attachment
from typing import Optional

class AttachmentRepo:
    def __init__(self, session: Session):
        self.db = session

    def create_attachment(
        self,
        filename: str,
        filepath: str,
        content_type: str,
    ) -> Attachment:
        db_attachment = Attachment(
            filename=filename,
            filepath=filepath,
            content_type=content_type,
            uploaded_at=datetime.utcnow()
        )
        self.db.add(db_attachment)
        self.db.commit()
        self.db.refresh(db_attachment)
        return db_attachment

    async def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        return self.db.query(Attachment).filter(Attachment.id == attachment_id).first()

    def delete_attachment(self, attachment_id: int) -> bool:
        attachment = self.get_attachment_by_id(attachment_id)
        if not attachment:
            return False
        self.db.delete(attachment)
        self.db.commit()
        return True