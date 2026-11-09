from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # 应用配置的默认值；.env 中的同名变量可以覆盖这些值。
    app_name: str = "Expense Tracker API"
    # SQLite 相对路径以启动服务时的工作目录为基准。
    database_url: str = "sqlite:///./expense.db"
    secret_key: str = "expense-tracker-dev-secret-key-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # 从项目根目录读取 .env 中的配置。
    model_config = ConfigDict(env_file=".env")


# 项目其他模块通过 settings 使用统一的应用配置。
settings = Settings()
