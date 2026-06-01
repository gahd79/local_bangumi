"""Character 角色相关 API 路由。"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Character, PersonCharacter, Subject, SubjectCharacter
from ..schemas.character import (
    CVPersonBrief,
    CharacterDetail,
    CharacterList,
    CharacterRead,
    SubjectBriefForCharacter,
)

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("", response_model=CharacterList)
def list_characters(
    role: Optional[int] = Query(
        None, description="角色类型：1=角色, 2=机体, 3=组织"
    ),
    search: Optional[str] = Query(None, description="关键词搜索 name"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    sort: str = Query(
        "bangumi_id",
        pattern="^(bangumi_id|name|comments_count|collects_count)$",
        description="排序字段",
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="排序方向"),
    db: Session = Depends(get_db),
):
    """获取角色列表，支持类型筛选、搜索、分页、排序。"""
    query = db.query(Character)

    if role is not None:
        query = query.filter(Character.role == role)

    if search:
        keyword = f"%{search}%"
        query = query.filter(Character.name.like(keyword))

    sort_column = getattr(Character, sort)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return CharacterList(items=items, total=total, page=page, limit=limit)


@router.get("/{bangumi_id}", response_model=CharacterDetail)
def get_character(bangumi_id: int, db: Session = Depends(get_db)):
    """根据 Bangumi ID 获取角色详情，包含出场作品和 CV。"""
    character = (
        db.query(Character).filter(Character.bangumi_id == bangumi_id).first()
    )
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 出场作品
    sc_entries = (
        db.query(SubjectCharacter)
        .options(selectinload(SubjectCharacter.subject))
        .filter(SubjectCharacter.character_id == bangumi_id)
        .limit(200)
        .all()
    )
    related_subjects = []
    for sc in sc_entries:
        if sc.subject:
            related_subjects.append(
                SubjectBriefForCharacter(
                    bangumi_id=sc.subject.bangumi_id,
                    name=sc.subject.name,
                    name_cn=sc.subject.name_cn,
                    type=sc.subject.type,
                )
            )

    # CV 声优
    pc_entries = (
        db.query(PersonCharacter)
        .options(selectinload(PersonCharacter.person))
        .filter(PersonCharacter.character_id == bangumi_id)
        .all()
    )
    cv_persons = []
    for pc in pc_entries:
        if pc.person:
            cv_persons.append(
                CVPersonBrief(
                    bangumi_id=pc.person.bangumi_id,
                    name=pc.person.name,
                    type=pc.person.type,
                )
            )

    return CharacterDetail(
        **CharacterRead.model_validate(character).model_dump(),
        related_subjects=related_subjects,
        cv_persons=cv_persons,
    )
