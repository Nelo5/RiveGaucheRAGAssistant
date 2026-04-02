from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from .database import engine, get_db, SessionLocal
from . import models, schemas, auth
from .dependencies import get_current_active_user, get_admin_user
from .auth import ACCESS_TOKEN_EXPIRE_MINUTES

# Создаем таблицы
def init_db():
    try:
        models.Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Создаем админа по умолчанию, если его нет
        db = SessionLocal()
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin_user = models.User(
                username="admin",
                password=auth.get_password_hash("admin123"),
                role=models.UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: admin / admin123")
        db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

init_db()

app = FastAPI(title="User Management API with JWT")

# ==================== Публичные эндпоинты ====================

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Создаем нового пользователя
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Авторизация и получение JWT токена"""
    # Аутентификация
    authenticated_user = auth.authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={
            "sub": authenticated_user.username,
            "user_id": authenticated_user.id,
            "role": authenticated_user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user_id=authenticated_user.id,
        username=authenticated_user.username,
        role=authenticated_user.role
    )

# ==================== Защищенные эндпоинты (требуют авторизацию) ====================

@app.get("/users/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user

@app.put("/users/me", response_model=schemas.UserResponse)
def update_current_user(
    username: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить имя текущего пользователя"""
    # Проверяем, не занято ли новое имя
    existing_user = db.query(models.User).filter(
        models.User.username == username,
        models.User.id != current_user.id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    current_user.username = username
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/users/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сменить пароль"""
    # Проверяем старый пароль
    if not auth.verify_password(old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Устанавливаем новый пароль
    current_user.password = auth.get_password_hash(new_password)
    db.commit()
    return {"message": "Password changed successfully"}

# ==================== Эндпоинты администратора ====================

@app.get("/admin/users", response_model=List[schemas.UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей (только для админов)"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/admin/users/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Получить пользователя по ID (только для админов)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: schemas.UserRole,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Изменить роль пользователя (только для админов)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role
    db.commit()
    return {"message": f"User role changed to {role.value}"}

@app.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Удалить пользователя (только для админов)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.get("/")
def root():
    return {
        "message": "User Management API with JWT",
        "endpoints": {
            "public": ["/register", "/login"],
            "protected": ["/users/me", "/users/me/update", "/users/change-password"],
            "admin": ["/admin/users", "/admin/users/{id}", "/admin/users/{id}/role"]
        }
    }