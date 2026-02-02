# Standard library imports
import os
import uuid # universally unique identifiers
from datetime import timedelta
import io # I/O operations

# Third-party imports
from fastapi import FastAPI, Depends, UploadFile, File, Query
from minio import Minio
from sqlalchemy.orm import Session
from PIL import Image # Python Imaging Library
from fastapi import HTTPException
from passlib.context import CryptContext

# Local project imports
from . import models, schemas, database
from .database import engine, SessionLocal
from .models import Base, Photo
from .security import create_access_token

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

# Registration endpoint
@app.post("/auth/register", response_model=schemas.UserResponse)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    # Check if email already exists
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Login endpoint
@app.post("/auth/login")
def login_user(
    data: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# Test upload endpoint (for manual testing only)
@app.post("/photos/upload-test")
async def upload_test(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Generate keys
    file_ext = file.filename.split(".")[-1]
    object_key = f"{uuid.uuid4()}.{file_ext}"
    thumb_key = f"thumb_{object_key}"

    # Upload ORIGINAL image
    minio_internal.put_object(
        bucket_name="photos",
        object_name=object_key,
        data=file.file,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=file.content_type,
    )

    # Reset file pointer (CRITICAL)
    file.file.seek(0)

    # Generate thumbnail (in memory)
    thumb_data = generate_thumbnail(file)

    # Upload THUMBNAIL
    minio_internal.put_object(
        bucket_name="photos",
        object_name=thumb_key,
        data=thumb_data,
        length=thumb_data.getbuffer().nbytes,
        content_type="image/jpeg",
    )

    # Save metadata to Postgres
    photo = Photo(
        title=file.filename,
        tags=[],
        object_key=object_key,
        thumb_key=thumb_key,
        original_filename=file.filename,
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    # Return response
    return {
        "id": photo.id,
        "title": photo.title,
        "object_key": object_key,
        "thumb_key": thumb_key,
        "created_at": photo.created_at,
    }

# Create photo metadata
@app.post("/photos", response_model=schemas.PhotoResponse)
def create_photo(photo: schemas.PhotoCreate, db: Session = Depends(get_db)):
    db_photo = models.Photo(**photo.dict())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

# List photos with pagination and optional tag filtering
@app.get("/photos", response_model=schemas.PhotoListResponse)
def list_photos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tag: str | None = Query(None),
    db: Session = Depends(get_db),
):
    # Base query
    query = db.query(models.Photo)

    # Optional tag filtering
    if tag:
        query = query.filter(models.Photo.tags.contains([tag]))

    # Get total count of photos (after filtering)
    total = query.count()

    # Query photos from the database with pagination
    photos = (
        query
        .order_by(models.Photo.created_at.desc()) # equivalent to ORDER BY created_at DESC
        .offset(offset) # equivalent to OFFSET :offset
        .limit(limit) # equivalent to LIMIT :limit
        .all()
    )

    return {
        "items": [
            {
                "id": photo.id,
                "title": photo.title,
                "tags": photo.tags or [],
                "original_filename": photo.original_filename,
                "image_url": get_presigned_url(photo.object_key),
                "thumbnail_url": ( # see if thumb_key exists, else give no error 
                    get_presigned_url(photo.thumb_key)
                    if photo.thumb_key
                    else None
                ),
                "created_at": photo.created_at,
            }
            for photo in photos
        ],
        "limit": limit,
        "offset": offset,
        "total": total,
    }

# Get photo by ID
@app.get("/photos/{photo_id}", response_model=schemas.PhotoResponse)
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return {
        "id": photo.id,
        "title": photo.title,
        "tags": photo.tags or [],
        "original_filename": photo.original_filename,
        "image_url": get_presigned_url(photo.object_key),
        "thumbnail_url": (
            get_presigned_url(photo.thumb_key)
            if photo.thumb_key
            else None
        ),
        "created_at": photo.created_at,
    }

@app.delete("/photos/{photo_id}", status_code=204)
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    # 1. Find photo
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # 2. Delete original image from MinIO
    try:
        minio_internal.remove_object("photos", photo.object_key)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image from storage: {str(e)}",
        )

    # 3. Delete thumbnail if exists
    if photo.thumb_key:
        try:
            minio_internal.remove_object("photos", photo.thumb_key)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete thumbnail from storage: {str(e)}",
            )

    # 4. Delete DB row
    db.delete(photo)
    db.commit()

    # 5. 204 No Content (correct REST behavior)
    return

# Update photo metadata
@app.patch("/photos/{photo_id}", response_model=schemas.PhotoResponse)
def update_photo(
    photo_id: int,
    updates: schemas.PhotoUpdate,
    db: Session = Depends(get_db),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if updates.title is not None:
        photo.title = updates.title

    if updates.tags is not None:
        photo.tags = updates.tags

    db.commit()
    db.refresh(photo)

    return {
        "id": photo.id,
        "title": photo.title,
        "tags": photo.tags or [],
        "original_filename": photo.original_filename,
        "image_url": get_presigned_url(photo.object_key),
        "thumbnail_url": (
            get_presigned_url(photo.thumb_key)
            if photo.thumb_key
            else None
        ),
        "created_at": photo.created_at,
    }

# Thumbnail helper function
def generate_thumbnail(file: UploadFile, max_size=(300, 300)) -> bytes:
    image = Image.open(file.file)
    image.thumbnail(max_size)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    return buffer

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   

# Password hashing helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Password verification helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
