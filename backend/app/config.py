"""应用配置模块，使用 pydantic-settings 管理环境变量。"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

# 项目根目录（backend/app/ → backend/ → 项目根）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """集中管理所有应用配置项。"""

    # 数据库路径：默认使用项目根目录下的 data/bangumi.db
    database_url: str = f"sqlite:///{_PROJECT_ROOT / 'data' / 'bangumi.db'}"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:18000"]
    sync_interval_hours: int = 168  # 每周同步（Bangumi 每周三更新）
    debug: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
