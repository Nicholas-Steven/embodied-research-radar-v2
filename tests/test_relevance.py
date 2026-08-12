"""测试相关性筛选与评分。"""
from schema import Paper
from relevance import compute_relevance, score_to_stars, filter_and_score
from config_loader import load_yaml


SCORING = load_yaml("scoring")


def make_paper(title: str, abstract: str, **kw) -> Paper:
    paper_id = kw.pop("paper_id", "x")
    return Paper(paper_id=paper_id, title=title, abstract=abstract, **kw)


def test_core_term_hit_scores_high():
    p = make_paper(
        "Vision-Force Fusion for Manipulation",
        "We fuse RGB vision with wrist force torque sensing for contact-rich robotic manipulation and grasping.",
    )
    score, reason, core, ctx = compute_relevance(p, SCORING)
    assert score >= 70
    assert "force" in [c.lower() for c in core]
    assert "manipulation" in [c.lower() for c in ctx]


def test_exclude_context_reduces_score():
    p = make_paper(
        "Force in Fluid Dynamics",
        "This paper studies force in computational fluid dynamics and material science.",
    )
    score, _, _, _ = compute_relevance(p, SCORING)
    assert score < 40  # 应被剔除


def test_score_to_stars_thresholds():
    assert score_to_stars(90, SCORING) == "★★★★★"
    assert score_to_stars(75, SCORING) == "★★★★☆"
    assert score_to_stars(60, SCORING) == "★★★☆☆"
    assert score_to_stars(45, SCORING) == "★★☆☆☆"
    assert score_to_stars(20, SCORING) == "★☆☆☆☆"


def test_filter_and_score_keeps_high_relevance():
    papers = [
        make_paper("A", "Vision force fusion robot manipulation grasping contact.", paper_id="1"),
        make_paper("B", "This is a pure physics paper about force in fluid dynamics.", paper_id="2"),
    ]
    kept = filter_and_score(papers, scoring_cfg=SCORING, pass_threshold=40)
    kept_ids = [p.paper_id for p in kept]
    assert "1" in kept_ids
    assert "2" not in kept_ids


def test_has_code_adds_bonus():
    p1 = make_paper("T", "Vision force fusion robot manipulation grasping contact.", paper_id="1")
    p2 = make_paper("T", "Vision force fusion robot manipulation grasping contact.", paper_id="2", code_url="https://github.com/x/y")
    s1, _, _, _ = compute_relevance(p1, SCORING)
    s2, _, _, _ = compute_relevance(p2, SCORING)
    assert s2 == s1 + 5  # has_code 权重
