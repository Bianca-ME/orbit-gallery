from pydantic import BaseModel
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
    created_at: datetime

    class Config:
        from_attributes = True