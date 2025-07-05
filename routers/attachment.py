from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
from db.database import get_db
from db.models import User
from schemas.attachment_schemas import AttachmentCreateResponse
from services.attachment_services import AttachmentServices
from services.user_services import UserService

router = APIRouter(prefix="/attachments", tags=["Attachments"])

def get_attach_service(db: Session = Depends(get_db)) -> AttachmentServices:
    return AttachmentServices(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.post("/upload", response_model=AttachmentCreateResponse)
async def upload_attachment(
    file: UploadFile = File(...),
    service: AttachmentServices = Depends(get_attach_service),
    current_user: User = Depends(get_current_user)
):
    """Upload an attachment and return its ID."""
    return await service.save_attachment(file, current_user)

@router.get("/{attachment_id}", response_model=AttachmentCreateResponse)
async def get_attachment(
    attachment_id: int,
    service: AttachmentServices = Depends(get_attach_service),
    current_user: User = Depends(get_current_user)
):
    """Get an attachment by ID."""
    return await service.get_attachment(attachment_id, current_user)

@router.get("/{attachment_id}/file", response_class=FileResponse)
async def get_attachment_file(
    attachment_id: int,
    service: AttachmentServices = Depends(get_attach_service),
    current_user: User = Depends(get_current_user)
):
    """Download an attachment file."""
    filepath, content_type = await service.get_attachment_file(attachment_id, current_user)
    return FileResponse(filepath, media_type=content_type)

@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    service: AttachmentServices = Depends(get_attach_service),
    current_user: User = Depends(get_current_user)
):
    """Delete an attachment by ID."""
    return await service.delete_attachment(attachment_id, current_user)