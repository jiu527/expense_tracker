import pytest

from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.database import Base
from app.main import app
from app.models.category import Category
from app.models.record import Record
from app.models.user import User


# 使用内存 SQLite，测试结束后数据库不会写入项目中的 expense.db。
# StaticPool 确保同一连接池中的所有线程/协程访问的是同一个内存数据库。
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Session 工厂负责为每个测试创建独立的 SQLAlchemy Session。
# 测试不会自动提交，因此测试内的数据库操作需要自行提交。
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def rebuild_tables() -> Generator[None]:
    # autouse=True 表示每个测试开始前都会执行，无需在测试函数参数中声明。
    # 先删除旧表，再根据当前 SQLAlchemy 模型重新建表，保证测试相互隔离。
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # 测试结束后清理表，避免残留数据影响下一个测试。
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db() -> Generator[Session]:
    # 为需要直接操作数据库的测试提供 Session。
    session = TestSessionLocal()
    try:
        yield session
    finally:
        # 无论测试成功或失败，都关闭 Session 释放数据库连接。
        session.close()


@pytest.fixture
def client() -> Generator[TestClient]:
    # FastAPI 的真实数据库依赖会调用应用默认的 Session 工厂。
    # 这里替换 get_db，使接口请求使用测试专用内存数据库。
    def override_get_db() -> Generator[Session]:
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    # TestClient 会模拟 HTTP 请求，并在上下文生命周期内触发应用启动/关闭逻辑。
    with TestClient(app) as test_client:
        yield test_client
    # 测试结束后移除依赖覆盖，防止影响其他测试或后续测试模块。
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    email = "test@test.com"
    password = "testpassword"

    # 注册用户
    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    # 登录用户
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    assert login_response.status_code == 200

    token = login_response.json().get("access_token")
    assert token is not None

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def login_headers(client):
    def login(email: str, password: str = "testpassword"):
        register_response = client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        assert login_response.status_code == 200

        return {
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }

    return login