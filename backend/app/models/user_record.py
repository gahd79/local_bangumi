"""UserRecord 用户观看/收藏记录模型。"""

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class UserRecord(Base):
    """用户观看记录表。

    status 映射：1=想看, 2=在看, 3=看过, 4=搁置, 5=抛弃
    user_id 默认为 1（预留多用户支持）
    """

    __tablename__ = "user_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )

    # ── 收藏状态 ──
    status: Mapped[int] = mapped_column(Integer, index=True, default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(String(2000))

    # ── 日期 ──
    start_date: Mapped[Optional[str]] = mapped_column(String(20))
    finish_date: Mapped[Optional[str]] = mapped_column(String(20))

    # ── 扩展字段（参考 bangumi collections API） ──
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    # 逐集进度追踪：{"1": "看过", "2": "看过", ...} 或 {"1": "抛弃", ...}
    ep_status: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    # ── 关系 ──
    subject: Mapped["Subject"] = relationship(foreign_keys=[subject_id])

    __table_args__ = (
        Index("ix_ur_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<UserRecord(id={self.id}, user={self.user_id}, subject={self.subject_id}, status={self.status})>"
