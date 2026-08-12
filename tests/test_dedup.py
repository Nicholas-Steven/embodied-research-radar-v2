"""测试去重逻辑。"""
from schema import Paper
from dedup import deduplicate, normalize_arxiv_id, normalize_title, dedup_key


def test_normalize_arxiv_id_strips_version():
    assert normalize_arxiv_id("2401.12345v2") == "2401.12345"
    assert normalize_arxiv_id("2309.00001") == "2309.00001"
    assert normalize_arxiv_id(None) == ""


def test_normalize_title_lowers_and_strips_punct():
    n = normalize_title("Force-Aware: A New Method!")
    assert n == "force aware a new method"


def test_dedup_by_arxiv_id_version():
    p1 = Paper(paper_id="a", title="T1", arxiv_id="2401.12345v1")
    p2 = Paper(paper_id="b", title="T1", arxiv_id="2401.12345v2")  # 同一论文新版本
    result = deduplicate([p1, p2])
    assert len(result) == 1
    assert result[0].paper_id == "a"  # 保留首个


def test_dedup_by_normalized_title():
    p1 = Paper(paper_id="a", title="Force-Aware Vision Fusion", arxiv_id="2401.1v1")
    p2 = Paper(paper_id="b", title="force-aware vision fusion", arxiv_id="2401.2v1")
    result = deduplicate([p1, p2])
    assert len(result) == 1


def test_dedup_by_doi():
    p1 = Paper(paper_id="a", title="T1", doi="10.1000/xyz")
    p2 = Paper(paper_id="b", title="T2", doi="10.1000/xyz")
    result = deduplicate([p1, p2])
    assert len(result) == 1


def test_dedup_keeps_different_papers():
    p1 = Paper(paper_id="a", title="Force Fusion", arxiv_id="2401.1v1")
    p2 = Paper(paper_id="b", title="Tactile Slip", arxiv_id="2401.2v1")
    result = deduplicate([p1, p2])
    assert len(result) == 2


def test_dedup_key_handles_none_fields():
    p = Paper(paper_id="x", title="T")
    doi, aid, title = dedup_key(p)
    assert doi == ""
    assert aid == ""
    assert title == "t"
