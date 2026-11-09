import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings


# 使用 bcrypt 生成密码哈希，并将结果转换为数据库可保存的字符串。
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# 校验登录密码是否与数据库中保存的 bcrypt 哈希匹配。
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# 创建包含用户 ID 和过期时间的 JWT 访问令牌。
def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)