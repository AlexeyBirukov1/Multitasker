from pydantic import BaseModel, Field, validator
from typing import Optional
import re

HEX_COLOR_REGEX = r'^#[0-9A-Fa-f]{6}$'

class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = None
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    name: str = Field(..., min_length=1, max_length=100)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    @validator('color')
    def validate_color(cls, v):
        if v and not re.match(HEX_COLOR_REGEX, v):
            raise ValueError("Color must be in HEX format, e.g., #FFFFFF")
        return v

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = None
    description: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip() if v else v

    @validator('color')
    def validate_color(cls, v):
        if v and not re.match(HEX_COLOR_REGEX, v):
            raise ValueError("Color must be in HEX format, e.g., #FFFFFF")
        return v

class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True