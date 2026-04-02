from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # Будет хранить хеш пароля
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())