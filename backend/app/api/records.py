"""UserRecord 用户记录相关 API 路由。"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Episode, Subject, UserRecord
from ..schemas.user_record import (
    UserRecordCreate,
    UserRecordRead,
    UserRecordStats,
    UserRecordUpdate,
)

router = APIRouter(prefix="/api/records", tags=["records"])

DEFAULT_USER_ID = 1  # 默认用户 ID，预留多用户支持

# Bangumi 收藏类型 → 本地 status 映射
# bgm: 1=想看, 2=看过, 3=在看, 4=搁置, 5=抛弃
# 本地: 1=想看, 2=在看, 3=看过, 4=搁置, 5=抛弃
BGM_STATUS_MAP = {1: 1, 2: 3, 3: 2, 4: 4, 5: 5}


def _format_ep_key(sort_val: float) -> str:
    """将剧集 sort 值格式化为统一的 key。

    Python str(1.0) → '1.0'，但 JS String(1.0) → '1'。
    统一使用：整数用 '1'，真正有小数的用 '3.5'。
    """
    if sort_val == int(sort_val):
        return str(int(sort_val))
    return str(sort_val)


def _normalize_ep_status_keys(ep_status: dict) -> dict:
    """将 ep_status 中所有 key 归一化（兼容旧 '1.0' 格式 → '1'）。"""
    if not ep_status:
        return {}
    result = {}
    for k, v in ep_status.items():
        try:
            sort_val = float(k)
            result[_format_ep_key(sort_val)] = v
        except (ValueError, TypeError):
            result[k] = v
    return result


def _get_episode_counts(db: Session, subject_ids: list[int]) -> dict[int, int]:
    """批量获取条目剧集数。"""
    if not subject_ids:
        return {}
    rows = (
        db.query(Episode.subject_id, func.count(Episode.id))
        .filter(Episode.subject_id.in_(subject_ids))
        .group_by(Episode.subject_id)
        .all()
    )
    return {s_id: cnt for s_id, cnt in rows}


def _sync_ep_status_from_progress(db: Session, subject_id: int, progress: int, existing_ep_status: dict) -> dict:
    """根据进度值自动生成逐集状态。

    规则：
    - 查询条目的所有剧集，获取 sort 值列表
    - sort <= progress 的剧集标记为「看过」
    - sort > progress 的剧集保留原有 ep_status（如有）
    - 不存在的剧集号不生成条目
    """
    if progress <= 0:
        return existing_ep_status or {}

    episodes = (
        db.query(Episode.sort)
        .filter(Episode.subject_id == subject_id)
        .order_by(Episode.sort.asc())
        .all()
    )

    # 先归一化旧 key（兼容 '1.0' → '1'）
    normalized_existing = _normalize_ep_status_keys(existing_ep_status or {})

    new_ep_status = {}
    for (sort_val,) in episodes:
        key = _format_ep_key(sort_val)
        if sort_val <= progress:
            new_ep_status[key] = "看过"
        elif key in normalized_existing and normalized_existing[key] != "看过":
            # 仅保留非「看过」的手动状态（如 抛弃），清除被进度覆盖的旧「看过」
            new_ep_status[key] = normalized_existing[key]

    return new_ep_status


def _enrich_record(record: UserRecord, episode_count: int = 0) -> dict:
    """将 UserRecord 转为包含条目名称的字典。"""
    return {
        "id": record.id,
        "user_id": record.user_id,
        "subject_id": record.subject_id,
        "subject_name_cn": record.subject.name_cn if record.subject else None,
        "subject_name": record.subject.name if record.subject else None,
        "subject_type": record.subject.type if record.subject else None,
        "status": record.status,
        "progress": record.progress,
        "rating": record.rating,
        "comment": record.comment,
        "tags": record.tags or [],
        "private": record.private or False,
        "ep_status": _normalize_ep_status_keys(record.ep_status or {}),
        "episode_count": episode_count,
        "start_date": record.start_date,
        "finish_date": record.finish_date,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@router.get("", response_model=List[UserRecordRead])
def list_records(
    status: Optional[int] = Query(
        None, description="过滤状态：1=想看, 2=在看, 3=看过, 4=搁置, 5=抛弃"
    ),
    subject_id: Optional[int] = Query(
        None, description="按条目 ID（bangumi_id）过滤"
    ),
    user_id: int = Query(DEFAULT_USER_ID, description="用户 ID"),
    db: Session = Depends(get_db),
):
    """获取当前用户的观看记录列表（含条目名称）。"""
    query = (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id)
    )
    if status is not None:
        query = query.filter(UserRecord.status == status)
    if subject_id is not None:
        query = query.filter(UserRecord.subject_id == subject_id)
    records = query.order_by(UserRecord.updated_at.desc()).all()

    # 批量获取剧集数
    subject_ids = list(set(r.subject_id for r in records))
    ep_counts = _get_episode_counts(db, subject_ids)

    return [_enrich_record(r, ep_counts.get(r.subject_id, 0)) for r in records]


@router.post("", response_model=UserRecordRead, status_code=201)
def create_record(
    record: UserRecordCreate,
    user_id: int = Query(DEFAULT_USER_ID, description="用户 ID"),
    db: Session = Depends(get_db),
):
    """添加一条新的观看记录。"""
    create_data = record.model_dump()
    if create_data.get("tags") is None:
        create_data["tags"] = []
    # 双向同步：如果设置了 progress 但未显式传入 ep_status，自动生成
    if create_data.get("progress", 0) > 0 and create_data.get("ep_status") is None:
        create_data["ep_status"] = _sync_ep_status_from_progress(
            db, create_data["subject_id"], create_data["progress"], {}
        )
    if create_data.get("ep_status") is None:
        create_data["ep_status"] = {}
    else:
        create_data["ep_status"] = _normalize_ep_status_keys(create_data["ep_status"])
    db_record = UserRecord(user_id=user_id, **create_data)
    db.add(db_record)
    db.commit()
    # 重新查询以加载 relationship (subject)
    db.refresh(db_record)
    db_record = db.query(UserRecord).filter(UserRecord.id == db_record.id).first()
    ep_counts = _get_episode_counts(db, [db_record.subject_id])
    return _enrich_record(db_record, ep_counts.get(db_record.subject_id, 0))


@router.put("/{record_id}", response_model=UserRecordRead)
def update_record(
    record_id: int,
    record: UserRecordUpdate,
    db: Session = Depends(get_db),
):
    """更新一条观看记录。"""
    db_record = db.query(UserRecord).filter(UserRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = record.model_dump(exclude_unset=True)

    # 双向同步：如果 progress 被设为 >0 但未显式传入 ep_status，自动生成逐集状态
    if update_data.get("progress", 0) > 0 and "ep_status" not in update_data:
        update_data["ep_status"] = _sync_ep_status_from_progress(
            db, db_record.subject_id, update_data["progress"], db_record.ep_status or {}
        )
    elif "progress" in update_data and update_data["progress"] == 0 and "ep_status" not in update_data:
        # progress 明确归零时清空逐集状态
        update_data["ep_status"] = {}
    elif "ep_status" in update_data and update_data["ep_status"] is not None:
        update_data["ep_status"] = _normalize_ep_status_keys(update_data["ep_status"])

    for key, value in update_data.items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)
    db_record = db.query(UserRecord).filter(UserRecord.id == record_id).first()
    ep_counts = _get_episode_counts(db, [db_record.subject_id])
    return _enrich_record(db_record, ep_counts.get(db_record.subject_id, 0))


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """删除一条观看记录。"""
    db_record = db.query(UserRecord).filter(UserRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()


@router.get("/stats", response_model=UserRecordStats)
def get_stats(
    user_id: int = Query(DEFAULT_USER_ID, description="用户 ID"),
    db: Session = Depends(get_db),
):
    """获取用户观看记录统计概览。"""
    records = (
        db.query(UserRecord).filter(UserRecord.user_id == user_id).all()
    )

    total = len(records)

    # 状态分布
    status_names = {1: "想看", 2: "在看", 3: "看过", 4: "搁置", 5: "抛弃"}
    status_dist: dict[str, int] = {}
    for r in records:
        key = status_names.get(r.status, f"未知({r.status})")
        status_dist[key] = status_dist.get(key, 0) + 1

    # 评分分布
    rating_dist: dict[str, int] = {}
    for r in records:
        if r.rating is not None:
            key = str(r.rating)
            rating_dist[key] = rating_dist.get(key, 0) + 1
    for i in range(1, 11):
        rating_dist.setdefault(str(i), 0)

    # 按条目类型分布
    subject_ids = [r.subject_id for r in records]
    type_dist: dict[str, int] = {}
    type_names = {1: "漫画", 2: "动画", 3: "音乐", 4: "游戏", 6: "三次元"}
    if subject_ids:
        type_counts = (
            db.query(Subject.type, func.count(Subject.id))
            .filter(Subject.bangumi_id.in_(subject_ids))
            .group_by(Subject.type)
            .all()
        )
        for stype, cnt in type_counts:
            key = type_names.get(stype, f"类型{stype}")
            type_dist[key] = cnt

    # 最近记录（前5条，含名称和剧集数）
    recent = (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id)
        .order_by(UserRecord.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_ids = list(set(r.subject_id for r in recent))
    recent_ep_counts = _get_episode_counts(db, recent_ids)

    return UserRecordStats(
        total_records=total,
        status_distribution=status_dist,
        rating_distribution=rating_dist,
        type_distribution=type_dist,
        recent_records=[_enrich_record(r, recent_ep_counts.get(r.subject_id, 0)) for r in recent],
    )


# ─── 在看追番端点（首页点格子用） ───

@router.get("/watching")
def get_watching(
    user_id: int = Query(DEFAULT_USER_ID, description="用户 ID"),
    db: Session = Depends(get_db),
):
    """获取用户正在观看的条目（含剧集列表），供首页点格子用。"""
    records = (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id, UserRecord.status == 2)  # 在看
        .order_by(UserRecord.updated_at.desc())
        .all()
    )

    if not records:
        return []

    subject_ids = list(set(r.subject_id for r in records))
    ep_counts = _get_episode_counts(db, subject_ids)

    # 批量获取 subject 和 episode
    subjects_map = {
        s.bangumi_id: s
        for s in db.query(Subject).filter(Subject.bangumi_id.in_(subject_ids)).all()
    }

    # 批量获取所有相关条目的剧集
    all_episodes = (
        db.query(Episode)
        .filter(Episode.subject_id.in_(subject_ids))
        .order_by(Episode.sort.asc())
        .all()
    )
    episodes_by_subject: dict[int, list] = {}
    for ep in all_episodes:
        episodes_by_subject.setdefault(ep.subject_id, []).append(ep)

    result = []
    for r in records:
        sub = subjects_map.get(r.subject_id)
        eps = episodes_by_subject.get(r.subject_id, [])
        ep_list = [
            {
                "bangumi_id": ep.bangumi_id,
                "name": ep.name,
                "name_cn": ep.name_cn,
                "airdate": ep.airdate,
                "disc": ep.disc,
                "duration": ep.duration,
                "sort": ep.sort,
                "type": ep.type,
            }
            for ep in eps[:200]  # 限制 200 集
        ]
        result.append({
            "record": _enrich_record(r, ep_counts.get(r.subject_id, 0)),
            "subject": {
                "bangumi_id": sub.bangumi_id if sub else r.subject_id,
                "name": sub.name if sub else "",
                "name_cn": sub.name_cn if sub else None,
                "type": sub.type if sub else None,
                "score": sub.score if sub else None,
                "date": sub.date if sub else None,
            },
            "episodes": ep_list,
            "episode_count": len(ep_list),
        })

    return result


# ─── Bangumi 记录导入 ───

@router.post("/import")
def import_records(
    data: List[dict],
    user_id: int = Query(DEFAULT_USER_ID, description="用户 ID"),
    db: Session = Depends(get_db),
):
    """从 Bangumi 导出的 collections JSON 导入记录。

    期望格式参考 bgm_collections.json：
    - type: bgm 收藏类型（1=想看, 2=看过, 3=在看, 4=搁置, 5=抛弃）
    - rate: 评分 1-10（0 表示无评分）
    - ep_status: 已看集数（数字）
    - comment, tags, private, updated_at
    - subject.id: 条目 bangumi ID
    """
    created = 0
    updated = 0
    skipped = 0
    errors = []

    for idx, item in enumerate(data):
        try:
            bgm_type = item.get("type")
            if bgm_type not in BGM_STATUS_MAP:
                skipped += 1
                continue

            subject_id = item.get("subject_id") or (item.get("subject") or {}).get("id")
            if not subject_id:
                skipped += 1
                continue

            # 检查条目是否存在
            sub = db.query(Subject).filter(Subject.bangumi_id == subject_id).first()
            if not sub:
                skipped += 1
                continue

            # 映射字段
            local_status = BGM_STATUS_MAP[bgm_type]
            rate = item.get("rate", 0)
            rating = rate if rate and rate > 0 else None
            progress = item.get("ep_status", 0) if isinstance(item.get("ep_status"), int) else 0
            comment = item.get("comment")
            tags = item.get("tags", [])
            private = item.get("private", False)
            updated_at_str = item.get("updated_at")

            # 检查是否已有记录（同一用户+条目）
            existing = (
                db.query(UserRecord)
                .filter(
                    UserRecord.user_id == user_id,
                    UserRecord.subject_id == subject_id,
                )
                .first()
            )

            if existing:
                # 更新已有记录
                existing.status = local_status
                if rating is not None:
                    existing.rating = rating
                if progress:
                    existing.progress = progress
                    # 双向同步：导入时 progress > 0 则自动生成 ep_status
                    existing.ep_status = _sync_ep_status_from_progress(
                        db, subject_id, progress, existing.ep_status or {}
                    )
                if comment:
                    existing.comment = comment
                if tags:
                    existing.tags = tags
                existing.private = private
                updated += 1
            else:
                ep_status_synced = None
                if progress > 0:
                    ep_status_synced = _sync_ep_status_from_progress(
                        db, subject_id, progress, {}
                    )
                new_record = UserRecord(
                    user_id=user_id,
                    subject_id=subject_id,
                    status=local_status,
                    progress=progress,
                    rating=rating,
                    comment=comment,
                    tags=tags,
                    private=private,
                    ep_status=ep_status_synced or {},
                )
                db.add(new_record)
                created += 1

        except Exception as exc:
            errors.append({"index": idx, "error": str(exc)})
            skipped += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:10],  # 最多返回前 10 个错误
        "total": len(data),
    }
