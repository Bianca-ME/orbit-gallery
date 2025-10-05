from pydantic import BaseModel
from datetime import datetime

class PhotoCreate(BaseModel):
    title: str
    tags: str | None = None
    s3_key: str

class PhotoResponse(PhotoCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True