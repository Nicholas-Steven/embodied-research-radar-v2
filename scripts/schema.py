"""
统一 Paper Schema 定义。

数据层与 UI 解耦：管线产出 JSONL（每行一篇论文），
构建期合并为单个 papers.json 供前端读取。

字段依据文档第二十节 Schema 至少包含，并允许改进。
事实字段与 AI 分析字段明确区分。
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields
from datetime import date
from typing import Optional


@dataclass
class Paper:
    # --- 基础信息（事实字段，来自数据源） ---
    paper_id: str                       # 内部稳定 ID（arxiv_id 或 normalized title）
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    abstract_zh: str = ""               # AI 字段
    published_date: str = ""            # ISO YYYY-MM-DD
    updated_date: str = ""
    year: Optional[int] = None
    venue: str = "Preprint / arXiv"     # 默认不猜
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    paper_url: str = ""
    pdf_url: str = ""
    code_url: Optional[str] = None
    project_url: Optional[str] = None
    image: Optional[str] = None         # 缩略图 URL（V1 用占位）

    # --- 分类 ---
    research_topics: list[str] = field(default_factory=list)    # topic id 列表
    literature_categories: list[str] = field(default_factory=list)  # A/B/C/D
    methods: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    sensors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    # --- AI 分析字段 ---
    summary_one_sentence: str = ""      # AI
    research_problem: str = ""          # AI
    core_contributions: list[str] = field(default_factory=list)  # AI
    method_summary: str = ""            # AI
    experimental_setup: str = ""        # AI
    key_results: list[str] = field(default_factory=list)          # AI
    limitations: str = ""               # AI
    why_it_matters: str = ""            # AI

    # --- 相关性评分 ---
    relevance_score: int = 0            # 0-100
    relevance_reason: str = ""
    relevance_stars: str = "★☆☆☆☆"

    # --- My Research 字段 ---
    related_to_my_research: list[str] = field(default_factory=list)  # related_to 值
    why_relevant: str = ""
    recommended_reading: list[str] = field(default_factory=list)
    reproduction_value: str = ""        # High/Medium/Low
    reproduction_reason: str = ""
    core_candidate: str = "No"          # Yes/No/Review

    # --- 元数据 ---
    source: str = "arxiv"               # arxiv/openreview/...
    last_checked: str = ""              # ISO date
    ai_status: str = "pending"          # pending/done/skipped/failed

    def to_dict(self) -> dict:
        return asdict(self)


# Schema 中所有允许的字段名（用于校验）
SCHEMA_FIELDS = {f.name for f in fields(Paper)}

# AI 生成的字段（缺 API 时标记 Pending）
AI_FIELDS = [
    "abstract_zh",
    "summary_one_sentence",
    "research_problem",
    "core_contributions",
    "method_summary",
    "experimental_setup",
    "key_results",
    "limitations",
    "why_it_matters",
    "why_relevant",
    "reproduction_value",
    "reproduction_reason",
    "recommended_reading",
]

# 事实字段（不可由 AI 编造）
FACT_FIELDS = [
    "title",
    "authors",
    "doi",
    "venue",
    "code_url",
    "project_url",
    "year",
    "published_date",
]
