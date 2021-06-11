from .. import security
from ..models import models, schemas
from sqlalchemy.orm import Session
from passlib.hash import bcrypt


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.public_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


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


def deactivate_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.public_id == user_id).first()
    if not db_user:
        return None
    db_user.is_active = False
    db.update(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def activate_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.public_id == user_id).first()
    if not db_user:
        return None
    db_user.is_active = True
    db.update(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_credentials(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Credential).filter(models.Credential.owner_id == user_id).offset(skip).limit(limit).all()


def get_credential(db: Session, credential_id: str, user_id: int):
    return db.query(models.Credential).filter(
        models.Credential.public_id == credential_id and models.Credential.owner_id == user_id).first()


def create_credential(db: Session, item: schemas.CredentialCreate, user_id: int):
    db_item = models.Credential(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db=db, email=email)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user
