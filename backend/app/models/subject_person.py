"""SubjectPerson 条目-人物（STAFF）关联模型。"""

import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class SubjectPerson(Base):
    """条目-人物关联表，记录 STAFF 信息（导演、编剧、作画等）。"""

    __tablename__ = "subject_persons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )
    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("persons.bangumi_id"), index=True, nullable=False
    )
    position: Mapped[Optional[int]] = mapped_column(Integer)
    appear_eps: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    subject: Mapped["Subject"] = relationship(back_populates="subject_persons")
    person: Mapped["Person"] = relationship(foreign_keys=[person_id])

    def __repr__(self) -> str:
        return (
            f"<SubjectPerson(subject={self.subject_id}, "
            f"person={self.person_id}, position={self.position})>"
        )
