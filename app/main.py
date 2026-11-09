from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.records import router as records_router
from app.routers.stats import router as stats_router
from app.exceptions import http_exception_handler, validation_exception_handler


# 创建 FastAPI 应用实例，应用标题会显示在自动生成的 API 文档中。
app = FastAPI(title="Expense Tracker API")

# 注册全局异常处理器，统一处理 HTTPException 和请求校验失败的异常。
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 注册路由器，将各个模块的路由整合到主应用中。
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(records_router)
app.include_router(stats_router)


@app.get("/health")
def health():
    # 健康检查接口用于确认服务是否正常运行，不涉及数据库操作。
    return {"status": "ok"}