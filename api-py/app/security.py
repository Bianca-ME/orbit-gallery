from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DELTA
from .database import get_db
from . import models

# Global objects / configuration -- a reusable dependency object
# OAuth2 token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Helper functions -- don't depend on Depends()
# Create JWT token
def create_access_token(data: dict) -> str:
    """
    data: payload data (usually {"sub": user_email or user_id})
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_DELTA
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# Decode and verify JWT token
def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        return None

# FastAPI Dependencies -- Depends() lives here
# Dependency to get current user from token
# The gatekeeper for protected endpoints -- use this in Depends() to require auth
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email: str | None = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
