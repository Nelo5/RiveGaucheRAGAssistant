from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    @field_validator("password")
    def strip_whitespace(cls, v: str) -> str:
        return v.replace("\x00", "").strip()



class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(..., min_length=6)
    @field_validator("password")
    def strip_whitespace(cls, v: str) -> str:
        return v.replace("\x00", "").strip()

class RegisterResponse(BaseModel):
    id: UUID
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime