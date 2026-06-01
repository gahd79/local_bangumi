"""FastAPI 应用入口模块。"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 — 启动/关闭调度器。"""
    # 启动时
    from .utils.logging_config import setup_logging
    from .utils.exception_handlers import register_exception_handlers

    setup_logging(debug=settings.debug)
    register_exception_handlers(app)
    logger.info("local_bangumi v%s starting...", app.version)

    from .scheduler.sync_scheduler import start_scheduler

    start_scheduler()

    yield

    # 关闭时
    from .scheduler.sync_scheduler import shutdown_scheduler

    shutdown_scheduler()
    logger.info("local_bangumi shutdown complete")


app = FastAPI(
    title="local_bangumi",
    description="A local ACGN database powered by Bangumi Archive data",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件 — 允许前端开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每个 HTTP 请求的 method、path 和耗时。"""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# 注册 API 路由
from .api import subjects, records, sync, episodes, persons, characters, relations, search  # noqa: E402

app.include_router(subjects.router)
app.include_router(records.router)
app.include_router(sync.router)
app.include_router(episodes.router)
app.include_router(persons.router)
app.include_router(characters.router)
app.include_router(relations.router)
app.include_router(search.router)


@app.get("/api/health")
def health_check():
    """健康检查端点。"""
    return {"status": "ok", "version": app.version}
