from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# Engine 管理数据库连接；首次实际执行数据库操作时才会创建 SQLite 文件。
engine = create_engine(
    settings.database_url,
    # FastAPI 可能在不同线程处理请求，因此允许 SQLite 连接跨线程使用。
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
# 每个请求可以通过 SessionLocal 创建独立的数据库会话。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 所有 SQLAlchemy 数据模型都继承此基类。
class Base(DeclarativeBase):
    pass