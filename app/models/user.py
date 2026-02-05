from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    emailVerified: bool = Field(default=False)  # Set default to False instead of None
    image: Optional[str] = Field(default=None)

class UserCreate(SQLModel):
    email: str
    name: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserPublic(SQLModel):
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime
