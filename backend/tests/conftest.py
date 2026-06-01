"""Pytest fixtures — 提供 TestClient + 测试数据库环境。"""

import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base
from app.main import app
from app.models import Subject, Episode, Person, Character


@pytest.fixture(scope="function")
def test_db():
    """使用临时文件 SQLite，所有连接共享同一数据。"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Monkeypatch SessionLocal → 所有请求使用测试数据库
    import app.database as db_module

    original = db_module.SessionLocal
    db_module.SessionLocal = TestSessionLocal

    yield TestSessionLocal

    db_module.SessionLocal = original
    engine.dispose()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def db_session(test_db):
    """单个测试函数的共享数据库会话。"""
    session = test_db()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(test_db, db_session):
    """提供 TestClient。"""
    with TestClient(app) as c:
        yield c


# ─── 测试数据（均使用共享 session，不 close） ───

@pytest.fixture
def sample_subject(db_session):
    """插入一个测试条目。"""
    subject = Subject(
        bangumi_id=1,
        type=2,
        name="Test Anime",
        name_cn="测试动画",
        summary="A test anime summary",
        score=8.5,
        rank=100,
        date="2024-01-01",
        tags=[{"name": "科幻", "count": 100}],
        meta_tags=["原创"],
        infobox_raw="Infobox test",
        infobox_parsed={"type": "动画", "fields": {"话数": "12"}},
        platform=1,
        nsfw=False,
        series=True,
        wish_count=10,
        doing_count=5,
        done_count=20,
        on_hold_count=3,
        dropped_count=1,
    )
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)
    return subject


@pytest.fixture
def sample_episode(db_session, sample_subject):
    """插入一集测试剧集。"""
    ep = Episode(
        bangumi_id=1001,
        subject_id=sample_subject.bangumi_id,
        name="第1话",
        name_cn="第一话",
        airdate="2024-01-01",
        sort=1.0,
        type=0,
        disc=1,
        duration="24m",
    )
    db_session.add(ep)
    db_session.commit()
    db_session.refresh(ep)
    return ep


@pytest.fixture
def sample_person(db_session):
    """插入一个测试人物。"""
    person = Person(
        bangumi_id=1,
        name="Test Director",
        type=1,
        career=["导演"],
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def sample_character(db_session):
    """插入一个测试角色。"""
    char = Character(
        bangumi_id=1,
        name="Test Character",
        role=1,
    )
    db_session.add(char)
    db_session.commit()
    db_session.refresh(char)
    return char
