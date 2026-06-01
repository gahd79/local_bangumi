"""Subject 相关的 Pydantic Schema。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ─── 嵌套 Schema（用于 SubjectDetail） ───

class EpisodeBrief(BaseModel):
    """剧集简要信息。"""

    bangumi_id: int
    name: str
    name_cn: Optional[str] = None
    airdate: Optional[str] = None
    disc: int = 0
    duration: Optional[str] = None
    sort: float = 0.0
    type: int = 0

    model_config = {"from_attributes": True}


class CharacterInSubject(BaseModel):
    """条目中的角色信息（含 CV）。"""

    character_id: int  # bangumi_id
    character_name: str
    role: int = 1
    type: int = 1  # 主角/配角/客串
    order: int = 0
    cv_persons: List["CVPersonBrief"] = []


class PersonInSubject(BaseModel):
    """条目中的 STAFF 信息。"""

    person_id: int  # bangumi_id
    person_name: str
    person_type: int = 1  # 个人/公司/组合
    position: Optional[int] = None
    appear_eps: Optional[str] = None


class RelationBrief(BaseModel):
    """条目关联简要信息。"""

    relation_type: int
    related_subject_id: int  # bangumi_id
    related_subject_name: str = ""
    related_subject_name_cn: Optional[str] = None
    related_subject_type: Optional[int] = None
    order: int = 0


# ─── 顶层 Schema ───

class SubjectRead(BaseModel):
    """单个条目响应（列表和基础详情共用）。"""

    id: int
    bangumi_id: int
    type: int
    name: str
    name_cn: Optional[str] = None
    name_en: Optional[str] = None
    platform: Optional[int] = None
    summary: Optional[str] = None
    nsfw: bool = False
    date: Optional[str] = None
    series: bool = False
    tags: Optional[List[Dict[str, Any]]] = None
    meta_tags: Optional[List[str]] = None
    score: Optional[float] = None
    score_details: Optional[Dict[str, int]] = None
    rank: Optional[int] = None
    wish_count: int = 0
    doing_count: int = 0
    done_count: int = 0
    on_hold_count: int = 0
    dropped_count: int = 0
    infobox_raw: Optional[str] = None
    infobox_parsed: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubjectDetail(SubjectRead):
    """条目详情（含关联数据）。"""

    episodes: List[EpisodeBrief] = []
    characters: List[CharacterInSubject] = []
    persons: List[PersonInSubject] = []
    relations: List[RelationBrief] = []


class SubjectList(BaseModel):
    """条目分页列表响应。"""

    items: List[SubjectRead]
    total: int
    page: int
    limit: int


# 导入放文件末尾避免循环引用
from ..schemas.character import CVPersonBrief  # noqa: E402
