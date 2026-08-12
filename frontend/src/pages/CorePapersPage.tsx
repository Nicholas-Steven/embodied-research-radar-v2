import { useMemo, useState } from "react";
import type { Paper } from "../types";
import type { Filters } from "../lib/filter";
import { filterPapers, sortPapers } from "../lib/filter";
import FilterSidebar from "../components/FilterSidebar";
import PaperCard from "../components/PaperCard";

export default function CorePapersPage({ papers }: { papers: Paper[] }) {
  const [filters, setFilters] = useState<Filters>({ core_only: true });

  const result = useMemo(() => {
    return sortPapers(filterPapers(papers, filters));
  }, [papers, filters]);

  return (
    <div className="layout">
      <FilterSidebar filters={filters} onChange={setFilters} papers={papers} />
      <div className="content">
        <div className="section-title">Core Papers · 核心必读</div>
        <p style={{ color: "var(--fg-soft)", marginTop: 0 }}>
          核心必读论文、高相关论文、综述、Benchmark、Baseline、值得复现论文。
        </p>
        <div className="meta-row" style={{ marginBottom: 10 }}>
          <span className="tag topic">共 {result.length} 篇</span>
        </div>
        {result.length === 0 ? (
          <div className="empty">
            暂无核心论文。当 AI 分析标记 core_candidate = Yes 时会出现在此列表。
            <div style={{ marginTop: 8, color: "var(--fg-soft)" }}>
              当前所有论文：{papers.length} 篇
            </div>
          </div>
        ) : (
          <div className="paper-list">
            {result.map((p) => (
              <PaperCard key={p.paper_id} paper={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
