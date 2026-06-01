"""关联数据查询 API 路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import (
    Character,
    Person,
    PersonCharacter,
    Subject,
    SubjectCharacter,
    SubjectPerson,
    SubjectRelation,
)
from ..schemas.character import CVPersonBrief
from ..schemas.subject import CharacterInSubject, PersonInSubject, RelationBrief

router = APIRouter(prefix="/api", tags=["relations"])


@router.get("/subjects/{bangumi_id}/relations")
def get_subject_relations(bangumi_id: int, db: Session = Depends(get_db)):
    """获取指定条目的所有关联条目（续作/前传/外传等）。"""
    # 确认条目存在
    subject = db.query(Subject).filter(Subject.bangumi_id == bangumi_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="条目不存在")

    relations = (
        db.query(SubjectRelation)
        .filter(SubjectRelation.subject_id == bangumi_id)
        .all()
    )

    related_ids = [r.related_subject_id for r in relations]
    related_map = {}
    if related_ids:
        subs = (
            db.query(Subject)
            .filter(Subject.bangumi_id.in_(related_ids))
            .all()
        )
        related_map = {s.bangumi_id: s for s in subs}

    results = []
    for r in relations:
        rel_sub = related_map.get(r.related_subject_id)
        results.append(
            RelationBrief(
                relation_type=r.relation_type,
                related_subject_id=r.related_subject_id,
                related_subject_name=rel_sub.name if rel_sub else "",
                related_subject_name_cn=rel_sub.name_cn if rel_sub else None,
                related_subject_type=rel_sub.type if rel_sub else None,
                order=r.order,
            )
        )
    return {"subject_id": bangumi_id, "relations": results}


@router.get("/subjects/{bangumi_id}/characters")
def get_subject_characters(bangumi_id: int, db: Session = Depends(get_db)):
    """获取指定条目的所有角色（含 CV 信息）。"""
    subject = db.query(Subject).filter(Subject.bangumi_id == bangumi_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="条目不存在")

    sc_entries = (
        db.query(SubjectCharacter)
        .options(selectinload(SubjectCharacter.character))
        .filter(SubjectCharacter.subject_id == bangumi_id)
        .order_by(SubjectCharacter.order.asc())
        .all()
    )

    # 批量查询 CV
    character_ids = [sc.character_id for sc in sc_entries if sc.character]
    cv_map: dict[int, list[CVPersonBrief]] = {}
    if character_ids:
        pc_entries = (
            db.query(PersonCharacter)
            .options(selectinload(PersonCharacter.person))
            .filter(
                PersonCharacter.character_id.in_(character_ids),
                PersonCharacter.subject_id == bangumi_id,
            )
            .all()
        )
        for pc in pc_entries:
            if pc.person:
                cv_map.setdefault(pc.character_id, []).append(
                    CVPersonBrief(
                        bangumi_id=pc.person.bangumi_id,
                        name=pc.person.name,
                        type=pc.person.type,
                    )
                )

    results = []
    for sc in sc_entries:
        if sc.character:
            results.append(
                CharacterInSubject(
                    character_id=sc.character_id,
                    character_name=sc.character.name,
                    role=sc.character.role,
                    type=sc.type,
                    order=sc.order,
                    cv_persons=cv_map.get(sc.character_id, []),
                )
            )

    return {"subject_id": bangumi_id, "characters": results}


@router.get("/subjects/{bangumi_id}/persons")
def get_subject_persons(bangumi_id: int, db: Session = Depends(get_db)):
    """获取指定条目的所有 STAFF 信息。"""
    subject = db.query(Subject).filter(Subject.bangumi_id == bangumi_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="条目不存在")

    sp_entries = (
        db.query(SubjectPerson)
        .options(selectinload(SubjectPerson.person))
        .filter(SubjectPerson.subject_id == bangumi_id)
        .all()
    )

    results = []
    for sp in sp_entries:
        if sp.person:
            results.append(
                PersonInSubject(
                    person_id=sp.person_id,
                    person_name=sp.person.name,
                    person_type=sp.person.type,
                    position=sp.position,
                    appear_eps=sp.appear_eps,
                )
            )

    return {"subject_id": bangumi_id, "persons": results}
