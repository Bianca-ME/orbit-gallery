from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class PhotoCreate(BaseModel):
    title: str
    tags: Optional[List[str]] = []
    object_key: str
    original_filename: str

class PhotoResponse(BaseModel):
    id: int
    title: str
    tags: List[str] = [] # default to empty list
    original_filename: str
    image_url: str
    thumbnail_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PhotoListResponse(BaseModel):
    items: List[PhotoResponse]
    limit: int
    offset: int
    total: int

class PhotoUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
