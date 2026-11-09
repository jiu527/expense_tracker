from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    # 为当前请求创建独立数据库会话。
    db = SessionLocal()
    try:
        yield db
    finally:
        # 请求结束后关闭数据库会话，释放连接。
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供有效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Authorization 请求头格式应为：Bearer <token>
    token = credentials.credentials

    # 用于请求头无效、Token 无效或用户不存在时统一返回认证错误。
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 校验 JWT 签名，并解析其中保存的用户 ID。
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except (jwt.JWTError, ValueError):
        raise credentials_exception

    # 根据 Token 中的用户 ID 查询数据库中的用户。
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
