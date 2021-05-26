import schemas
import models
from sqlalchemy.orm import Session
from passlib.hash import bcrypt


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_email_password(db: Session, email: str, password: str):
    return db.query(models.User).filter(models.User.email == email and models.User.hashed_password == bcrypt.hash(password)).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hash(user.password)
    db_user = models.User(
        email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_credentials(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Credentials).offset(skip).limit(limit).all()


def create_user_credential(db: Session, item: schemas.CredentialCreate, user_id: int):
    db_item = models.Credential(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
