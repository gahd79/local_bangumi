"""PersonRelation 人物/角色间关联模型。"""

import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class PersonRelation(Base):
    """人物间/角色间关联表。

    person_type: "prsn"=现实人物, "crt"=虚拟角色
    """

    __tablename__ = "person_relations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    person_type: Mapped[str] = mapped_column(String(10), nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    related_person_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    relation_type: Mapped[int] = mapped_column(Integer, nullable=False)
    spoiler: Mapped[bool] = mapped_column(Boolean, default=False)
    ended: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<PersonRelation(type={self.person_type}, "
            f"person={self.person_id}, related={self.related_person_id})>"
        )
