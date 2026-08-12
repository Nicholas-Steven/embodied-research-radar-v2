"""
构建前端静态数据。

读取 data/processed/papers.jsonl，生成：
- frontend/public/papers.json    全量论文数组
- frontend/public/site.json      站点元数据

若 papers.jsonl 不存在（首次 clone），尝试用 data/processed/papers.jsonl；
若仍无，则写入空数组，前端显示"暂无数据"，不崩溃。

用法：
  python scripts/build_data.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import read_jsonl, today_iso
from config_loader import load_all_config

ROOT = Path(__file__).resolve().parent.parent
PAPERS_JSONL = ROOT / "data" / "processed" / "papers.jsonl"
FRONTEND_PUBLIC = ROOT / "frontend" / "public"


def main() -> int:
    FRONTEND_PUBLIC.mkdir(parents=True, exist_ok=True)

    papers = read_jsonl(PAPERS_JSONL)
    papers_dicts = [p.to_dict() for p in papers]

    # 写 papers.json
    out_papers = FRONTEND_PUBLIC / "papers.json"
    out_papers.write_text(
        json.dumps(papers_dicts, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[build_data] wrote {len(papers_dicts)} papers -> {out_papers}")

    # 站点元数据
    cfg = load_all_config()
    topics_cfg = cfg.get("topics", {}).get("topics", [])
    topic_counts: dict[str, int] = {}
    for p in papers:
        for t in p.research_topics:
            topic_counts[t] = topic_counts.get(t, 0) + 1

    site_meta = {
        "last_updated": today_iso(),
        "total_papers": len(papers_dicts),
        "topic_counts": topic_counts,
        "topics": [
            {
                "id": t.get("id"),
                "name_zh": t.get("name_zh"),
                "name_en": t.get("name_en"),
                "nav_label": t.get("nav_label"),
                "status": t.get("status"),
                "description_zh": t.get("description_zh"),
            }
            for t in topics_cfg
        ],
    }

    out_site = FRONTEND_PUBLIC / "site.json"
    out_site.write_text(
        json.dumps(site_meta, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[build_data] wrote site meta -> {out_site}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
