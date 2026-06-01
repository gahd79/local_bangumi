"""Subject 条目模型 — 统一存储所有类型（动画/漫画/游戏/小说等）。"""

import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Subject(Base):
    """统一条目表，通过 type 字段区分作品类型。

    type 映射：1=漫画, 2=动画, 3=音乐, 4=游戏, 6=三次元
    """

    __tablename__ = "subjects"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bangumi_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)

    # 基本信息
    type: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    name_cn: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(500))

    # Wiki 内容
    infobox_raw: Mapped[Optional[str]] = mapped_column(Text)
    infobox_parsed: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # 元数据
    platform: Mapped[Optional[int]] = mapped_column(Integer)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    nsfw: Mapped[bool] = mapped_column(Boolean, default=False)
    date: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    series: Mapped[bool] = mapped_column(Boolean, default=False)

    # 标签（JSON 格式）
    tags: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)
    meta_tags: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # 评分与排名
    score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    score_details: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON)
    rank: Mapped[Optional[int]] = mapped_column(Integer)

    # 收藏统计（从 favorite JSON 反规范化）
    wish_count: Mapped[int] = mapped_column(Integer, default=0)
    doing_count: Mapped[int] = mapped_column(Integer, default=0)
    done_count: Mapped[int] = mapped_column(Integer, default=0)
    on_hold_count: Mapped[int] = mapped_column(Integer, default=0)
    dropped_count: Mapped[int] = mapped_column(Integer, default=0)

    # 时间戳
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        index=True,
    )

    # 关联关系
    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="subject", lazy="dynamic"
    )
    subject_characters: Mapped[List["SubjectCharacter"]] = relationship(
        back_populates="subject"
    )
    subject_persons: Mapped[List["SubjectPerson"]] = relationship(
        back_populates="subject"
    )

    # 复合索引
    __table_args__ = (
        Index("ix_subjects_type_score", "type", "score"),
        Index("ix_subjects_type_date", "type", "date"),
    )

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name={self.name_cn or self.name})>"
