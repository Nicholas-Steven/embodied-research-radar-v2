"""
arXiv 检索与解析。

使用 arXiv REST API（http://export.arxiv.org/api/query）
返回 Atom XML，通过 feedparser 解析为内部 Paper 对象。

查询策略：
- 多 Query Group 并行检索（vision_force / vision_tactile / contact / failure / recovery）
- 每个 group 内部短语用 OR 组合
- 尊重 arXiv rate limit：每次请求间隔 sleep_seconds
"""
from __future__ import annotations

import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

from schema import Paper
from config_loader import load_yaml, env

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def build_query(phrases: list[str]) -> str:
    """将短语列表组合成 arXiv 查询字符串。
    短语用 all:"phrase" 包裹，OR 连接。
    """
    encoded = [f'all:"{urllib.parse.quote(p)}"' for p in phrases]
    return "+OR+".join(encoded)


def parse_arxiv_xml(xml_text: str) -> list[Paper]:
    """解析 arXiv Atom XML 为 Paper 列表。"""
    root = ET.fromstring(xml_text)
    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        arxiv_id_full = _text(entry, "atom:id")
        if not arxiv_id_full:
            continue
        # 形如 http://arxiv.org/abs/2401.12345v1
        arxiv_id = arxiv_id_full.split("/abs/")[-1]

        title = _text(entry, "atom:title").strip().replace("\n", " ")
        title = " ".join(title.split())

        summary = _text(entry, "atom:summary").strip().replace("\n", " ")
        summary = " ".join(summary.split())

        published = _text(entry, "atom:published")
        updated = _text(entry, "atom:updated")
        year = int(published[:4]) if published and len(published) >= 4 else None

        authors: list[str] = []
        for author in entry.findall("atom:author", ARXIV_NS):
            name = author.find("atom:name", ARXIV_NS)
            if name is not None and name.text:
                authors.append(name.text.strip())

        pdf_url = ""
        paper_url = ""
        for link in entry.findall("atom:link", ARXIV_NS):
            rel = link.get("rel", "")
            href = link.get("href", "")
            if rel == "alternate":
                paper_url = href
            elif rel == "related" and "pdf" in href:
                pdf_url = href
        if not pdf_url:
            pdf_url = f"http://arxiv.org/pdf/{arxiv_id}"

        # DOI
        doi_elem = entry.find("{http://arxiv.org/schemas/atom}doi")
        doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

        paper = Paper(
            paper_id=f"arxiv-{arxiv_id}",
            title=title,
            authors=authors,
            abstract=summary,
            published_date=_iso_date(published),
            updated_date=_iso_date(updated),
            year=year,
            arxiv_id=arxiv_id,
            paper_url=paper_url or f"http://arxiv.org/abs/{arxiv_id}",
            pdf_url=pdf_url,
            doi=doi,
            venue="Preprint / arXiv",
            source="arxiv",
            last_checked=datetime.utcnow().strftime("%Y-%m-%d"),
        )
        papers.append(paper)
    return papers


def fetch_query(
    query_str: str,
    start: int = 0,
    max_results: int = 50,
    api_url: str | None = None,
    timeout: int = 30,
) -> str:
    """调用 arXiv API，返回原始 XML 文本。"""
    api_url = api_url or env("ARXIV_API_URL", "http://export.arxiv.org/api/query")
    url = (
        f"{api_url}?search_query={query_str}"
        f"&start={start}&max_results={max_results}"
        "&sortBy=submittedDate&sortOrder=descending"
    )
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "EmbodiedResearchRadar/1.0"})
    resp.raise_for_status()
    return resp.text


def fetch_group(
    group_id: str,
    phrases: list[str],
    max_results: int = 50,
    api_url: str | None = None,
    sleep_seconds: int = 4,
) -> list[Paper]:
    """抓取一个 query group 的论文。"""
    query_str = build_query(phrases)
    xml_text = fetch_query(query_str, max_results=max_results, api_url=api_url)
    time.sleep(sleep_seconds)
    return parse_arxiv_xml(xml_text)


def fetch_all(
    queries_cfg: dict,
    max_results_per_query: int = 50,
    api_url: str | None = None,
    sleep_seconds: int = 4,
) -> dict[str, list[Paper]]:
    """抓取所有 query group。返回 {group_id: [Paper, ...]}。"""
    results: dict[str, list[Paper]] = {}
    for group_id, phrases in queries_cfg.items():
        print(f"[arxiv] fetching group '{group_id}': {len(phrases)} phrases")
        try:
            papers = fetch_group(
                group_id, phrases,
                max_results=max_results_per_query,
                api_url=api_url,
                sleep_seconds=sleep_seconds,
            )
            results[group_id] = papers
            print(f"[arxiv] group '{group_id}' got {len(papers)} papers")
        except Exception as e:
            print(f"[arxiv] group '{group_id}' FAILED: {e}")
            results[group_id] = []
    return results


# --- helpers ---

def _text(parent: ET.Element, tag: str) -> str:
    elem = parent.find(tag, ARXIV_NS)
    return elem.text if elem is not None and elem.text else ""


def _iso_date(raw: str) -> str:
    """arXiv 日期 2024-01-15T00:00:00Z -> 2024-01-15"""
    if not raw:
        return ""
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return ""
