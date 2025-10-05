from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database

app = FastAPI()

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