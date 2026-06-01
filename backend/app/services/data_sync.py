"""数据同步编排服务。

整合下载 → 解析 → 导入的完整流程，管理同步状态。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from sqlalchemy import func

from ..database import SessionLocal
from ..models import (
    Subject,
    Episode,
    Person,
    Character,
    SubjectRelation,
    SubjectCharacter,
    SubjectPerson,
    PersonCharacter,
    PersonRelation,
)
from ..utils.github_fetcher import fetch_latest_to_dir, get_latest_version
from .data_import import import_all_from_dir

logger = logging.getLogger(__name__)

# 同步状态文件
SYNC_STATE_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sync_state.json"


def _get_table_counts(db) -> Dict[str, int]:
    """获取各表记录数。"""
    tables = {
        "subjects": Subject,
        "episodes": Episode,
        "persons": Person,
        "characters": Character,
        "subject_relations": SubjectRelation,
        "subject_characters": SubjectCharacter,
        "subject_persons": SubjectPerson,
        "person_characters": PersonCharacter,
        "person_relations": PersonRelation,
    }
    counts = {}
    for name, model in tables.items():
        counts[name] = db.query(func.count(model.id)).scalar() or 0
    return counts


def _load_sync_state() -> Dict:
    """读取同步状态。"""
    if SYNC_STATE_FILE.exists():
        try:
            return json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "last_sync": None,
        "last_version": None,
        "total_records": 0,
    }


def _save_sync_state(state: Dict):
    """保存同步状态。"""
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def sync_from_local(
    dump_dir: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> Dict:
    """从本地 dump 目录导入数据。

    Args:
        dump_dir: 包含 .jsonlines 文件的目录路径
        progress_callback: 可选的进度回调 (table_name, current, total)

    Returns:
        dict: {"success": bool, "counts": {...}, "errors": [...], "duration_seconds": float}
    """
    start = datetime.utcnow()
    errors = []

    logger.info(f"Starting local sync from: {dump_dir}")

    try:
        counts = import_all_from_dir(dump_dir, progress_callback)
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        errors.append(str(e))
        counts = {}

    duration = (datetime.utcnow() - start).total_seconds()

    # 更新同步状态
    total = sum(counts.values())
    state = {
        "last_sync": datetime.utcnow().isoformat(),
        "last_version": f"local:{dump_dir}",
        "total_records": total,
        "table_counts": counts,
    }
    _save_sync_state(state)

    logger.info(f"Sync finished in {duration:.1f}s, total records: {total}")

    return {
        "success": len(errors) == 0,
        "counts": counts,
        "total": total,
        "errors": errors,
        "duration_seconds": duration,
    }


def sync_from_github(
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> Dict:
    """从 GitHub 下载最新 Archive 数据并导入。

    Returns:
        dict: {"success": bool, "version": str, "counts": {...}, "duration_seconds": float}
    """
    # 获取版本信息
    latest = get_latest_version()
    if not latest:
        return {"success": False, "error": "无法获取最新版本信息"}

    # 检查是否需要更新
    state = _load_sync_state()
    if state.get("last_version") == latest.name:
        logger.info(f"Already at latest version: {latest.name}")
        return {
            "success": True,
            "version": latest.name,
            "counts": {},
            "message": "已是最新版本，无需同步",
            "duration_seconds": 0,
        }

    # 下载到项目缓存目录
    cache_dir = str(
        Path(__file__).resolve().parent.parent.parent.parent
        / "data" / "cache" / "github_wiki"
    )

    logger.info(f"Downloading to {cache_dir}...")
    file_paths = fetch_latest_to_dir(cache_dir)
    if not file_paths:
        return {"success": False, "error": "下载数据失败"}

    # 找到解压后的目录
    dump_dir = str(Path(list(file_paths.values())[0]).parent)

    # 导入
    result = sync_from_local(dump_dir, progress_callback)

    if result["success"]:
        state = _load_sync_state()
        state["last_version"] = latest.name
        _save_sync_state(state)

    result["version"] = latest.name
    return result


def get_sync_status() -> Dict:
    """获取当前同步状态。"""
    state = _load_sync_state()
    db = SessionLocal()
    try:
        counts = _get_table_counts(db)
    finally:
        db.close()

    return {
        "last_sync": state.get("last_sync"),
        "last_version": state.get("last_version"),
        "total_records": state.get("total_records", 0),
        "table_counts": counts,
        "has_data": any(v > 0 for v in counts.values()),
    }
