# Standard library imports
import os
import uuid # universally unique identifiers
from datetime import timedelta

# Third-party imports
from fastapi import FastAPI, Depends, UploadFile, File
from minio import Minio
from sqlalchemy.orm import Session

# Local project imports
from . import models, schemas, database
from .database import engine, SessionLocal
from .models import Base, Photo

# Create database tables (runs once at import time) / initialise DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI()

# MinIO client configuration
# Internal client: used by FastAPI inside Docker
minio_internal = Minio(
    "minio-orbit:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

# Public client: ONLY for signed URLs
minio_public = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
    region="us-east-1",  # ← THIS STOPS THE NETWORK CALL
)


# Dependency: DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_presigned_url(object_key: str) -> str:
    return minio_public.presigned_get_object(
        bucket_name="photos",
        object_name=object_key,
        expires=timedelta(hours=3),
    )

@app.on_event("startup")
def startup():
    # auto-create tables if not exist
    models.Base.metadata.create_all(bind=database.engine)

@app.post("/photos", response_model=schemas.PhotoResponse)
def create_photo(photo: schemas.PhotoCreate, db: Session = Depends(get_db)):
    db_photo = models.Photo(**photo.dict())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

@app.get("/photos", response_model=list[schemas.PhotoResponse])
def list_photos(db: Session = Depends(get_db)):
    photos = db.query(models.Photo).all()

    return [
        {
            "id": photo.id,
            "title": photo.title,
            "tags": photo.tags or [],
            "original_filename": photo.original_filename,
            "image_url": get_presigned_url(photo.object_key),
            "created_at": photo.created_at,
        }
        for photo in photos
    ]

@app.post("/photos/upload-test")    # Upload file to MinIO
async def upload_test(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    print(">>> UPLOADING TO MINIO <<<")

    # object_name = file.filename # use original filename (not recommended, may cause name conflicts)
    file_ext = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{file_ext}"

    minio_internal.put_object(
        bucket_name="photos",
        object_name=object_name,
        data=file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type,
    )

    print(">>> UPLOAD FINISHED <<<")

    # Save metadata to Postgres
    photo = Photo(
        title=file.filename,
        tags=[],
        object_key=object_name,
        original_filename=file.filename,
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {
        "id": photo.id,
        "title": photo.title,
        "object_key": object_name,
        "created_at": photo.created_at,
    }