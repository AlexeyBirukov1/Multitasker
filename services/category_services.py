from fastapi import HTTPException
from sqlalchemy.orm import Session
from repository.category_repository import CategoryRepo
from schemas.category_schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from db.models import User, Category
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, db: Session, repo: CategoryRepo = None):
        self.db = db
        self.repo = repo or CategoryRepo(db)

    async def get_by_id(self, category_id: int, user: User) -> CategoryResponse:
        category = self.repo.get_by_id(category_id, user.id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Retrieved category {category_id} for user {user.id}")
        return CategoryResponse.from_orm(category)

    async def get_all(self, user: User, skip: int = 0, limit: int = 100) -> List[CategoryResponse]:
        categories = self.repo.get_all(user.id, skip, limit)
        logger.info(f"Retrieved {len(categories)} categories for user {user.id}")
        return [CategoryResponse.from_orm(c) for c in categories]

    async def create(self, category: CategoryCreate, user: User) -> CategoryResponse:

        if self.repo.get_by_name(category.name, user.id):
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        db_category = self.repo.create(category, user.id)
        logger.info(f"Created category {db_category.id} for user {user.id}")
        return CategoryResponse.from_orm(db_category)

    async def update(self, category_id: int, category: CategoryUpdate, user: User) -> CategoryResponse:

        if category.name and self.repo.get_by_name(category.name, user.id, exclude_id=category_id):
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        db_category = self.repo.update(category_id, category, user.id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Updated category {category_id} for user {user.id}")
        return CategoryResponse.from_orm(db_category)

    async def delete(self, category_id: int, user: User) -> dict:
        if not self.repo.delete(category_id, user.id):
            raise HTTPException(status_code=404, detail="Category not found")
        logger.info(f"Deleted category {category_id} for user {user.id}")
        return {"message": "Category deleted"}


    def get_by_name(self, name: str, user_id: int, exclude_id: int = None) -> Optional[Category]:
        query = self.db.query(Category).filter(
            Category.name == name,
            Category.user_id == user_id
        )
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first()