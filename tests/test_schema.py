"""测试统一 Paper Schema。"""
from schema import Paper, SCHEMA_FIELDS, AI_FIELDS, FACT_FIELDS


def test_paper_defaults():
    p = Paper(paper_id="x", title="T")
    assert p.authors == []
    assert p.venue == "Preprint / arXiv"
    assert p.relevance_score == 0
    assert p.ai_status == "pending"
    assert p.core_candidate == "No"


def test_schema_fields_contains_required():
    required = {
        "paper_id", "title", "authors", "abstract", "abstract_zh",
        "published_date", "updated_date", "year", "venue", "doi",
        "arxiv_id", "paper_url", "pdf_url", "code_url", "project_url",
        "image", "research_topics", "literature_categories", "methods",
        "tasks", "sensors", "keywords", "summary_one_sentence",
        "research_problem", "core_contributions", "method_summary",
        "experimental_setup", "key_results", "limitations", "why_it_matters",
        "relevance_score", "relevance_reason", "related_to_my_research",
        "recommended_reading", "reproduction_value", "core_candidate",
        "source", "last_checked",
    }
    missing = required - SCHEMA_FIELDS
    assert not missing, f"schema 缺字段: {missing}"


def test_ai_fields_excluded_from_fact():
    # 事实字段不应在 AI 字段集合里
    for f in FACT_FIELDS:
        assert f not in AI_FIELDS


def test_to_dict_roundtrip_keys():
    p = Paper(paper_id="x", title="T", authors=["A", "B"])
    d = p.to_dict()
    assert set(d.keys()) == SCHEMA_FIELDS
    assert d["authors"] == ["A", "B"]
