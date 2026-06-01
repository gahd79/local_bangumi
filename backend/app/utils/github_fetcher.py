"""GitHub Archive 数据下载器。

从 Bangumi Archive GitHub Release 获取最新的数据导出文件。
"""

import hashlib
import io
import json
import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Optional

import httpx

logger = logging.getLogger(__name__)

LATEST_URL = (
    "https://raw.githubusercontent.com/bangumi/Archive/master/aux/latest.json"
)

EXPECTED_FILES = [
    "subject.jsonlines",
    "episode.jsonlines",
    "person.jsonlines",
    "character.jsonlines",
    "subject-relations.jsonlines",
    "subject-characters.jsonlines",
    "subject-persons.jsonlines",
    "person-characters.jsonlines",
    "person-relations.jsonlines",
]


class ArchiveVersion:
    """记录一次 Archive 发布的版本信息。"""

    def __init__(self, info: dict):
        self.name: str = info.get("name", "")
        self.download_url: str = info.get("browser_download_url", "")
        self.size: int = info.get("size", 0)
        self.digest: str = info.get("digest", "")  # "sha256:xxx" 格式
        self.created_at: str = info.get("created_at", "")

    @property
    def sha256(self) -> Optional[str]:
        if self.digest.startswith("sha256:"):
            return self.digest[7:]
        return None


def get_latest_version() -> Optional[ArchiveVersion]:
    """获取最新 Archive 版本的元信息。"""
    try:
        resp = httpx.get(LATEST_URL, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        info = resp.json()
        logger.info(f"Latest version: {info.get('name')} ({info.get('size', 0)} bytes)")
        return ArchiveVersion(info)
    except Exception as e:
        logger.error(f"Failed to fetch latest version: {e}")
        return None


def download_archive(
    version: ArchiveVersion,
    dest_dir: Optional[str] = None,
    verify_sha256: bool = False,
) -> Dict[str, str]:
    """下载并解压 Archive zip 文件。

    Args:
        version: ArchiveVersion 对象
        dest_dir: 解压目标目录，None 则使用临时目录
        verify_sha256: 是否校验 SHA-256

    Returns:
        dict: {"subject.jsonlines": "/path/to/file", ...}
    """
    if dest_dir:
        extract_dir = Path(dest_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
    else:
        extract_dir = Path(tempfile.mkdtemp(prefix="bangumi_dump_"))

    logger.info(f"Downloading {version.name} ({version.size / 1024 / 1024:.1f} MB)...")

    # 下载
    resp = httpx.get(version.download_url, follow_redirects=True, timeout=600)
    resp.raise_for_status()
    data = resp.content

    # SHA-256 校验
    if verify_sha256 and version.sha256:
        actual = hashlib.sha256(data).hexdigest()
        if actual != version.sha256:
            raise ValueError(
                f"SHA-256 mismatch! expected={version.sha256}, got={actual}"
            )
        logger.info("SHA-256 verified OK")

    # 解压
    logger.info(f"Extracting to {extract_dir}...")
    file_paths: Dict[str, str] = {}

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            basename = name.split("/")[-1]  # 去掉可能的目录前缀
            if not basename:
                continue
            # 只提取需要的 jsonlines 文件
            if basename in EXPECTED_FILES or basename.endswith(".jsonlines"):
                target = extract_dir / basename
                with zf.open(name) as src, open(target, "wb") as dst:
                    dst.write(src.read())
                file_paths[basename] = str(target)
                logger.info(f"  extracted: {basename}")

    logger.info(f"Download complete: {len(file_paths)} files extracted")
    return file_paths


def fetch_latest_to_dir(dest_dir: str) -> Optional[Dict[str, str]]:
    """便捷方法：获取最新版本并下载到指定目录。

    Returns:
        {"subject.jsonlines": "/path/to/file", ...} 或 None（失败时）
    """
    version = get_latest_version()
    if not version:
        return None
    return download_archive(version, dest_dir)
