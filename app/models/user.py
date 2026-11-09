from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):
    __tablename__ = "users"
    __label__ = "用户"

    id: Mapped[int] = mapped_column(primary_key=True, info={"label": "用户 ID"})
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, info={"label": "邮箱"})
    hashed_password: Mapped[str] = mapped_column(String(255), info={"label": "密码哈希"})
    # datetime.now 是可无参数调用的工厂函数，不能直接使用 datetime 类作为默认值。
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, info={"label": "创建时间"})