from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    s3_key = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())