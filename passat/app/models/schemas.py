from typing import List
from pydantic import BaseModel


class CredentialBase(BaseModel):
    login: str
    password: str


class CredentialCreate(CredentialBase):
    pass


class Credential(CredentialBase):
    public_id: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    public_id: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str
