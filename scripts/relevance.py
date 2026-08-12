"""
相关性筛选与评分（Stage 2 + Research Relevance Score）。

文档第八节：二级相关性筛选
- Stage 1 检索召回（arxiv_fetcher 完成）
- Stage 2 相关性判断：根据 title/abstract/categories/methods/robot manipulation context 过滤无关论文

文档第九节：相关性评分 0-100，转星级，必须解释

评分组成：
- 核心高权关键词命中（force/torque/tactile/haptic/contact/vision-force/visuotactile/f/t sensor/wrist sensor）
- 机器人操作上下文词命中（robot/manipulation/grasp/assembly/peg-in-hole/insertion/end-effector/gripper/manipulator/automation）
- 排除上下文命中减分（physics/material science/fluid dynamics/pure computer vision/computational fluid）
- 有代码 +5
- abstract 长度合理 +3
- 顶会顶刊 +5

低于 pass_threshold 的论文在 Stage 2 被剔除。
"""
from __future__ import annotations

import re
from typing import Iterable

from schema import Paper
from config_loader import load_yaml


def _lower_text(paper: Paper) -> str:
    parts = [paper.title or "", paper.abstract or ""]
    parts.extend(paper.methods or [])
    parts.extend(paper.keywords or [])
    return " ".join(parts).lower()


def _count_hits(text: str, terms: Iterable[str]) -> tuple[int, list[str]]:
    """返回命中次数与命中词列表。"""
    hits: list[str] = []
    count = 0
    for term in terms:
        t = term.lower().strip()
        if not t:
            continue
        # 词形匹配：允许 - / 空格等变体
        pattern = re.escape(t)
        found = re.findall(pattern, text)
        if found:
            count += len(found)
            hits.append(term)
    return count, hits


def compute_relevance(paper: Paper, scoring_cfg: dict | None = None) -> tuple[int, str, list[str], list[str]]:
    """计算相关性评分。
    返回 (score, reason, core_hits, context_hits)。
    """
    cfg = scoring_cfg or load_yaml("scoring")
    text = _lower_text(paper)

    core_terms = cfg.get("core_terms", [])
    robot_context = cfg.get("robot_context_terms", [])
    exclude_context = cfg.get("exclude_context_terms", [])
    weights = cfg.get("weights", {})

    core_count, core_hits = _count_hits(text, core_terms)
    robot_count, robot_hits = _count_hits(text, robot_context)
    exclude_count, exclude_hits = _count_hits(text, exclude_context)

    score = 0
    reasons: list[str] = []

    if core_count > 0:
        score += weights.get("core_term_hit", 20) * min(core_count, 3)
        reasons.append(f"命中核心词 {core_hits}")

    if robot_count > 0:
        score += weights.get("robot_context_hit", 8) * min(robot_count, 4)
        reasons.append(f"命中机器人上下文 {robot_hits}")

    if exclude_count > 0:
        score += weights.get("exclude_context_hit", -25) * exclude_count
        reasons.append(f"命中排除上下文 {exclude_hits}（减分）")

    if paper.code_url:
        score += weights.get("has_code", 5)
        reasons.append("有代码 (+5)")

    if len(paper.abstract) > 500:
        score += weights.get("long_abstract", 3)
        reasons.append("摘要信息量足 (+3)")

    # 上限 100，下限 0
    score = max(0, min(100, score))
    reason = "；".join(reasons) if reasons else "无显著命中"
    return score, reason, core_hits, robot_hits


def score_to_stars(score: int, scoring_cfg: dict | None = None) -> str:
    """分数转星级。"""
    cfg = scoring_cfg or load_yaml("scoring")
    thresholds = cfg.get("star_thresholds", {})
    if score >= thresholds.get("five_star", 85):
        return "★★★★★"
    if score >= thresholds.get("four_star", 70):
        return "★★★★☆"
    if score >= thresholds.get("three_star", 55):
        return "★★★☆☆"
    if score >= thresholds.get("two_star", 40):
        return "★★☆☆☆"
    return "★☆☆☆☆"


def filter_and_score(
    papers: list[Paper],
    scoring_cfg: dict | None = None,
    pass_threshold: int | None = None,
) -> list[Paper]:
    """对论文列表执行相关性评分 + Stage 2 筛选。
    低于 pass_threshold 的论文被剔除。
    """
    cfg = scoring_cfg or load_yaml("scoring")
    if pass_threshold is None:
        pass_threshold = cfg.get("pass_threshold", 40)

    kept: list[Paper] = []
    for paper in papers:
        score, reason, core_hits, robot_hits = compute_relevance(paper, cfg)
        paper.relevance_score = score
        paper.relevance_reason = reason
        paper.relevance_stars = score_to_stars(score, cfg)

        # 把命中的核心词回填到 keywords（如果还没有）
        for kw in core_hits:
            if kw not in paper.keywords:
                paper.keywords.append(kw)

        if score >= pass_threshold:
            kept.append(paper)

    # 按相关度降序
    kept.sort(key=lambda p: p.relevance_score, reverse=True)
    return kept
