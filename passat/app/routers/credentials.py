from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..database import crud
from ..models import schemas

router = APIRouter(
    prefix="/credentials",
    tags=["credentials"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)


@router.get("/", response_model=List[schemas.Credential])
async def read_credentials(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    credentials = crud.get_credentials(db, user_id=current_user.id)

    return credentials


@router.get("/{credential_id}", response_model=schemas.Credential)
async def read_credential(credential_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    credential = crud.get_credential(db, credential_id=credential_id, user_id=current_user.id)

    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    return credential


@router.put("/{credential_id}", response_model=schemas.Credential)
async def update_credential(credential_id: str, model: schemas.CredentialCreate, db: Session = Depends(get_db),
                            current_user=Depends(get_current_user)):
    credential = crud.get_credential(db, credential_id=credential_id, user_id=current_user.id)

    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    credential.login = model.login
    credential.password = model.password

    db.update(credential)
    db.commit()
    db.refresh(credential)

    return credential
