from pydantic import BaseModel, Field


class MonthlyStatsResponse(BaseModel):
    year: int = Field(..., title="年份")
    month: int = Field(..., title="月份")
    income: float = Field(..., title="总收入")
    expense: float = Field(..., title="总支出")
    balance: float = Field(..., title="结余")


class CategoryStatsResponse(BaseModel):
    category_id: int = Field(..., title="分类 ID")
    category_name: str = Field(..., title="分类名称")
    category_type: str = Field(..., title="分类类型")
    amount: float = Field(..., title="金额合计")
    percentage: float = Field(..., title="占比")
