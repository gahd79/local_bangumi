"""Subject 条目相关 API 路由。"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import (
    Episode,
    Person,
    PersonCharacter,
    Subject,
    SubjectCharacter,
    SubjectPerson,
    SubjectRelation,
)
from ..schemas.character import CVPersonBrief
from ..schemas.subject import (
    CharacterInSubject,
    EpisodeBrief,
    PersonInSubject,
    RelationBrief,
    SubjectDetail,
    SubjectList,
    SubjectRead,
)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

# 季度映射：1=冬(1-3月), 2=春(4-6月), 3=夏(7-9月), 4=秋(10-12月)
SEASON_MONTHS = {1: ("-01-", "-03-"), 2: ("-04-", "-06-"), 3: ("-07-", "-09-"), 4: ("-10-", "-12-")}


@router.get("", response_model=SubjectList)
def list_subjects(
    type: Optional[int] = Query(
        None, description="条目类型：1=漫画, 2=动画, 3=音乐, 4=游戏, 6=三次元"
    ),
    search: Optional[str] = Query(
        None, description="关键词搜索（匹配 name/name_cn/name_en）"
    ),
    tag: Optional[str] = Query(
        None, description="按标签筛选（匹配 tags JSON 中的标签名）"
    ),
    year: Optional[int] = Query(
        None, description="发行年份（如 2024）"
    ),
    season: Optional[int] = Query(
        None, ge=1, le=4, description="季度：1=冬(1-3月), 2=春(4-6月), 3=夏(7-9月), 4=秋(10-12月)"
    ),
    score_from: Optional[float] = Query(
        None, ge=0, le=10, description="最低评分"
    ),
    score_to: Optional[float] = Query(
        None, ge=0, le=10, description="最高评分"
    ),
    popularity_from: Optional[int] = Query(
        None, ge=0, description="最低收藏人数"
    ),
    nsfw: Optional[bool] = Query(None, description="是否显示 NSFW 内容"),
    series: Optional[bool] = Query(None, description="是否为系列作品"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    sort: str = Query(
        "bangumi_id",
        pattern="^(bangumi_id|score|date|rank|name_cn|updated_at|popularity)$",
        description="排序字段（popularity=收藏人数）",
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="排序方向"),
    db: Session = Depends(get_db),
):
    """获取条目列表，支持年份/季度/热度筛选、分页、排序。"""
    query = db.query(Subject)

    # 类型筛选
    if type is not None:
        query = query.filter(Subject.type == type)

    # 关键词搜索
    if search:
        keyword = f"%{search}%"
        query = query.filter(
            Subject.name.like(keyword)
            | Subject.name_cn.like(keyword)
            | (Subject.name_en.isnot(None) & Subject.name_en.like(keyword))
        )

    # 标签筛选
    if tag:
        query = query.filter(Subject.tags.isnot(None)).filter(
            Subject.tags.cast(str).contains(f'"name": "{tag}"')
        )

    # 年份筛选
    if year is not None:
        year_str = str(year)
        if season is not None and 1 <= season <= 4:
            # 季度筛选
            start_month, end_month = SEASON_MONTHS[season]
            query = query.filter(
                Subject.date.like(f"{year_str}{start_month}%")
                | Subject.date.like(f"{year_str}{end_month}%")
            )
        else:
            # 仅年份
            query = query.filter(Subject.date.like(f"{year_str}-%"))

    # 评分范围
    if score_from is not None:
        query = query.filter(Subject.score >= score_from)
    if score_to is not None:
        query = query.filter(Subject.score <= score_to)

    # 热度筛选（收藏人数 = 想看+在看+看过+搁置+抛弃）
    if popularity_from is not None:
        query = query.filter(
            (Subject.wish_count + Subject.doing_count + Subject.done_count
             + Subject.on_hold_count + Subject.dropped_count) >= popularity_from
        )

    # NSFW 过滤
    if nsfw is not None:
        query = query.filter(Subject.nsfw == nsfw)

    # 系列筛选
    if series is not None:
        query = query.filter(Subject.series == series)

    # 排序
    if sort == "popularity":
        # 按收藏总数排序
        pop_col = (
            Subject.wish_count + Subject.doing_count + Subject.done_count
            + Subject.on_hold_count + Subject.dropped_count
        )
        if order == "desc":
            query = query.order_by(pop_col.desc())
        else:
            query = query.order_by(pop_col.asc())
    else:
        sort_column = getattr(Subject, sort)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # 总数
    total = query.count()

    # 分页
    items = query.offset((page - 1) * limit).limit(limit).all()

    return SubjectList(items=items, total=total, page=page, limit=limit)


@router.get("/{bangumi_id}", response_model=SubjectDetail)
def get_subject(bangumi_id: int, db: Session = Depends(get_db)):
    """根据 Bangumi ID 获取单个条目详情，包含剧集、角色、STAFF、关联条目。"""
    subject = db.query(Subject).filter(Subject.bangumi_id == bangumi_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="条目不存在")

    # ─── 1. 剧集列表（按 sort 排序，限制 200 条） ───
    episodes = (
        db.query(Episode)
        .filter(Episode.subject_id == bangumi_id)
        .order_by(Episode.sort.asc())
        .limit(200)
        .all()
    )
    episode_briefs = [
        EpisodeBrief(
            bangumi_id=ep.bangumi_id,
            name=ep.name,
            name_cn=ep.name_cn,
            airdate=ep.airdate,
            disc=ep.disc,
            duration=ep.duration,
            sort=ep.sort,
            type=ep.type,
        )
        for ep in episodes
    ]

    # ─── 2. 角色列表（含 CV） ───
    sc_entries = (
        db.query(SubjectCharacter)
        .options(
            selectinload(SubjectCharacter.character),
        )
        .filter(SubjectCharacter.subject_id == bangumi_id)
        .order_by(SubjectCharacter.order.asc())
        .limit(100)
        .all()
    )

    # 收集所有角色 ID，批量查询 CV
    character_ids = [sc.character_id for sc in sc_entries if sc.character]
    cv_map: dict[int, list[CVPersonBrief]] = {}
    if character_ids:
        pc_entries = (
            db.query(PersonCharacter)
            .options(
                selectinload(PersonCharacter.person),
            )
            .filter(
                PersonCharacter.character_id.in_(character_ids),
                PersonCharacter.subject_id == bangumi_id,
            )
            .all()
        )
        for pc in pc_entries:
            if pc.person:
                cv_brief = CVPersonBrief(
                    bangumi_id=pc.person.bangumi_id,
                    name=pc.person.name,
                    type=pc.person.type,
                )
                cv_map.setdefault(pc.character_id, []).append(cv_brief)

    character_infos = []
    for sc in sc_entries:
        if sc.character:
            character_infos.append(
                CharacterInSubject(
                    character_id=sc.character_id,
                    character_name=sc.character.name,
                    role=sc.character.role,
                    type=sc.type,
                    order=sc.order,
                    cv_persons=cv_map.get(sc.character_id, []),
                )
            )

    # ─── 3. STAFF 列表 ───
    sp_entries = (
        db.query(SubjectPerson)
        .options(selectinload(SubjectPerson.person))
        .filter(SubjectPerson.subject_id == bangumi_id)
        .all()
    )
    person_infos = []
    for sp in sp_entries:
        if sp.person:
            person_infos.append(
                PersonInSubject(
                    person_id=sp.person_id,
                    person_name=sp.person.name,
                    person_type=sp.person.type,
                    position=sp.position,
                    appear_eps=sp.appear_eps,
                )
            )

    # ─── 4. 关联条目 ───
    relations = (
        db.query(SubjectRelation)
        .filter(SubjectRelation.subject_id == bangumi_id)
        .all()
    )
    related_ids = [r.related_subject_id for r in relations]
    related_subjects_map = {}
    if related_ids:
        related_subs = (
            db.query(Subject)
            .filter(Subject.bangumi_id.in_(related_ids))
            .all()
        )
        related_subjects_map = {s.bangumi_id: s for s in related_subs}

    relation_briefs = []
    for r in relations:
        rel_sub = related_subjects_map.get(r.related_subject_id)
        relation_briefs.append(
            RelationBrief(
                relation_type=r.relation_type,
                related_subject_id=r.related_subject_id,
                related_subject_name=rel_sub.name if rel_sub else "",
                related_subject_name_cn=rel_sub.name_cn if rel_sub else None,
                related_subject_type=rel_sub.type if rel_sub else None,
                order=r.order,
            )
        )

    # ─── 组装 SubjectDetail ───
    return SubjectDetail(
        **SubjectRead.model_validate(subject).model_dump(),
        episodes=episode_briefs,
        characters=character_infos,
        persons=person_infos,
        relations=relation_briefs,
    )
