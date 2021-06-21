import uvicorn

from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import models, schemas
from .database.database import engine, SessionLocal
from .dependencies import get_db
from .internal import admin
from app.routers import credentials, users
from app.settings import settings
from app.database import crud
from app import security

api = FastAPI()

api.include_router(users.router)
api.include_router(credentials.router)
api.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    responses={status.HTTP_418_IM_A_TEAPOT: {"description": "I'm a teapot"}},
)


@api.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    user = crud.get_user_by_email(db, settings.super_user_email)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.super_user_email, password=settings.super_user_password
        )
        crud.create_user(db, user_in)
    db.close()


@api.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    return {
        "access_token": security.create_access_token(subject=user.public_id),
        "token_type": "bearer",
    }


if __name__ == "__main__":
    # python3 -m app.main
    uvicorn.run("app.main:api", port=8000, reload=True, access_log=False)
