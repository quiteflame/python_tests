from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_token_header, get_db
from ..database import crud
from ..models import schemas

router = APIRouter(
    prefix="/credentials",
    tags=["credentials"],
    # dependencies=[Depends(get_token_header)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    },
)


@router.get("/", response_model=List[schemas.Credential])
async def read_credentials(db: Session = Depends(get_db)):
    credentials = crud.get_credentials(db)
    
    return credentials


@router.get("/{credential_id}", response_model=schemas.Credential)
async def read_item(credential_id: str, db: Session = Depends(get_db)):
    credential = crud.get_credential(db, credential_id)
    
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    
    return credential


@router.put("/{credential_id}", response_model=schemas.Credential)
async def update_credential(credential_id: str, model: schemas.CredentialCreate, db: Session = Depends(get_db)):
    credential = crud.get_credential(db, credential_id)
    
    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    
    credential.login = model.login
    credential.password = model.password
    
    db.update(credential)
    db.commit()
    db.refresh(credential)

    return credential