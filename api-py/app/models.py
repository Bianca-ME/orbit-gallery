from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base
from datetime import datetime

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True) # Postgres auto-assigns id
    title = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True) # helpful with filtering

    # storage keys
    object_key = Column(String, nullable=False, unique=True) # object_key links DB to MinIO; s3_key renamed to object_key
    thumb_key = Column(String, nullable=True)

    # debug / traceability
    original_filename = Column(String, nullable=False)

    # timestamp
    created_at = Column(  # time of upload
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,)
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ) 