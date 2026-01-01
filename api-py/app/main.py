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

# @app.post("/photos/upload-test")  # Temporarily save uploaded file inside container
# async def upload_test(file: UploadFile = File(...)):
#     upload_dir = "uploads" # to be clear: the dir is created inside the container
#     os.makedirs(upload_dir, exist_ok=True) # create the dir if it doesn't exist

#     file_path = os.path.join(upload_dir, file.filename)

#     with open(file_path, "wb") as buffer: # create a real file; write binary data
#         content = await file.read() # read the file content async. (read the file's bytes)
#         buffer.write(content)

#     return {
#         "filename": file.filename,
#         "saved_to": file_path,
#     }

# run docker `compose exec api-py ls uploads` to see the uploaded files inside the container

@app.post("/photos/upload-test")    # Upload file to MinIO
async def upload_test(file: UploadFile = File(...)):
    print(">>> UPLOADING TO MINIO <<<")
    object_name = file.filename

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
        "filename": file.filename,
        "stored_in": "minio",
        "object_name": object_name,
    }