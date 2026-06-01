"""Person 人物相关 API 路由。"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Person, PersonCharacter, Subject, SubjectPerson
from ..schemas.person import (
    CharacterBriefForPerson,
    PersonDetail,
    PersonList,
    PersonRead,
    SubjectBriefForPerson,
)

router = APIRouter(prefix="/api/persons", tags=["persons"])


@router.get("", response_model=PersonList)
def list_persons(
    type: Optional[int] = Query(
        None, description="人物类型：1=个人, 2=公司, 3=组合"
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
    """获取人物列表，支持类型筛选、搜索、分页、排序。"""
    query = db.query(Person)

    if type is not None:
        query = query.filter(Person.type == type)

    if search:
        keyword = f"%{search}%"
        query = query.filter(Person.name.like(keyword))

    sort_column = getattr(Person, sort)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return PersonList(items=items, total=total, page=page, limit=limit)


@router.get("/{bangumi_id}", response_model=PersonDetail)
def get_person(bangumi_id: int, db: Session = Depends(get_db)):
    """根据 Bangumi ID 获取人物详情，包含参与作品和配音角色。"""
    person = db.query(Person).filter(Person.bangumi_id == bangumi_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人物不存在")

    # 参与作品
    sp_entries = (
        db.query(SubjectPerson)
        .options(selectinload(SubjectPerson.subject))
        .filter(SubjectPerson.person_id == bangumi_id)
        .all()
    )
    related_subjects = []
    for sp in sp_entries:
        if sp.subject:
            related_subjects.append(
                SubjectBriefForPerson(
                    bangumi_id=sp.subject.bangumi_id,
                    name=sp.subject.name,
                    name_cn=sp.subject.name_cn,
                    type=sp.subject.type,
                    position=sp.position,
                )
            )

    # 配音角色
    pc_entries = (
        db.query(PersonCharacter)
        .options(selectinload(PersonCharacter.character))
        .filter(PersonCharacter.person_id == bangumi_id)
        .limit(200)
        .all()
    )
    # 批量获取 subject 名称
    subject_ids = list({pc.subject_id for pc in pc_entries})
    subject_map = {}
    if subject_ids:
        subjects = (
            db.query(Subject)
            .filter(Subject.bangumi_id.in_(subject_ids))
            .all()
        )
        subject_map = {s.bangumi_id: s for s in subjects}

    related_characters = []
    for pc in pc_entries:
        if pc.character:
            sub = subject_map.get(pc.subject_id)
            related_characters.append(
                CharacterBriefForPerson(
                    bangumi_id=pc.character.bangumi_id,
                    name=pc.character.name,
                    subject_bangumi_id=pc.subject_id,
                    subject_name=sub.name if sub else "",
                )
            )

    return PersonDetail(
        **PersonRead.model_validate(person).model_dump(),
        related_subjects=related_subjects,
        related_characters=related_characters,
    )
