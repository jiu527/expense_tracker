from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class RecordCreate(BaseModel):
    category_id: int = Field(..., gt=0, title="分类 ID", description="分类 ID")
    type: Literal["income", "expense"] = Field(..., title="分类类型", description="分类类型")
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, title="金额", description="金额")
    note: str | None = Field(None, max_length=255, title="备注", description="备注")
    occurred_at: date = Field(..., title="记录日期", description="记录日期")


class RecordUpdate(BaseModel):
    category_id: int | None = Field(None, gt=0, title="分类 ID", description="分类 ID")
    note: str | None = Field(None, max_length=255, title="备注", description="备注")
    type: Literal["income", "expense"] | None = Field(None, title="分类类型", description="分类类型")
    amount: Decimal | None = Field(
        None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        title="金额",
        description="金额",
    )
    occurred_at: date | None = Field(None, title="记录日期", description="记录日期")


class RecordResponse(BaseModel):
    id: int = Field(..., title="记录 ID")
    user_id: int = Field(..., title="用户 ID")
    category_id: int = Field(..., title="分类 ID")
    amount: Decimal = Field(..., max_digits=10, decimal_places=2, title="金额")
    note: str | None = Field(None, title="备注")
    type: str = Field(..., title="分类类型")
    occurred_at: date = Field(..., title="记录日期")
    created_at: datetime = Field(..., title="创建时间")

    model_config = {"from_attributes": True}


class RecordPage(BaseModel):
    total: int = Field(..., title="总数")
    page: int = Field(..., title="页码")
    page_size: int = Field(..., title="每页数量")
    items: list[RecordResponse] = Field(..., title="记录列表")