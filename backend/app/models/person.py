"""Person 人物/STAFF 模型。"""

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Person(Base):
    """人物表，包含 STAFF、声优等。

    type 映射：1=个人, 2=公司, 3=组合
    """

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bangumi_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[int] = mapped_column(Integer, default=1)
    career: Mapped[Optional[List[str]]] = mapped_column(JSON)

    infobox_raw: Mapped[Optional[str]] = mapped_column(Text)
    infobox_parsed: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    collects_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, name={self.name})>"
