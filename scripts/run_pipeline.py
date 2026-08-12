"""
论文抓取主入口。

流程（文档第二十四节）：
  fetch -> normalize -> deduplicate -> filter -> rank -> AI summarize -> write JSONL

用法：
  python scripts/run_pipeline.py                 # 每日增量抓取
  python scripts/run_pipeline.py --init          # 初始化大抓取
  python scripts/run_pipeline.py --no-ai         # 跳过 AI 分析
  python scripts/run_pipeline.py --topic vision_force  # 仅抓某 topic 对应 query groups

输出：
  data/raw/<date>_arxiv.jsonl      原始抓取（去重前）
  data/processed/papers.jsonl      处理后合并库（用于前端构建）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 允许 `python scripts/run_pipeline.py` 直接 import
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_loader import load_all_config, ai_config
from arxiv_fetcher import fetch_all
from dedup import deduplicate, dedup_key
from relevance import filter_and_score
from ai_analyzer import analyze_papers
from utils import write_jsonl, read_jsonl, today_iso
from schema import Paper


DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PROC = Path(__file__).resolve().parent.parent / "data" / "processed"


def run(init: bool = False, no_ai: bool = False, topic: str | None = None):
    cfg = load_all_config()
    queries = cfg["queries"]["query_groups"]
    group_topic = cfg["queries"]["group_topic_map"]

    # 如果指定 topic，过滤出该 topic 对应的 query groups
    if topic:
        queries = {gid: ps for gid, ps in queries.items() if group_topic.get(gid) == topic}
        if not queries:
            print(f"[pipeline] no query groups mapped to topic '{topic}'")
            return

    max_per_query = cfg["site"]["arxiv"]["max_results_per_query"]
    sleep_s = cfg["site"]["arxiv"]["sleep_seconds"]
    if init:
        # 初始化大抓取：放宽单组上限
        max_per_query = max(max_per_query, 100)

    print(f"[pipeline] fetching {len(queries)} query groups (init={init})")
    raw_by_group = fetch_all(
        queries,
        max_results_per_query=max_per_query,
        sleep_seconds=sleep_s,
    )

    # 标记 research_topics
    all_papers: list[Paper] = []
    for group_id, papers in raw_by_group.items():
        topic_id = group_topic.get(group_id, "")
        for p in papers:
            if topic_id and topic_id not in p.research_topics:
                p.research_topics.append(topic_id)
            # 也用 group 名作为 keyword 线索（仅当缺失）
            if not p.keywords:
                p.keywords = []
        all_papers.extend(papers)

    print(f"[pipeline] raw fetched: {len(all_papers)}")

    # 写原始
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    raw_path = DATA_RAW / f"{today_iso()}_arxiv.jsonl"
    write_jsonl(raw_path, all_papers)
    print(f"[pipeline] wrote raw -> {raw_path}")

    # 去重
    deduped = deduplicate(all_papers)
    print(f"[pipeline] after dedup: {len(deduped)}")

    # 相关性筛选 + 评分 + 排序
    scoring_cfg = cfg["scoring"]
    kept = filter_and_score(deduped, scoring_cfg=scoring_cfg)
    print(f"[pipeline] after relevance filter: {len(kept)}")

    # AI 分析
    if no_ai:
        for p in kept:
            p.ai_status = "skipped"
        print("[pipeline] AI analysis skipped")
    else:
        kept = analyze_papers(kept)

    # 合并历史库（保留旧数据，新数据覆盖同 paper_id）
    papers_jsonl = DATA_PROC / "papers.jsonl"
    historical = read_jsonl(papers_jsonl)
    merged: dict[str, Paper] = {p.paper_id: p for p in historical}
    for p in kept:
        merged[p.paper_id] = p
    final = list(merged.values())
    # 按相关度+日期排序
    final.sort(key=lambda p: (p.relevance_score, p.published_date), reverse=True)

    write_jsonl(papers_jsonl, final)
    print(f"[pipeline] wrote {len(final)} papers -> {papers_jsonl}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true", help="初始化大抓取")
    ap.add_argument("--no-ai", action="store_true", help="跳过 AI 分析")
    ap.add_argument("--topic", type=str, default=None, help="仅抓某 topic 对应的 query groups")
    args = ap.parse_args()
    run(init=args.init, no_ai=args.no_ai, topic=args.topic)


if __name__ == "__main__":
    main()
