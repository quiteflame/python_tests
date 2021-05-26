from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    credentials = relationship("Credentials", back_populates="owner")


class Credentials(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True)
    password = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="credentials")
