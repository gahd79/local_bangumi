"""SubjectCharacter 条目-角色关联模型。"""

import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class SubjectCharacter(Base):
    """条目-角色关联表。

    type 映射：1=主角, 2=配角, 3=客串
    """

    __tablename__ = "subject_characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("characters.bangumi_id"), index=True, nullable=False
    )
    type: Mapped[int] = mapped_column(Integer, default=1)
    order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    subject: Mapped["Subject"] = relationship(back_populates="subject_characters")
    character: Mapped["Character"] = relationship(foreign_keys=[character_id])

    def __repr__(self) -> str:
        return (
            f"<SubjectCharacter(subject={self.subject_id}, "
            f"character={self.character_id}, type={self.type})>"
        )
