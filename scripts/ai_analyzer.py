"""
AI 分析模块（Provider 抽象）。

- OpenAI 兼容协议：支持 OpenAI / DeepSeek / ModelScope / Moonshot 等
- API Key 通过环境变量读取，绝不写入代码或仓库
- API 不可用时只更新元数据，AI 字段标记为 Pending，构建不崩溃
- 事实字段（doi/venue/authors/code_url 等）不由 AI 编造

每个 Paper 调用 LLM 生成结构化分析字段。
"""
from __future__ import annotations

import json
import time
from typing import Any

import requests

from schema import Paper, AI_FIELDS, FACT_FIELDS
from config_loader import ai_config

SYSTEM_PROMPT = """你是具身智能科研分析助手。分析 arXiv 论文并输出严格的 JSON。
要求：
1. 仅输出 JSON 对象，不要任何解释、Markdown 或代码块标记。
2. 事实字段（doi/venue/authors/code_url/year/publication_status/experimental_numbers）不要编造；不确定时用 null 或空字符串。
3. venue 仅当论文明确发表在会议/期刊时填写，否则用 "Preprint / arXiv"。
4. 中文分析字段使用简洁中文。
5. key_results / core_contributions 用字符串数组，每条一句话。
6. relevance_score 为 0-100 整数，relevance_reason 简短解释。
7. reproduction_value 只能是 "High" / "Medium" / "Low"。
8. core_candidate 只能是 "Yes" / "No" / "Review"。
"""

USER_TEMPLATE = """论文标题：{title}
作者：{authors}
arXiv ID：{arxiv_id}
摘要：{abstract}
当前相关度评分：{score}/100

请输出 JSON，包含以下字段：
- abstract_zh: 中文摘要（200字内）
- summary_one_sentence: 一句话总结
- research_problem: 研究问题
- core_contributions: 核心贡献（字符串数组，1-3条）
- method_summary: 方法简述
- experimental_setup: 实验设置简述
- key_results: 关键结果（字符串数组，1-3条，只总结明确数字）
- limitations: 局限
- why_it_matters: 为什么重要
- why_relevant: 与具身智能/视觉力觉融合研究的相关性
- reproduction_value: High/Medium/Low
- reproduction_reason: 复现价值原因
- core_candidate: Yes/No/Review
"""


class AIProvider:
    """OpenAI 兼容 Provider 抽象。"""

    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.base_url = cfg.get("base_url", "").rstrip("/")
        self.api_key = cfg.get("api_key", "")
        self.model = cfg.get("model", "deepseek-chat")
        self.timeout = cfg.get("timeout_seconds", 60)
        self.max_retries = cfg.get("max_retries", 3)

    def is_available(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def chat(self, system: str, user: str) -> str:
        """调用 chat/completions，返回 content 文本。"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.3,
        }
        last_err: Exception | None = None
        for _ in range(self.max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_err = e
                time.sleep(2)
        raise RuntimeError(f"AI chat failed: {last_err}")


def _parse_ai_json(content: str) -> dict[str, Any]:
    """从 LLM 输出中解析 JSON（容忍 ```json 包裹）。"""
    s = content.strip()
    if s.startswith("```"):
        # 去掉首尾代码块标记
        s = s.split("```", 2)
        if len(s) >= 2:
            s = s[1]
            if s.startswith("json"):
                s = s[4:]
        s = s.strip()
    # 找第一个 { 到最后一个 }
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        s = s[start : end + 1]
    try:
        return json.loads(s)
    except Exception:
        return {}


def analyze_paper(paper: Paper, provider: AIProvider) -> Paper:
    """对单篇论文执行 AI 分析，回填字段。
    失败时 ai_status=failed，但事实字段不变。
    """
    if not provider.is_available():
        paper.ai_status = "skipped"
        return paper

    user = USER_TEMPLATE.format(
        title=paper.title,
        authors=", ".join(paper.authors[:5]),
        arxiv_id=paper.arxiv_id or "",
        abstract=paper.abstract[:2000],
        score=paper.relevance_score,
    )
    try:
        content = provider.chat(SYSTEM_PROMPT, user)
        data = _parse_ai_json(content)
        _apply_ai_fields(paper, data)
        paper.ai_status = "done"
    except Exception as e:
        print(f"[ai] analyze failed for {paper.paper_id}: {e}")
        paper.ai_status = "failed"
    return paper


def _apply_ai_fields(paper: Paper, data: dict[str, Any]) -> None:
    """将 AI 输出回填到 Paper，且不覆盖事实字段。"""
    if not data:
        return

    def _set_str(field: str, key: str) -> None:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            setattr(paper, field, val.strip())

    def _set_list(field: str, key: str) -> None:
        val = data.get(key)
        if isinstance(val, list):
            cleaned = [str(x).strip() for x in val if str(x).strip()]
            if cleaned:
                setattr(paper, field, cleaned)

    # AI 文本字段
    for f, k in [
        ("abstract_zh", "abstract_zh"),
        ("summary_one_sentence", "summary_one_sentence"),
        ("research_problem", "research_problem"),
        ("method_summary", "method_summary"),
        ("experimental_setup", "experimental_setup"),
        ("limitations", "limitations"),
        ("why_it_matters", "why_it_matters"),
        ("why_relevant", "why_relevant"),
        ("reproduction_reason", "reproduction_reason"),
    ]:
        _set_str(f, k)

    _set_list("core_contributions", "core_contributions")
    _set_list("key_results", "key_results")

    # reproduction_value 枚举校验
    rv = data.get("reproduction_value")
    if isinstance(rv, str) and rv.strip() in ("High", "Medium", "Low"):
        paper.reproduction_value = rv.strip()

    # core_candidate 枚举校验
    cc = data.get("core_candidate")
    if isinstance(cc, str) and cc.strip() in ("Yes", "No", "Review"):
        paper.core_candidate = cc.strip()

    # AI 可重算 relevance_score（带 reason）
    rs = data.get("relevance_score")
    if isinstance(rs, int) and 0 <= rs <= 100:
        paper.relevance_score = rs
        from relevance import score_to_stars
        paper.relevance_stars = score_to_stars(rs)

    rr = data.get("relevance_reason")
    if isinstance(rr, str) and rr.strip():
        paper.relevance_reason = rr.strip()


def analyze_papers(papers: list[Paper], cfg: dict | None = None) -> list[Paper]:
    """批量分析。API 不可用时所有论文标记 skipped。"""
    acfg = cfg or ai_config()
    provider = AIProvider(acfg)

    if not provider.is_available():
        print("[ai] provider not available, skipping AI analysis")
        for p in papers:
            p.ai_status = "skipped"
        return papers

    sleep_s = 1
    for i, p in enumerate(papers):
        print(f"[ai] analyzing {i+1}/{len(papers)}: {p.paper_id}")
        analyze_paper(p, provider)
        time.sleep(sleep_s)
    return papers
