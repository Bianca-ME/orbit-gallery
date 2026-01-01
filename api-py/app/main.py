import uuid # universally unique identifiers
from minio import Minio
import os
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from . import models, schemas, database

app = FastAPI()

minio_client = Minio(
    "minio-orbit:9000",         # minio-orbit = container name (Docker DNS); MiniO API port: 9000
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

# Dependency: DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    return db.query(models.Photo).all()

@app.post("/photos/upload-test")    # Upload file to MinIO
async def upload_test(file: UploadFile = File(...)):
    print(">>> UPLOADING TO MINIO <<<")
    # object_name = file.filename # use original filename (not recommended, may cause name conflicts)
    file_ext = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{file_ext}"

    minio_client.put_object(
        bucket_name="photos",
        object_name=object_name,
        data=file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type,
    )
    print(">>> UPLOAD FINISHED <<<")

    return {
        "original_filename": file.filename,
        "object_key": object_name,
    }