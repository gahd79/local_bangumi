"""Character 角色模型。"""

import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Character(Base):
    """角色表。

    role 映射：1=角色, 2=机体, 3=组织, …
    """

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bangumi_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[int] = mapped_column(Integer, default=1)

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
        return f"<Character(id={self.id}, name={self.name})>"
