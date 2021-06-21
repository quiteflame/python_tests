from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt
from pydantic import ValidationError
from app.database.database import SessionLocal
from app.database import crud
from app.models import schemas, models
from app import security
from app.settings import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.get_user(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User deactivated"
        )
    return user


def get_current_superuser(current_user: models.User = Depends(get_current_user)):
    if not current_user.email == settings.super_user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not the superuser"
        )
    return current_user
