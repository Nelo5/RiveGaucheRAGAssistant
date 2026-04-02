from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas

# Настройки JWT
SECRET_KEY = "your-secret-key-change-this-in-production"  # В продакшене используйте переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Исправленная инициализация CryptContext
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Явно указываем количество раундов
)

def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password):
    """Хеширование пароля"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )

def authenticate_user(db: Session, username: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str, db: Session):
    """Получение текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, user_id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def check_admin_role(user: models.User):
    """Проверка прав администратора"""
    if user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return True