from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, RegisterResponse, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=RegisterResponse)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = auth_service.register(db, data.email, data.password)
    if not user:
        raise HTTPException(400, "Email already exists")
    return RegisterResponse(id=str(user.id), email=user.email)

@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    token = auth_service.login(db, data.email, data.password)
    if not token:
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(access_token=token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at
    )