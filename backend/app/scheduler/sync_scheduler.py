"""定时同步调度器 — 使用 APScheduler 每周三自动同步。"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..services.data_sync import sync_from_github

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _sync_job():
    """同步任务执行函数。"""
    logger.info("Scheduled sync job started...")
    try:
        result = sync_from_github()
        if result.get("success"):
            logger.info(f"Scheduled sync completed: {result.get('total', 0)} records")
        elif result.get("message"):
            logger.info(f"Scheduled sync skipped: {result['message']}")
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")


def start_scheduler():
    """启动定时同步调度器。

    每周三凌晨 5:00 (GMT+8) 执行。
    """
    # 每周三 5:00 Asia/Shanghai（GMT+8）
    trigger = CronTrigger(day_of_week="wed", hour=5, minute=0, timezone="Asia/Shanghai")

    scheduler.add_job(
        _sync_job,
        trigger=trigger,
        id="weekly_sync",
        name="Weekly Bangumi Archive Sync",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info("Sync scheduler started (weekly on Wednesday 05:00 GMT+8)")


def shutdown_scheduler():
    """停止调度器。"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Sync scheduler stopped")
