"""PersonCharacter 人物-角色（CV）关联模型。"""

import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class PersonCharacter(Base):
    """人物-角色关联表，记录声优（CV）与角色的对应关系。"""

    __tablename__ = "person_characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("persons.bangumi_id"), index=True, nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.bangumi_id"), index=True, nullable=False
    )
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("characters.bangumi_id"), index=True, nullable=False
    )
    type: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[Optional[str]] = mapped_column(String(1000))

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    person: Mapped["Person"] = relationship(foreign_keys=[person_id])
    character: Mapped["Character"] = relationship(foreign_keys=[character_id])

    def __repr__(self) -> str:
        return (
            f"<PersonCharacter(person={self.person_id}, "
            f"subject={self.subject_id}, character={self.character_id})>"
        )
