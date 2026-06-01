"""Pydantic Schema 包。"""

from .character import CharacterDetail, CharacterList, CharacterRead
from .episode import EpisodeList, EpisodeRead
from .person import PersonDetail, PersonList, PersonRead
from .subject import (
    CharacterInSubject,
    EpisodeBrief,
    PersonInSubject,
    RelationBrief,
    SubjectDetail,
    SubjectList,
    SubjectRead,
)
from .user_record import (
    UserRecordCreate,
    UserRecordRead,
    UserRecordStats,
    UserRecordUpdate,
)

__all__ = [
    # Subject
    "SubjectRead",
    "SubjectDetail",
    "SubjectList",
    "EpisodeBrief",
    "CharacterInSubject",
    "PersonInSubject",
    "RelationBrief",
    # Episode
    "EpisodeRead",
    "EpisodeList",
    # Person
    "PersonRead",
    "PersonList",
    "PersonDetail",
    # Character
    "CharacterRead",
    "CharacterList",
    "CharacterDetail",
    # UserRecord
    "UserRecordCreate",
    "UserRecordRead",
    "UserRecordUpdate",
    "UserRecordStats",
]
