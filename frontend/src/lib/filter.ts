import type { Paper } from "../types";

// 搜索：title / authors / abstract / abstract_zh / method / tag / arxiv_id / venue / research_topic
export function searchPapers(papers: Paper[], query: string): Paper[] {
  const q = query.trim().toLowerCase();
  if (!q) return papers;
  return papers.filter((p) => {
    const haystack = [
      p.title,
      p.abstract,
      p.abstract_zh,
      p.method_summary,
      p.summary_one_sentence,
      p.venue,
      p.arxiv_id ?? "",
      p.research_topics.join(" "),
      p.keywords.join(" "),
      p.methods.join(" "),
      p.tasks.join(" "),
      p.sensors.join(" "),
      p.authors.join(" "),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
}

// 筛选
export interface Filters {
  research_topic?: string;          // topic id
  year?: number;
  venue?: string;
  min_relevance?: number;           // 0-100
  has_code?: boolean;
  core_only?: boolean;              // core_candidate === "Yes"
  literature_category?: string;     // A/B/C/D
  sensor?: string;
}

export function filterPapers(papers: Paper[], f: Filters): Paper[] {
  return papers.filter((p) => {
    if (f.research_topic && !p.research_topics.includes(f.research_topic)) return false;
    if (f.year && p.year !== f.year) return false;
    if (f.venue && p.venue !== f.venue) return false;
    if (f.min_relevance !== undefined && p.relevance_score < f.min_relevance) return false;
    if (f.has_code && !p.code_url) return false;
    if (f.core_only && p.core_candidate !== "Yes") return false;
    if (f.literature_category && !p.literature_categories.includes(f.literature_category)) return false;
    if (f.sensor && !p.sensors.includes(f.sensor)) return false;
    return true;
  });
}

// 排序：默认相关度+日期
export function sortPapers(papers: Paper[]): Paper[] {
  return [...papers].sort(
    (a, b) => b.relevance_score - a.relevance_score || (b.published_date || "").localeCompare(a.published_date || "")
  );
}

// 提取首页科研情报模块（文档第十二节）
export function topPapers(papers: Paper[], n: number): Paper[] {
  return sortPapers(papers).slice(0, n);
}

// 潜在竞争工作：相关度 >= 85 且 vision_force topic
export function potentialCompetitions(papers: Paper[]): Paper[] {
  return papers.filter((p) => p.relevance_score >= 85 && p.research_topics.includes("vision_force"));
}

// 可借鉴方法：有 core_contributions 的相关度前 N
export function borrowableMethods(papers: Paper[], n: number): Paper[] {
  return sortPapers(papers.filter((p) => p.core_contributions.length > 0)).slice(0, n);
}

// 今日新增
export function todayNew(papers: Paper[], today: string): Paper[] {
  return papers.filter((p) => p.last_checked === today);
}
