// Paper 类型定义（与 scripts/schema.py 的 Paper dataclass 对应）

export interface Paper {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  abstract_zh: string;
  published_date: string;
  updated_date: string;
  year: number | null;
  venue: string;
  doi: string | null;
  arxiv_id: string | null;
  paper_url: string;
  pdf_url: string;
  code_url: string | null;
  project_url: string | null;
  image: string | null;
  research_topics: string[];
  literature_categories: string[];
  methods: string[];
  tasks: string[];
  sensors: string[];
  keywords: string[];
  summary_one_sentence: string;
  research_problem: string;
  core_contributions: string[];
  method_summary: string;
  experimental_setup: string;
  key_results: string[];
  limitations: string;
  why_it_matters: string;
  relevance_score: number;
  relevance_reason: string;
  relevance_stars: string;
  related_to_my_research: string[];
  why_relevant: string;
  recommended_reading: string[];
  reproduction_value: string;
  reproduction_reason: string;
  core_candidate: string;
  source: string;
  last_checked: string;
  ai_status: string;
}

export interface SiteMeta {
  last_updated: string;
  total_papers: number;
  topic_counts: Record<string, number>;
}
