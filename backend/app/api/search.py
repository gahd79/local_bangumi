"""全局搜索 API 路由。"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Character, Person, Subject

logger = logging.getLogger("app.search")
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    scope: str = Query(
        "subjects",
        pattern="^(subjects|persons|characters|all)$",
        description="搜索范围",
    ),
    type: Optional[int] = Query(
        None, description="条目类型筛选（仅 scope=subjects 时有效）"
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """全局搜索条目/人物/角色。

    搜索策略：
    - 精确匹配（name == keyword）优先级最高
    - 前缀匹配（name LIKE 'keyword%'）其次
    - 包含匹配（name LIKE '%keyword%'）最低
    - 使用 CASE WHEN 表达式实现排序
    - SQLite LIKE 默认不区分 ASCII 大小写
    """
    # 转义 LIKE 通配符
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    exact = escaped
    prefix = f"{escaped}%"
    contain = f"%{escaped}%"

    results: dict[str, list] = {}
    subj_total = 0
    pers_total = 0
    char_total = 0

    # ─── 条目搜索 ───
    if scope in ("subjects", "all"):
        from sqlalchemy import case

        subj_query = db.query(Subject)
        if type is not None and scope == "subjects":
            subj_query = subj_query.filter(Subject.type == type)

        subj_query = subj_query.filter(
            Subject.name.like(contain, escape="\\")
            | (Subject.name_cn.isnot(None) & Subject.name_cn.like(contain, escape="\\"))
            | (Subject.name_en.isnot(None) & Subject.name_en.like(contain, escape="\\"))
        )

        # 按匹配质量排序：name 精确 > name_cn 精确 > 前缀 > 包含
        rank_expr = (
            case(
                (Subject.name == exact, 10),
                (Subject.name_cn == exact, 9),
                (Subject.name.like(prefix, escape="\\"), 5),
                (Subject.name_cn.like(prefix, escape="\\"), 4),
                else_=1,
            )
            + case(
                (Subject.score.isnot(None), Subject.score / 10),
                else_=0,
            )
        )

        subj_total = subj_query.count()
        subj_items = (
            subj_query.order_by(rank_expr.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        results["subjects"] = [
            {
                "bangumi_id": s.bangumi_id,
                "name": s.name,
                "name_cn": s.name_cn,
                "type": s.type,
                "score": s.score,
                "rank": s.rank,
                "date": s.date,
            }
            for s in subj_items
        ]
        logger.debug("搜索条目 q=%r → %d 条结果 (共 %d)", q, len(subj_items), subj_total)

    # ─── 人物搜索 ───
    if scope in ("persons", "all"):
        pers_query = db.query(Person).filter(
            Person.name.like(contain, escape="\\")
        )
        pers_total = pers_query.count()
        pers_items = (
            pers_query.order_by(Person.name.asc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        results["persons"] = [
            {
                "bangumi_id": p.bangumi_id,
                "name": p.name,
                "type": p.type,
            }
            for p in pers_items
        ]

    # ─── 角色搜索 ───
    if scope in ("characters", "all"):
        char_query = db.query(Character).filter(
            Character.name.like(contain, escape="\\")
        )
        char_total = char_query.count()
        char_items = (
            char_query.order_by(Character.name.asc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        results["characters"] = [
            {
                "bangumi_id": c.bangumi_id,
                "name": c.name,
                "role": c.role,
            }
            for c in char_items
        ]

    # 组装 totals
    totals = {}
    if scope == "subjects" or (scope == "all" and "subjects" in results):
        totals["subjects"] = subj_total
    if scope == "persons" or (scope == "all" and "persons" in results):
        totals["persons"] = pers_total
    if scope == "characters" or (scope == "all" and "characters" in results):
        totals["characters"] = char_total

    # 确保 scope='all' 时所有 key 都存在
    if scope == "all":
        totals.setdefault("subjects", subj_total if "subjects" in results else 0)
        totals.setdefault("persons", pers_total if "persons" in results else 0)
        totals.setdefault("characters", char_total if "characters" in results else 0)
        results.setdefault("subjects", [])
        results.setdefault("persons", [])
        results.setdefault("characters", [])

    return {
        "query": q,
        "scope": scope,
        "page": page,
        "limit": limit,
        "results": results,
        "totals": totals,
    }
