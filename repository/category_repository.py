from sqlalchemy.orm import Session
from db.models import Category
from schemas.category_schemas import CategoryCreate, CategoryUpdate
from typing import List, Optional

class CategoryRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

    def get_by_name(self, name: str, user_id: int, exclude_id: int = None) -> Optional[Category]:
        query = self.db.query(Category).filter(
            Category.name == name,
            Category.user_id == user_id
        )
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first()

    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.db.query(Category).filter(
            Category.user_id == user_id
        ).offset(skip).limit(limit).all()

    def create(self, category: CategoryCreate, user_id: int) -> Category:
        db_category = Category(**category.dict(), user_id=user_id)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update(self, category_id: int, category: CategoryUpdate, user_id: int) -> Optional[Category]:
        db_category = self.get_by_id(category_id, user_id)
        if not db_category:
            return None
        for key, value in category.dict(exclude_unset=True).items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete(self, category_id: int, user_id: int) -> bool:
        db_category = self.get_by_id(category_id, user_id)
        if not db_category:
            return False
        self.db.delete(db_category)
        self.db.commit()
        return True