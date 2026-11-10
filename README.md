# Expense Tracker

个人收支记录 REST API，支持账号认证、分类与收支记录管理，以及按月、按分类汇总统计。接口文档由 FastAPI 自动生成。

## 功能

- 邮箱注册、登录和 JWT Bearer Token 认证
- 收入/支出分类的创建、查询、修改和删除
- 收支记录的创建、查询、修改和删除
- 记录分页，以及日期、分类、收支类型筛选
- 金额校验：必须大于 0，最多两位小数
- 按月统计收入、支出和结余
- 在指定日期区间内按分类汇总
- 按用户隔离分类、记录和统计数据
- Alembic 数据库迁移

## 技术栈与架构

- **API**：Python、FastAPI、Uvicorn
- **数据校验**：Pydantic v2、pydantic-settings
- **数据库**：SQLAlchemy ORM；本地默认 SQLite，Docker/生产环境使用 PostgreSQL
- **迁移**：Alembic
- **认证**：JWT（PyJWT）、bcrypt 密码哈希
- **测试**：pytest、FastAPI TestClient、内存 SQLite
- **部署**：Docker、Docker Compose；可部署到 Render

主要代码分层：

| 目录/文件 | 职责 |
|---|---|
| `app/routers/` | HTTP 路由、请求处理和业务流程 |
| `app/schemas/` | Pydantic 请求/响应模型及字段校验 |
| `app/models/` | SQLAlchemy 数据模型 |
| `app/core/` | 数据库依赖、JWT 和密码安全逻辑 |
| `app/database.py` | SQLAlchemy Engine、Session 和声明式基类 |
| `app/config.py` | 读取环境变量及 `.env` 配置 |
| `app/exceptions.py` | 统一 HTTP 和请求校验错误响应 |
| `alembic/` | 数据库迁移脚本 |
| `tests/` | API 自动化测试 |

## API 接口

Swagger UI：`/docs`  
OpenAPI JSON：`/openapi.json`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| `GET` | `/health` | 健康检查 | 否 |
| `POST` | `/auth/register` | 注册账号 | 否 |
| `POST` | `/auth/login` | 登录并获取 Token | 否 |
| `GET` | `/auth/me` | 获取当前用户 | 是 |
| `POST` | `/categories` | 创建分类 | 是 |
| `GET` | `/categories` | 查询当前用户的分类 | 是 |
| `PATCH` | `/categories/{category_id}` | 修改分类 | 是 |
| `DELETE` | `/categories/{category_id}` | 删除分类 | 是 |
| `POST` | `/records` | 创建收支记录 | 是 |
| `GET` | `/records` | 分页查询和筛选记录 | 是 |
| `PATCH` | `/records/{record_id}` | 修改记录 | 是 |
| `DELETE` | `/records/{record_id}` | 删除记录 | 是 |
| `GET` | `/stats/monthly` | 按年月汇总收支和结余 | 是 |
| `GET` | `/stats/by-category` | 按分类汇总日期区间内的记录 | 是 |

记录查询支持 `start`、`end`、`category_id`、`type`、`page`、`page_size` 参数。分类统计使用 `start` 和 `end` 日期参数；月度统计使用 `year` 和 `month`。

登录接口使用 OAuth2 表单，不是 JSON：表单字段为 `username`（填写注册邮箱）和 `password`。登录成功后，在 Swagger UI 点击 **Authorize** 输入 Bearer Token，或在请求中添加：

```text
Authorization: Bearer <access_token>
```

## 本地运行

需要 Python 3.13 或兼容版本。

PowerShell 示例：

```powershell
cd D:\Code\Python\expense_tracker
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

在项目根目录创建 `.env`：

```dotenv
DATABASE_URL=sqlite:///./expense.db
SECRET_KEY=replace-with-a-long-random-development-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

`.env` 不应提交到 Git。上面的 SQLite URL 和密钥仅用于本地开发；生产环境应使用 Render 环境变量和 PostgreSQL。`DATABASE_URL` 支持 SQLite 和 PostgreSQL，例如：

```text
postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
```

初始化数据库并启动 API：

```powershell
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

打开 <http://127.0.0.1:8000/docs> 查看接口文档；健康检查地址为 <http://127.0.0.1:8000/health>。

## Docker 启动

项目根目录的 `docker-compose.yml` 启动 FastAPI API 和 PostgreSQL，并使用 `postgres_data` 命名卷持久化数据库：

```powershell
docker compose up --build -d
docker compose logs -f api
```

访问 <http://localhost:8000/docs>。停止服务但保留数据库：

```powershell
docker compose down
```

**谨慎使用** `docker compose down -v`：`-v` 会删除 PostgreSQL 数据卷及其中的数据。Compose 文件中的数据库密码和 JWT 密钥是本地开发示例值，生产环境必须换成安全值并通过部署平台的环境变量配置。

Docker 容器启动时会先执行 `alembic upgrade head`，然后启动 Uvicorn。Dockerfile 使用 Render 提供的 `PORT` 环境变量；未设置时默认监听 `10000`。

## 测试

安装依赖后，在项目根目录运行：

```powershell
python -m pytest -q
```

当前测试套件共 **26 个用例**，覆盖认证、分类 CRUD 和越权、记录 CRUD/分页/筛选/金额校验，以及统计结果和用户数据隔离。

## 部署地址

- **Render API**：`https://expense-tracker-edox.onrender.com`
- **Swagger UI**：`https://expense-tracker-edox.onrender.com/docs`
- **健康检查**：`https://expense-tracker-edox.onrender.com/health`

Render Web Service 需设置 `DATABASE_URL`、`SECRET_KEY` 和 `ACCESS_TOKEN_EXPIRE_MINUTES` 环境变量。数据库 URL 使用 PostgreSQL Internal Database URL，并采用 `postgresql+psycopg://` 驱动前缀。不要将真实连接串或密钥写入仓库。

## 实际踩坑记录

1. **登录请求格式不是 JSON**：登录端点使用 `OAuth2PasswordRequestForm`。测试或客户端若发送 JSON，FastAPI 会因缺少表单字段返回 `422`。应以表单编码发送 `username` 和 `password`，其中 `username` 填注册邮箱。
2. **SQLite 的跨线程检查**：FastAPI TestClient 可能在不同线程处理请求，测试用 SQLite Engine 需要设置 `connect_args={"check_same_thread": False}`，并使用共享内存连接池，避免线程检查错误或测试读到不同的内存数据库。
3. **越权资源要验证不可区分性**：分类和记录的更新、删除按“资源 ID + 当前用户 ID”查询；资源不存在或属于其他用户时都返回 `404`。测试应创建两个用户，让其中一人尝试修改/删除另一人的资源，并确认返回 `404` 且所有者的数据未变。
