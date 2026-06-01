"""Episode 剧集相关 Pydantic Schema。"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class EpisodeRead(BaseModel):
    """单个剧集响应。"""

    id: int
    bangumi_id: int
    subject_id: int
    name: str
    name_cn: Optional[str] = None
    description: Optional[str] = None
    airdate: Optional[str] = None
    disc: int = 0
    duration: Optional[str] = None
    sort: float = 0.0
    type: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EpisodeList(BaseModel):
    """剧集分页列表响应。"""

    items: List[EpisodeRead]
    total: int
    page: int
    limit: int
