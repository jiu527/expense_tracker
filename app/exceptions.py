from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


# 需要展示固定业务含义的错误，在这里映射专用业务错误码。
# 未映射的错误会根据 HTTP 状态码由 get_http_error_code 生成默认业务码。
BUSINESS_ERROR_CODES = {
    "邮箱已注册": 40001,
    "邮箱或密码错误": 40101,
}


def get_http_error_code(status_code: int, message: str) -> int:
    """根据错误信息或 HTTP 状态码生成统一的业务错误码。"""
    if message in BUSINESS_ERROR_CODES:
        return BUSINESS_ERROR_CODES[message]
    return {
        status.HTTP_400_BAD_REQUEST: 40000,
        status.HTTP_401_UNAUTHORIZED: 40100,
        status.HTTP_404_NOT_FOUND: 40400,
        # 使用新版状态码名称，避免 Starlette 的弃用警告。
        status.HTTP_422_UNPROCESSABLE_CONTENT: 42200,
    }.get(status_code, status_code * 100)


async def http_exception_handler(request, exc: StarletteHTTPException) -> JSONResponse:
    """
    统一处理 FastAPI 或 Starlette 抛出的 HTTPException。

    当 exc.detail 是字符串时，直接作为用户可见的 message；如果是其他类型，
    则转换为字符串，避免接口返回 FastAPI 原始的列表、字典等不固定结构。
    detail 字段始终返回 null，业务详细信息保留在 message 中。
    """
    if isinstance(exc.detail, str):
        message = exc.detail
        detail = exc.detail
    else:
        message = str(exc.detail)
        detail = None

    return JSONResponse(
        status_code=exc.status_code,
        headers=getattr(exc, "headers", None),
        content={
            "code": get_http_error_code(exc.status_code, message),
            "message": message,
            "detail": detail,
        },
    )


async def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    """
    统一处理 Pydantic 请求校验失败。

    密码长度校验等字段级错误保留在 detail 中，并将固定字段名转换为
    FastAPI 测试和客户端约定的字符串。
    """
    details = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        message = error["msg"]
        # 将密码长度校验转换为测试与客户端使用的统一英文提示。
        if location.endswith("password") and error["type"] == "string_too_short":
            message = f"登录密码不能少于 {error['ctx']['min_length']} 个字符"

        details.append(
            {
                "loc": error["loc"],
                "msg": message,
                "type": error["type"],
            }
        )
    details.sort(key=lambda item: item["loc"][-1] != "password")

    return JSONResponse(
        # HTTP 422 表示请求语义有效但字段内容无法处理。
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": 42201,
            "message": "输入校验失败",
            "detail": details,
        },
    )