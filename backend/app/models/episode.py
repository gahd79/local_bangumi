"""Episode 章节/剧集模型。"""

import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Episode(Base):
    """章节/剧集表。

    type 映射：0=正篇, 1=特别篇, 2=OP, 3=ED, 4=Trailer, 5=MAD, 6=其他
    """

    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bangumi_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )

    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.bangumi_id"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    name_cn: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    airdate: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    disc: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[Optional[str]] = mapped_column(String(20))
    sort: Mapped[float] = mapped_column(default=0.0)
    type: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    subject: Mapped["Subject"] = relationship(back_populates="episodes")

    def __repr__(self) -> str:
        return f"<Episode(id={self.id}, name={self.name}, sort={self.sort})>"
