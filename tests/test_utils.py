"""测试工具函数：JSONL 读写、合并、日期。"""
import tempfile
from pathlib import Path

from schema import Paper
from utils import write_jsonl, read_jsonl, merge_papers, today_iso


def test_jsonl_roundtrip_preserves_fields():
    p = Paper(
        paper_id="x",
        title="T",
        authors=["A"],
        abstract="abs",
        arxiv_id="2401.1v1",
        relevance_score=80,
        keywords=["force", "vision"],
    )
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "test.jsonl"
        n = write_jsonl(path, [p])
        assert n == 1
        loaded = read_jsonl(path)
        assert len(loaded) == 1
        assert loaded[0].title == "T"
        assert loaded[0].relevance_score == 80
        assert loaded[0].keywords == ["force", "vision"]


def test_read_jsonl_nonexistent_returns_empty():
    assert read_jsonl("/nonexistent/path/xyz.jsonl") == []


def test_merge_papers_concatenates():
    p1 = Paper(paper_id="1", title="A")
    p2 = Paper(paper_id="2", title="B")
    merged = merge_papers([p1], [p2])
    assert len(merged) == 2


def test_today_iso_format():
    s = today_iso()
    assert len(s) == 10
    assert s[4] == "-" and s[7] == "-"
