from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Схемы для пользователей
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Схемы для токенов
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: UserRole

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None