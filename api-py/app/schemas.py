from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PhotoCreate(BaseModel):
    title: str
    tags: Optional[List[str]] = None
    s3_key: str

class PhotoResponse(PhotoCreate):
    id: int
    title: str
    tags: Optional[List[str]] = None
    s3_key: str
    created_at: datetime

    class Config:
        orm_mode = True