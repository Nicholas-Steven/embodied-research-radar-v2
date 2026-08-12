"""
去重（Deduplication）。

文档第二十三节去重至少处理：
- arXiv 版本重复（arXiv ID 形如 2401.12345v1/v2）
- title 轻微变化
- 更新版本
- 正式论文与 arXiv 可能重复
- 同一论文多次抓取

优先级键：DOI > arXiv ID (去版本号) > Normalized Title
"""
from __future__ import annotations

import re

from schema import Paper


def normalize_arxiv_id(arxiv_id: str | None) -> str:
    """去除版本号：2401.12345v2 -> 2401.12345"""
    if not arxiv_id:
        return ""
    return re.sub(r"v\d+$", "", arxiv_id.strip())


def normalize_title(title: str) -> str:
    """标题归一化：小写、去标点、压缩空白。"""
    if not title:
        return ""
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def dedup_key(paper: Paper) -> tuple[str, str, str]:
    """生成去重键：(doi, arxiv_id_norm, title_norm)。
    任何非空字段都参与判断。
    """
    return (
        (paper.doi or "").strip().lower(),
        normalize_arxiv_id(paper.arxiv_id),
        normalize_title(paper.title),
    )


def is_duplicate(paper: Paper, seen_keys: set[tuple[str, str, str]]) -> bool:
    """判断 paper 是否与已见论文重复。
    任一非空键命中即视为重复。
    """
    doi, aid, title = dedup_key(paper)
    for existing in seen_keys:
        e_doi, e_aid, e_title = existing
        if doi and doi == e_doi:
            return True
        if aid and aid == e_aid:
            return True
        if title and len(title) > 10 and title == e_title:
            return True
    return False


def deduplicate(papers: list[Paper]) -> list[Paper]:
    """对论文列表去重，保留首次出现的版本。
    后续版本若有更新字段，可在此合并（V1 简单保留首个）。
    """
    seen: set[tuple[str, str, str]] = set()
    result: list[Paper] = []
    for p in papers:
        if is_duplicate(p, seen):
            continue
        seen.add(dedup_key(p))
        result.append(p)
    return result
