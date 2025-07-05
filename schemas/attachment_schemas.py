
from pydantic import BaseModel
from datetime import datetime

class AttachmentCreateResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    content_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True