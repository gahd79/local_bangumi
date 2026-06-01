"""FastAPI 全局异常处理器。

为 4 类异常注册统一处理器：
- HTTPException：保持原有行为，记录 WARNING 日志
- RequestValidationError：422 + 友好中文提示
- SQLAlchemyError：500 + 通用数据库错误
- Exception：500 + 兜底处理
"""

import logging
import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.api")


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """HTTP 异常（4xx/5xx）处理器。"""
    if exc.status_code >= 500:
        logger.exception(
            "HTTP %d: %s %s — %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
        )
    else:
        logger.warning(
            "HTTP %d: %s %s — %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """请求参数校验失败处理器。"""
    errors = []
    for err in exc.errors():
        loc = " → ".join(str(part) for part in err["loc"])
        errors.append(f"{loc}: {err['msg']}")

    logger.warning(
        "Validation error: %s %s — %s",
        request.method,
        request.url.path,
        "; ".join(errors),
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数校验失败",
            "errors": errors,
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """数据库异常处理器。"""
    logger.exception(
        "Database error: %s %s — %s",
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "数据库操作失败，请稍后重试"},
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """未捕获异常的兜底处理器。"""
    logger.exception(
        "Unhandled exception: %s %s\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请查看日志了解详情"},
    )


def register_exception_handlers(app):
    """在 FastAPI app 上注册所有异常处理器。"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
