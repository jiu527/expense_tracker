from typing import Literal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=50, title="分类名称", description="分类名称")
    type: Literal["income", "expense"] = Field(..., title="分类类型", description="分类类型")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, max_length=50, title="分类名称", description="分类名称")
    type: Literal["income", "expense"] | None = Field(None, title="分类类型", description="分类类型")


class CategoryResponse(BaseModel):
    id: int = Field(..., title="分类 ID")
    user_id: int = Field(..., title="用户 ID")
    name: str = Field(..., title="分类名称")
    type: str = Field(..., title="分类类型")

    model_config = {"from_attributes": True}
