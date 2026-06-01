"""数据库连接和会话管理模块。"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLite WAL 模式 + 外键约束启用
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ARG001
    """为 SQLite 连接启用 WAL 模式和外键约束。"""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类，所有模型继承自此。"""
    pass


def get_db():
    """FastAPI 依赖注入：为每个请求提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
