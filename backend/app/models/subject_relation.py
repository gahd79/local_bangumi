"""SubjectRelation 条目间关联模型。"""

import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SubjectRelation(Base):
    """条目间关联表（续作、前传、外传、同系列等）。"""

    __tablename__ = "subject_relations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )
    relation_type: Mapped[int] = mapped_column(Integer, nullable=False)
    related_subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    __table_args__ = (
        Index("ix_sr_subject_related", "subject_id", "related_subject_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<SubjectRelation(subject={self.subject_id}, "
            f"type={self.relation_type}, related={self.related_subject_id})>"
        )
