from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from ..dependencies import get_token_header, get_db
from ..database import crud
from ..models import schemas

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)


@router.get("/", response_model=List[schemas.User])
async def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@router.get("/me")
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user