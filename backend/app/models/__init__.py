"""数据模型包 — 导入所有模型以便 Alembic 自动检测。"""

from .subject import Subject
from .episode import Episode
from .person import Person
from .character import Character
from .subject_relation import SubjectRelation
from .subject_character import SubjectCharacter
from .subject_person import SubjectPerson
from .person_character import PersonCharacter
from .person_relation import PersonRelation
from .user_record import UserRecord

__all__ = [
    "Subject",
    "Episode",
    "Person",
    "Character",
    "SubjectRelation",
    "SubjectCharacter",
    "SubjectPerson",
    "PersonCharacter",
    "PersonRelation",
    "UserRecord",
]
