"""数据导入服务 — 将 Bangumi Archive JSON Lines 数据导入数据库。

导入顺序严格按照外键依赖：
1. Subject, Person, Character（无 FK 依赖）
2. Episode（→ Subject）
3. SubjectRelation, SubjectCharacter, SubjectPerson（→ 主表）
4. PersonCharacter, PersonRelation（→ 主表）
"""

import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import (
    Subject,
    Episode,
    Person,
    Character,
    SubjectRelation,
    SubjectCharacter,
    SubjectPerson,
    PersonCharacter,
    PersonRelation,
)
from ..utils.parser import count_lines, read_jsonlines
from ..utils.infobox_parser import parse_infobox

logger = logging.getLogger(__name__)

BATCH_SIZE = 500
LOG_INTERVAL = 10000  # 每 N 条记录输出一次进度


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _load_valid_ids(db: Session, model, column_name: str = "bangumi_id") -> Set[int]:
    """从数据库加载所有有效 ID 到内存（用于 FK 校验）。"""
    col = getattr(model, column_name)
    ids = db.query(col).all()
    return {row[0] for row in ids}


def _bulk_insert(db: Session, records: List[dict], model, label: str) -> int:
    """批量插入记录。返回成功插入数。"""
    if not records:
        return 0
    try:
        db.bulk_insert_mappings(model, records)
        db.commit()
        return len(records)
    except Exception as e:
        db.rollback()
        logger.error(f"  [ERROR] {label} bulk insert failed: {e}")
        # 逐条重试以定位问题行
        success = 0
        for rec in records:
            try:
                db.bulk_insert_mappings(model, [rec])
                db.commit()
                success += 1
            except Exception:
                db.rollback()
        return success


# ---------------------------------------------------------------------------
# 导入函数
# ---------------------------------------------------------------------------


