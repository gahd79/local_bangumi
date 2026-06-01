"""数据同步管理 API 路由。"""

from fastapi import APIRouter, BackgroundTasks

from ..services.data_sync import (
    get_sync_status,
    sync_from_local,
    sync_from_github,
)
from ..utils.github_fetcher import get_latest_version

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.get("/status")
def sync_status():
    """获取当前同步状态：各表记录数、最后同步时间等。"""
    return get_sync_status()


@router.get("/latest-version")
def latest_version():
    """获取 GitHub 上最新的 Archive 版本信息。"""
    version = get_latest_version()
    if not version:
        return {"error": "无法获取最新版本信息"}
    return {
        "name": version.name,
        "size": version.size,
        "created_at": version.created_at,
    }


@router.post("/trigger/local")
def trigger_local_sync(dump_dir: str):
    """触发本地数据导入（从指定目录读取 jsonlines 文件）。

    Args:
        dump_dir: 包含 .jsonlines 文件的目录绝对路径
    """
    return sync_from_local(dump_dir)


@router.post("/trigger/github")
async def trigger_github_sync(background_tasks: BackgroundTasks):
    """触发从 GitHub 下载最新 Archive 数据并导入（后台执行）。

    由于数据量大，此操作放在后台执行。
    """
    # 先获取版本信息确认可用
    version = get_latest_version()
    if not version:
        return {"success": False, "error": "无法获取最新版本信息"}

    # 后台执行同步
    background_tasks.add_task(sync_from_github)
    return {
        "success": True,
        "message": f"同步任务已开始（版本: {version.name}），请通过 GET /api/sync/status 查看进度",
    }
