from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# 注册接口接收的数据模型。
class UserRegister(BaseModel):
    email: EmailStr = Field(..., max_length=255, title="用户邮箱", description="用户邮箱")
    # Pydantic 在字段校验阶段拦截少于 8 个字符的密码。
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        title="登录密码",
        description="登录密码不能少于 8 个字符",
    )


# 登录成功后返回的 Bearer Token 响应。
class Token(BaseModel):
    access_token: str = Field(..., title="访问令牌")
    token_type: str = Field("bearer", title="令牌类型")


# 对外返回的用户信息，不包含密码或密码哈希。
class UserResponse(BaseModel):
    id: int = Field(..., title="用户 ID")
    email: EmailStr = Field(..., title="用户邮箱")
    created_at: datetime = Field(..., title="创建时间")

    # 允许从 SQLAlchemy User 实例直接转换为响应模型。
    model_config = {"from_attributes": True}
