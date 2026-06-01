"""Character 角色相关 Pydantic Schema。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CharacterRead(BaseModel):
    """单个角色响应。"""

    id: int
    bangumi_id: int
    name: str
    role: int = 1
    infobox_raw: Optional[str] = None
    infobox_parsed: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    comments_count: int = 0
    collects_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterList(BaseModel):
    """角色分页列表响应。"""

    items: List[CharacterRead]
    total: int
    page: int
    limit: int


class CharacterDetail(CharacterRead):
    """角色详情，包含出场作品和CV。"""

    related_subjects: List["SubjectBriefForCharacter"] = []
    cv_persons: List["CVPersonBrief"] = []


class SubjectBriefForCharacter(BaseModel):
    """角色出场的作品简要信息。"""

    bangumi_id: int
    name: str
    name_cn: Optional[str] = None
    type: int

    model_config = {"from_attributes": True}


class CVPersonBrief(BaseModel):
    """声优简要信息（嵌套在角色详情/条目角色中）。"""

    bangumi_id: int
    name: str
    type: int

    model_config = {"from_attributes": True}
