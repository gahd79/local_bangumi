"""Person 人物相关 Pydantic Schema。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PersonRead(BaseModel):
    """单个人物响应。"""

    id: int
    bangumi_id: int
    name: str
    type: int = 1
    career: Optional[List[str]] = None
    infobox_raw: Optional[str] = None
    infobox_parsed: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    comments_count: int = 0
    collects_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonList(BaseModel):
    """人物分页列表响应。"""

    items: List[PersonRead]
    total: int
    page: int
    limit: int


# 用于嵌套在 SubjectDetail 中的精简人物信息
class PersonBrief(BaseModel):
    """人物简要信息（嵌套在条目详情中）。"""

    bangumi_id: int
    name: str
    type: int
    position: Optional[int] = None
    appear_eps: Optional[str] = None

    model_config = {"from_attributes": True}


# 人物详情增强（含关联数据）
class PersonDetail(PersonRead):
    """人物详情，包含参与作品和配音角色。"""

    related_subjects: List["SubjectBriefForPerson"] = []
    related_characters: List["CharacterBriefForPerson"] = []


class SubjectBriefForPerson(BaseModel):
    """人物参与的作品简要信息。"""

    bangumi_id: int
    name: str
    name_cn: Optional[str] = None
    type: int
    position: Optional[int] = None

    model_config = {"from_attributes": True}


class CharacterBriefForPerson(BaseModel):
    """人物配音的角色简要信息。"""

    bangumi_id: int
    name: str
    subject_bangumi_id: int
    subject_name: str = ""

    model_config = {"from_attributes": True}
