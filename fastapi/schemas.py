from typing import List
from pydantic import BaseModel


class CredentialBase(BaseModel):
    login: str
    password: str


class CredentialCreate(CredentialBase):
    pass


class Credential(CredentialBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    credentials: List[Credential] = []

    class Config:
        orm_mode = True
