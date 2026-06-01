#!/usr/bin/env python3
"""手动数据同步脚本。

用法:
    # 从本地 dump 目录导入
    python scripts/sync_data.py --source local --path ./dialogue_file/dump-2026-05-26.210457Z

    # 从 GitHub 下载最新数据并导入
    python scripts/sync_data.py --source github
"""

import argparse
import logging
import sys
from pathlib import Path

# 将 backend/ 添加到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.data_sync import sync_from_github, sync_from_local

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sync_data")


def main():
    parser = argparse.ArgumentParser(
        description="local_bangumi 数据同步工具"
    )
    parser.add_argument(
        "--source",
        choices=["local", "github"],
        default="local",
        help="数据来源：local=本地dump目录, github=GitHub远程下载",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="本地 dump 目录路径（--source=local 时必需）",
    )
    args = parser.parse_args()

    if args.source == "local":
        if not args.path:
            dump_dir = str(
                Path(__file__).resolve().parent.parent
                / "dialogue_file"
                / "dump-2026-05-26.210457Z"
            )
            logger.info(f"No --path specified, using default: {dump_dir}")
        else:
            dump_dir = args.path

        if not Path(dump_dir).exists():
            logger.error(f"Dump directory not found: {dump_dir}")
            sys.exit(1)

        logger.info(f"Starting local sync from: {dump_dir}")
        result = sync_from_local(dump_dir)

        if result["success"]:
            logger.info(f"Sync complete! Total records: {result['total']}")
            for table, count in result.get("counts", {}).items():
                logger.info(f"  {table}: {count}")
            logger.info(f"Duration: {result['duration_seconds']:.1f}s")
        else:
            logger.error(f"Sync failed: {result.get('errors', [])}")
            sys.exit(1)

    elif args.source == "github":
        logger.info("Starting GitHub sync...")
        result = sync_from_github()

        if result.get("message"):
            logger.info(result["message"])
        elif result["success"]:
            logger.info(f"Sync complete! Total records: {result.get('total', 0)}")
            for table, count in result.get("counts", {}).items():
                logger.info(f"  {table}: {count}")
            logger.info(f"Version: {result.get('version', 'unknown')}")
        else:
            logger.error(f"Sync failed: {result.get('error', 'unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
