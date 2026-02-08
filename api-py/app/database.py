from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string:
# postgres (user) : postgres (password)
# postgres (service name from docker-compose)
# 5432 (default port)
# orbit (database name)
DATABASE_URL = "postgresql://postgres:postgres@pg-orbit:5432/orbit"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # to check if connection is alive with the DB before using it
)

# Each request will get its own database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# Base class for SQLAlchemy models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
