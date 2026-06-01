"""Alembic 环境配置 — 连接应用模型和数据库 URL。"""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# 将 backend/ 目录添加到 Python 路径，以便导入 app 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import *  # noqa: E402, F401, F403 — 确保所有模型被导入

# Alembic Config 对象
config = context.config

# 从应用配置读取数据库 URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的 MetaData 对象，用于 autogenerate 支持
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以离线模式运行迁移（生成 SQL 脚本而非直接执行）。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以在线模式运行迁移（直接连接数据库执行）。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
