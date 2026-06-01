"""Bangumi Wiki Infobox 解析器 — 将 Wiki 语法字符串转为结构化 dict。"""

from typing import Any, Dict, List, Optional

from bgm_tv_wiki import Wiki, parse as wiki_parse, try_parse as wiki_try_parse


def _field_value_to_dict(value) -> Any:
    """将 Wiki Field 的值转换为可 JSON 序列化的 Python 对象。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    # 列表值：可能是 (key, value) 元组列表或纯值列表
    if hasattr(value, "__iter__"):
        items = []
        for item in value:
            if hasattr(item, "key") and hasattr(item, "value"):
                k = item.key.strip() if item.key else ""
                v = item.value.strip() if item.value else ""
                items.append({"k": k, "v": v})
            else:
                items.append(str(item))
        return items
    return str(value)


def _wiki_to_dict(wiki: Wiki) -> Dict[str, Any]:
    """将 Wiki 对象转为扁平字典。"""
    result: Dict[str, Any] = {}
    for field in wiki.fields:
        result[field.key] = _field_value_to_dict(field.value)
    return result


def parse_infobox(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    """解析 Bangumi Wiki 语法的 infobox 字符串。

    返回 {"type": str, "fields": dict} 格式的字典，
    解析失败返回 None。

    预处理：标准化 \\r\\n → \\n（Bangumi Archive 数据中常见）。
    """
    if not raw or not raw.strip():
        return None

    # 标准化换行符
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    try:
        wiki = wiki_parse(text)
    except Exception:
        try:
            wiki = wiki_try_parse(text)
        except Exception:
            return None

    if not wiki or not wiki.fields:
        return None

    return {
        "type": wiki.type or "",
        "fields": _wiki_to_dict(wiki),
    }


def parse_infobox_flat(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    """解析 infobox 并返回扁平字典（仅 fields 内容，不含 type）。

    将列表值展开：有 key 的项保留为 {"k": key, "v": value}，
    多个标量值的列表合并为逗号分隔字符串。
    """
    parsed = parse_infobox(raw)
    if not parsed:
        return None
    return parsed.get("fields", {})
