from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.db import get_db
from app.core.security import decode_token
from jose import JWTError

security = HTTPBearer()

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    try:
        payload = decode_token(token.credentials)

        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise credentials_exception

    return user

def require_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(403, "Forbidden")
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user