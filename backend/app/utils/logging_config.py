"""应用日志配置模块。

配置 RotatingFileHandler + StreamHandler，统一日志格式。
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(debug: bool = True, log_dir: str | None = None) -> None:
    """初始化全局日志配置。

    Args:
        debug: True 时控制台输出 DEBUG 级别，文件输出 INFO
        log_dir: 日志目录，默认 <项目根>/data/logs/
    """
    if log_dir is None:
        log_dir = str(
            Path(__file__).resolve().parent.parent.parent.parent / "data" / "logs"
        )
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / "bangumi.log"

    # 根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # 格式
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 清除已有的 handlers（避免重复注册）
    root_logger.handlers.clear()

    # 文件输出 — RotatingFileHandler（10MB x 5）
    file_handler = RotatingFileHandler(
        str(log_file),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 调低第三方库的日志级别（避免噪音）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.getLogger("app").info("Logging configured (debug=%s)", debug)
