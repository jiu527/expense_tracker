FROM python:3.13-slim

# 禁用 Python 缓存文件，并确保容日志实时输出。
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 先复制依赖清单以利用 Docker 的构建缓存。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用和数据库迁移文件。
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# 容器启动时先执行迁移，再启动 API 服务。
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
