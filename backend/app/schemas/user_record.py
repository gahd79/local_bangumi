"""UserRecord 相关的 Pydantic Schema。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserRecordCreate(BaseModel):
    """创建观看记录的请求体。"""

    subject_id: int
    status: int = Field(ge=1, le=5, description="1=想看, 2=在看, 3=看过, 4=搁置, 5=抛弃")
    progress: int = Field(default=0, ge=0, description="当前进度（集数/章节）")
    rating: Optional[int] = Field(default=None, ge=1, le=10, description="个人评分 1-10")
    comment: Optional[str] = Field(default=None, max_length=2000)
    tags: Optional[List[str]] = Field(default=None, description="用户标签列表")
    private: bool = Field(default=False, description="是否私有")
    ep_status: Optional[Dict[str, Any]] = Field(default=None, description="逐集状态")
    start_date: Optional[str] = None
    finish_date: Optional[str] = None


class UserRecordUpdate(BaseModel):
    """更新观看记录的请求体 — 所有字段可选。"""

    status: Optional[int] = Field(default=None, ge=1, le=5)
    progress: Optional[int] = Field(default=None, ge=0)
    rating: Optional[int] = Field(default=None, ge=1, le=10)
    comment: Optional[str] = Field(default=None, max_length=2000)
    tags: Optional[List[str]] = None
    private: Optional[bool] = None
    ep_status: Optional[Dict[str, Any]] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None


class UserRecordRead(BaseModel):
    """观看记录响应 — 包含关联条目名称。"""

    id: int
    user_id: int
    subject_id: int
    subject_name_cn: Optional[str] = None
    subject_name: Optional[str] = None
    subject_type: Optional[int] = None
    status: int
    progress: int
    rating: Optional[int] = None
    comment: Optional[str] = None
    tags: Optional[List[str]] = None
    private: bool = False
    ep_status: Optional[Dict[str, Any]] = None
    episode_count: int = 0
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserRecordStats(BaseModel):
    """用户观看记录统计概览。"""

    total_records: int
    status_distribution: Dict[str, int]  # {"想看": N, "在看": N, ...}
    rating_distribution: Dict[str, int]  # {"1": N, "2": N, ..., "10": N}
    type_distribution: Dict[str, int]  # {"动画": N, "漫画": N, ...}
    recent_records: List[UserRecordRead] = []
