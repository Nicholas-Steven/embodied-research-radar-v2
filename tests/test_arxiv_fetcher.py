"""测试 arXiv XML 解析。"""
from arxiv_fetcher import parse_arxiv_xml, build_query
from dedup import normalize_arxiv_id

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345v1</id>
    <title>Force-Aware Vision Fusion for Robotic Manipulation</title>
    <summary>We propose a multimodal fusion of RGB-D vision and wrist force-torque sensing for contact-rich assembly.</summary>
    <published>2024-01-15T00:00:00Z</published>
    <updated>2024-01-16T00:00:00Z</updated>
    <author><name>Alice Chen</name></author>
    <author><name>Bob Li</name></author>
    <link rel="alternate" href="http://arxiv.org/abs/2401.12345v1"/>
    <link rel="related" href="http://arxiv.org/pdf/2401.12345v1"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2309.00001v2</id>
    <title>Tactile Slip Detection</title>
    <summary>A visuotactile approach to slip detection in peg-in-hole insertion.</summary>
    <published>2023-09-01T00:00:00Z</published>
    <updated>2023-09-05T00:00:00Z</updated>
    <author><name>Carol Wu</name></author>
    <link rel="alternate" href="http://arxiv.org/abs/2309.00001v2"/>
  </entry>
</feed>
"""


def test_parse_returns_two_papers():
    papers = parse_arxiv_xml(SAMPLE_XML)
    assert len(papers) == 2


def test_arxiv_id_extracted_without_version():
    papers = parse_arxiv_xml(SAMPLE_XML)
    assert papers[0].arxiv_id == "2401.12345v1"
    assert normalize_arxiv_id(papers[0].arxiv_id) == "2401.12345"


def test_authors_parsed():
    papers = parse_arxiv_xml(SAMPLE_XML)
    assert papers[0].authors == ["Alice Chen", "Bob Li"]


def test_dates_iso_format():
    papers = parse_arxiv_xml(SAMPLE_XML)
    assert papers[0].published_date == "2024-01-15"
    assert papers[0].year == 2024


def test_pdf_url_default():
    papers = parse_arxiv_xml(SAMPLE_XML)
    # 第二篇没有 pdf link，应回填默认
    assert papers[1].pdf_url == "http://arxiv.org/pdf/2309.00001v2"


def test_build_query_quotes_phrases():
    q = build_query(["visual force fusion", "tactile"])
    assert 'all:"visual' in q
    assert "OR" in q
