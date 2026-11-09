from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    __label__ = "分类"

    id: Mapped[int] = mapped_column(primary_key=True, info={"label": "分类 ID"})
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, info={"label": "用户 ID"})
    name: Mapped[str] = mapped_column(String(50), info={"label": "分类名称"})
    type: Mapped[str] = mapped_column(String(10), info={"label": "分类类型"})