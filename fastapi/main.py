import jwt
import crud
import models
import schemas

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List
from sqlalchemy.orm import Session

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')
JWT_SECRET = 'n~2NAPpm?pCJNn2HL!)3'

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=['HS256'])
        user = crud.get_user(db=db, user_id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user

# Paths


@app.post("/api/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email_password(
        db=db, email=form_data.username, password=form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

    token = jwt.encode(payload=schemas.User.from_orm(
        user).dict(), key=JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}


@app.post('/api/users', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get('/api/users/me', response_model=schemas.User)
async def me(user: schemas.User = Depends(get_current_user)):
    return user
