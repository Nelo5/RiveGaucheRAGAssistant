from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .auth import get_current_user, check_admin_role
from . import models

security = HTTPBearer()

def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Зависимость для получения текущего пользователя"""
    token = credentials.credentials
    return get_current_user(token, db)

def get_current_active_user(
    current_user: models.User = Depends(get_current_user_dependency)
):
    """Зависимость для получения активного пользователя"""
    return current_user

def get_admin_user(
    current_user: models.User = Depends(get_current_user_dependency)
):
    """Зависимость для проверки прав администратора"""
    check_admin_role(current_user)
    return current_user