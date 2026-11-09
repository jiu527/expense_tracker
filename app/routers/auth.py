from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import Token, UserRegister, UserResponse

# 认证接口统一使用 /auth 前缀，并归类到 Swagger 的“认证”分组。
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # 注册前检查邮箱，避免违反 User.email 的唯一约束。
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已注册")

    # 密码仅以 bcrypt 哈希保存，不在数据库中保存明文密码。
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    # 刷新对象以获取数据库生成的 id 和创建时间。
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 表单中的 username 字段用于接收用户邮箱。
    user = db.query(User).filter(User.email == form_data.username).first()
    # 用户不存在或密码校验失败时，统一返回认证失败。
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token 的 subject 为用户 ID，后续由认证依赖解析并查询用户。
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # get_current_user 会先校验 Bearer Token，再返回对应用户。
    return current_user
