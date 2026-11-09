from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Record(Base):
    __tablename__ = "records"
    __label__ = "记录"

    id: Mapped[int] = mapped_column(primary_key=True, info={"label": "记录 ID"})
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, info={"label": "用户 ID"})
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), info={"label": "分类 ID"})
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), info={"label": "金额"})
    type: Mapped[str] = mapped_column(String(10), info={"label": "记录类型"})
    note: Mapped[str | None] = mapped_column(String(255), nullable=True, info={"label": "备注"})
    occurred_at: Mapped[date] = mapped_column(index=True, info={"label": "记录日期"})
    # 插入记录时由 SQLAlchemy 调用 datetime.now 生成创建时间。
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, info={"label": "创建时间"})