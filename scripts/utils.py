"""
工具函数：JSONL 读写、日期处理、安全字符串。
"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from schema import Paper


def write_jsonl(path: str | Path, papers: Iterable[Paper]) -> int:
    """将 Paper 列表写为 JSONL，返回写入条数。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for p in papers:
            f.write(json.dumps(p.to_dict(), ensure_ascii=False) + "\n")
            count += 1
    return count


def read_jsonl(path: str | Path) -> list[Paper]:
    """读取 JSONL 为 Paper 列表。"""
    path = Path(path)
    if not path.exists():
        return []
    papers: list[Paper] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            # 仅取 schema 已知字段，过滤未知键
            papers.append(_from_dict(d))
    return papers


def _from_dict(d: dict[str, Any]) -> Paper:
    """从 dict 构造 Paper，忽略未知键。"""
    from schema import SCHEMA_FIELDS
    filtered = {k: v for k, v in d.items() if k in SCHEMA_FIELDS}
    return Paper(**filtered)


def merge_papers(*lists: list[Paper]) -> list[Paper]:
    """合并多个论文列表（不去重）。"""
    merged: list[Paper] = []
    for lst in lists:
        merged.extend(lst)
    return merged


def today_iso() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d")
