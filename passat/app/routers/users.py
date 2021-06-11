from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from ..dependencies import get_current_user, get_db, get_current_superuser
from ..database import crud
from ..models import schemas

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(get_current_user)])
async def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@router.get("/me", response_model=schemas.User)
async def read_user_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(get_current_user)])
async def read_user(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.post("/", response_model=schemas.User, dependencies=[Depends(get_current_superuser)])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db, user=user)


@router.put("/{user_id}/deactivate", response_model=schemas.User, dependencies=[Depends(get_current_superuser)])
async def deactivate_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.deactivate_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="User not found")
    return db_user


@router.put("/{user_id}/activate", response_model=schemas.User, dependencies=[Depends(get_current_superuser)])
async def activate_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.activate_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="User not found")
    return db_user