def import_subjects(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 Subject（条目）数据。

    关键映射：
    - id → bangumi_id
    - infobox → infobox_raw（原文）+ infobox_parsed（解析后 dict）
    - favorite → wish_count / doing_count / done_count / on_hold_count / dropped_count
    """
    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            favorite = row.get("favorite") or {}
            infobox_parsed = parse_infobox(row.get("infobox"))

            records.append({
                "bangumi_id": row["id"],
                "type": row["type"],
                "name": row.get("name", ""),
                "name_cn": row.get("name_cn"),
                "name_en": row.get("name_en"),
                "infobox_raw": row.get("infobox"),
                "infobox_parsed": infobox_parsed,
                "platform": row.get("platform"),
                "summary": row.get("summary"),
                "nsfw": row.get("nsfw", False),
                "date": row.get("date"),
                "series": row.get("series", False),
                "tags": row.get("tags"),
                "meta_tags": row.get("meta_tags"),
                "score": row.get("score"),
                "score_details": row.get("score_details"),
                "rank": row.get("rank"),
                "wish_count": favorite.get("wish", 0),
                "doing_count": favorite.get("doing", 0),
                "done_count": favorite.get("done", 0),
                "on_hold_count": favorite.get("on_hold", 0),
                "dropped_count": favorite.get("dropped", 0),
            })
        except Exception as e:
            skipped += 1
            continue

        count += 1

        # 批量写入
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, Subject, "subjects")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  subjects: {count}/{total} ({count * 100 // total}%)")
            if progress_callback:
                progress_callback("subjects", count, total)

    # 写入剩余记录
    if records:
        _bulk_insert(db, records, Subject, "subjects")

    logger.info(f"  subjects done: {count} imported, {skipped} skipped")
    return count


def import_persons(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 Person（人物）数据。"""
    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            infobox_parsed = parse_infobox(row.get("infobox"))
            records.append({
                "bangumi_id": row["id"],
                "name": row.get("name", ""),
                "type": row.get("type", 1),
                "career": row.get("career"),
                "infobox_raw": row.get("infobox"),
                "infobox_parsed": infobox_parsed,
                "summary": row.get("summary"),
                "comments_count": row.get("comments", 0),
                "collects_count": row.get("collects", 0),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, Person, "persons")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  persons: {count}/{total} ({count * 100 // total}%)")

    if records:
        _bulk_insert(db, records, Person, "persons")

    logger.info(f"  persons done: {count} imported, {skipped} skipped")
    return count


def import_characters(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 Character（角色）数据。"""
    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            infobox_parsed = parse_infobox(row.get("infobox"))
            records.append({
                "bangumi_id": row["id"],
                "name": row.get("name", ""),
                "role": row.get("role", 1),
                "infobox_raw": row.get("infobox"),
                "infobox_parsed": infobox_parsed,
                "summary": row.get("summary"),
                "comments_count": row.get("comments", 0),
                "collects_count": row.get("collects", 0),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, Character, "characters")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  characters: {count}/{total} ({count * 100 // total}%)")

    if records:
        _bulk_insert(db, records, Character, "characters")

    logger.info(f"  characters done: {count} imported, {skipped} skipped")
    return count


def import_episodes(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 Episode（剧集）数据。

    FK subject_id → subjects.bangumi_id，无效 FK 的记录会被跳过。
    """
    # 加载有效 subject ID
    valid_subjects = _load_valid_ids(db, Subject)
    logger.info(f"  loaded {len(valid_subjects)} valid subject IDs for FK check")

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            sid = row.get("subject_id")
            if sid and sid not in valid_subjects:
                skipped += 1
                continue

            records.append({
                "bangumi_id": row["id"],
                "subject_id": sid,
                "name": row.get("name", ""),
                "name_cn": row.get("name_cn"),
                "description": row.get("description"),
                "airdate": row.get("airdate"),
                "disc": row.get("disc", 0),
                "duration": row.get("duration"),
                "sort": row.get("sort", 0),
                "type": row.get("type", 0),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, Episode, "episodes")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  episodes: {count}/{total}")

    if records:
        _bulk_insert(db, records, Episode, "episodes")

    logger.info(f"  episodes done: {count} imported, {skipped} skipped (FK invalid or error)")
    return count


def import_subject_relations(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 SubjectRelation 数据。"""
    valid_subjects = _load_valid_ids(db, Subject)
    logger.info(f"  loaded {len(valid_subjects)} valid subject IDs for FK check")

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            sid = row.get("subject_id")
            rid = row.get("related_subject_id")
            if sid not in valid_subjects or rid not in valid_subjects:
                skipped += 1
                continue

            records.append({
                "subject_id": sid,
                "relation_type": row["relation_type"],
                "related_subject_id": rid,
                "order": row.get("order", 0),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, SubjectRelation, "subject_relations")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  subject_relations: {count}/{total}")

    if records:
        _bulk_insert(db, records, SubjectRelation, "subject_relations")

    logger.info(f"  subject_relations done: {count} imported, {skipped} skipped")
    return count


def import_subject_characters(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 SubjectCharacter 数据。"""
    valid_subjects = _load_valid_ids(db, Subject)
    valid_characters = _load_valid_ids(db, Character)
    logger.info(f"  loaded {len(valid_subjects)} subjects, {len(valid_characters)} characters")

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            sid = row.get("subject_id")
            cid = row.get("character_id")
            if sid not in valid_subjects or cid not in valid_characters:
                skipped += 1
                continue

            records.append({
                "subject_id": sid,
                "character_id": cid,
                "type": row.get("type", 1),
                "order": row.get("order", 0),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, SubjectCharacter, "subject_characters")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  subject_characters: {count}/{total}")

    if records:
        _bulk_insert(db, records, SubjectCharacter, "subject_characters")

    logger.info(f"  subject_characters done: {count} imported, {skipped} skipped")
    return count


def import_subject_persons(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 SubjectPerson 数据（STAFF 关联）。"""
    valid_subjects = _load_valid_ids(db, Subject)
    valid_persons = _load_valid_ids(db, Person)
    logger.info(f"  loaded {len(valid_subjects)} subjects, {len(valid_persons)} persons")

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            sid = row.get("subject_id")
            pid = row.get("person_id")
            if sid not in valid_subjects or pid not in valid_persons:
                skipped += 1
                continue

            records.append({
                "subject_id": sid,
                "person_id": pid,
                "position": row.get("position"),
                "appear_eps": row.get("appear_eps", ""),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, SubjectPerson, "subject_persons")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  subject_persons: {count}/{total}")

    if records:
        _bulk_insert(db, records, SubjectPerson, "subject_persons")

    logger.info(f"  subject_persons done: {count} imported, {skipped} skipped")
    return count


def import_person_characters(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 PersonCharacter 数据（CV 关联）。"""
    valid_persons = _load_valid_ids(db, Person)
    valid_subjects = _load_valid_ids(db, Subject)
    valid_characters = _load_valid_ids(db, Character)
    logger.info(
        f"  loaded {len(valid_persons)} persons, "
        f"{len(valid_subjects)} subjects, {len(valid_characters)} characters"
    )

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            pid = row.get("person_id")
            sid = row.get("subject_id")
            cid = row.get("character_id")
            if pid not in valid_persons or sid not in valid_subjects or cid not in valid_characters:
                skipped += 1
                continue

            records.append({
                "person_id": pid,
                "subject_id": sid,
                "character_id": cid,
                "type": row.get("type", 0),
                "summary": row.get("summary", ""),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, PersonCharacter, "person_characters")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  person_characters: {count}/{total}")

    if records:
        _bulk_insert(db, records, PersonCharacter, "person_characters")

    logger.info(f"  person_characters done: {count} imported, {skipped} skipped")
    return count


def import_person_relations(
    db: Session,
    file_path: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> int:
    """导入 PersonRelation 数据（人物/角色间关联）。"""
    valid_persons = _load_valid_ids(db, Person)
    valid_characters = _load_valid_ids(db, Character)
    valid_all = valid_persons | valid_characters
    logger.info(f"  loaded {len(valid_all)} valid person/character IDs")

    total = count_lines(file_path)
    records = []
    count = 0
    skipped = 0

    for row in read_jsonlines(file_path):
        try:
            pid = row.get("person_id")
            rid = row.get("related_person_id")
            # person_relations 中的 ID 可能指向 person 或 character
            if pid not in valid_all or rid not in valid_all:
                skipped += 1
                continue

            records.append({
                "person_type": row.get("person_type", ""),
                "person_id": pid,
                "related_person_id": rid,
                "relation_type": row.get("relation_type", 0),
                "spoiler": row.get("spoiler", False),
                "ended": row.get("ended", False),
            })
        except Exception:
            skipped += 1
            continue

        count += 1
        if len(records) >= BATCH_SIZE:
            _bulk_insert(db, records, PersonRelation, "person_relations")
            records = []

        if count % LOG_INTERVAL == 0:
            logger.info(f"  person_relations: {count}/{total}")

    if records:
        _bulk_insert(db, records, PersonRelation, "person_relations")

    logger.info(f"  person_relations done: {count} imported, {skipped} skipped")
    return count


# ---------------------------------------------------------------------------
# 统一导入入口
# ---------------------------------------------------------------------------


def import_all_from_dir(
    dump_dir: str,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
) -> Dict[str, int]:
    """从本地 dump 目录导入所有数据文件。

    返回各表的导入记录数统计。
    """
    dump_path = Path(dump_dir)
    if not dump_path.exists():
        raise FileNotFoundError(f"Dump directory not found: {dump_dir}")

    files = {
        "subjects": dump_path / "subject.jsonlines",
        "persons": dump_path / "person.jsonlines",
        "characters": dump_path / "character.jsonlines",
        "episodes": dump_path / "episode.jsonlines",
        "subject_relations": dump_path / "subject-relations.jsonlines",
        "subject_characters": dump_path / "subject-characters.jsonlines",
        "subject_persons": dump_path / "subject-persons.jsonlines",
        "person_characters": dump_path / "person-characters.jsonlines",
        "person_relations": dump_path / "person-relations.jsonlines",
    }

    # 检查文件是否存在
    missing = [k for k, v in files.items() if not v.exists()]
    if missing:
        logger.warning(f"Missing files: {missing}")

    results: Dict[str, int] = {}
    db = SessionLocal()

    try:
        # Phase 1: 无 FK 依赖的表（可按顺序或清空后导入）
        logger.info("=" * 60)
        logger.info("Phase 1: Importing base tables...")

        if files["subjects"].exists():
            logger.info("Importing subjects...")
            results["subjects"] = import_subjects(db, str(files["subjects"]), progress_callback)

        if files["persons"].exists():
            logger.info("Importing persons...")
            results["persons"] = import_persons(db, str(files["persons"]), progress_callback)

        if files["characters"].exists():
            logger.info("Importing characters...")
            results["characters"] = import_characters(db, str(files["characters"]), progress_callback)

        # Phase 2: Episode（依赖 Subject）
        if files["episodes"].exists():
            logger.info("Importing episodes...")
            results["episodes"] = import_episodes(db, str(files["episodes"]), progress_callback)

        # Phase 3: 关联表（依赖主表）
        logger.info("=" * 60)
        logger.info("Phase 3: Importing relation tables...")

        relation_importers = [
            ("subject_relations", import_subject_relations),
            ("subject_characters", import_subject_characters),
            ("subject_persons", import_subject_persons),
            ("person_characters", import_person_characters),
            ("person_relations", import_person_relations),
        ]

        for name, importer in relation_importers:
            if files[name].exists():
                logger.info(f"Importing {name}...")
                results[name] = importer(db, str(files[name]), progress_callback)

        logger.info("=" * 60)
        total_imported = sum(results.values())
        logger.info(f"Import complete! Total records: {total_imported}")
        for table, n in results.items():
            logger.info(f"  {table}: {n}")

    finally:
        db.close()

    return results
