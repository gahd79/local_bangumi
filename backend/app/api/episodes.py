"""Episode 剧集相关 API 路由。"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Episode, Subject
from ..schemas.episode import EpisodeList, EpisodeRead

router = APIRouter(prefix="/api/episodes", tags=["episodes"])


@router.get("", response_model=EpisodeList)
def list_episodes(
    subject_id: int = Query(..., description="条目 Bangumi ID（必填）"),
    type: Optional[int] = Query(
        None, description="剧集类型：0=正篇, 1=特别篇, 2=OP, 3=ED, 4=Trailer, 5=MAD, 6=其他"
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=500, description="每页数量"),
    db: Session = Depends(get_db),
):
    """获取指定条目的剧集列表，按 sort 排序。"""
    query = (
        db.query(Episode)
        .filter(Episode.subject_id == subject_id)
    )

    if type is not None:
        query = query.filter(Episode.type == type)

    query = query.order_by(Episode.sort.asc())

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return EpisodeList(items=items, total=total, page=page, limit=limit)


@router.get("/{bangumi_id}", response_model=EpisodeRead)
def get_episode(bangumi_id: int, db: Session = Depends(get_db)):
    """根据 Bangumi ID 获取单个剧集详情。"""
    episode = (
        db.query(Episode).filter(Episode.bangumi_id == bangumi_id).first()
    )
    if not episode:
        raise HTTPException(status_code=404, detail="剧集不存在")
    return episode
