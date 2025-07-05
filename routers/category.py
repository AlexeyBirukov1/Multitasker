from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from db.models import User
from schemas.category_schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category_services import CategoryService
from services.user_services import UserService

router = APIRouter(prefix="/categories", tags=["Categories"])

def get_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(token)

@router.get("/", response_model=List[CategoryResponse])
async def get_all(
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of categories to return"),
    service: CategoryService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    """Get all categories for the current user."""
    return await service.get_all(user, skip, limit)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_by_id(
    category_id: int,
    service: CategoryService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    """Get a category by ID."""
    return await service.get_by_id(category_id, user)

@router.post("/", response_model=CategoryResponse)
async def create(
    category: CategoryCreate,
    service: CategoryService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    """Create a new category for the current user."""
    return await service.create(category, user)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    """Update an existing category."""
    return await service.update(category_id, category, user)

@router.delete("/{category_id}")
async def delete(
    category_id: int,
    service: CategoryService = Depends(get_service),
    user: User = Depends(get_current_user)
):
    """Delete a category."""
    return await service.delete(category_id, user)