"""JSON Lines 文件解析器 — 逐行读取大文件，内存友好。"""

import json
from typing import Generator


def read_jsonlines(file_path: str) -> Generator[dict, None, None]:
    """逐行读取 JSON Lines 文件，返回每行解析后的 dict。

    适用于 GB 级别的大文件，不会一次性加载到内存。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  [WARN] Line {line_num} in {file_path}: {e}")


def count_lines(file_path: str) -> int:
    """快速统计文件行数（非空行）。"""
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count
