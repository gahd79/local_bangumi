#!/usr/bin/env python3
"""初始化数据库 — 运行 Alembic 迁移创建所有表。"""

import subprocess
import sys
from pathlib import Path


def main():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
