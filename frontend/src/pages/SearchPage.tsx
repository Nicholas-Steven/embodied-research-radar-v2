import { useMemo, useState } from "react";
import type { Paper } from "../types";
import type { Filters } from "../lib/filter";
import { searchPapers, filterPapers, sortPapers } from "../lib/filter";
import FilterSidebar from "../components/FilterSidebar";
import PaperCard from "../components/PaperCard";

export default function SearchPage({ papers }: { papers: Paper[] }) {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Filters>({});

  const result = useMemo(() => {
    const searched = searchPapers(papers, query);
    const filtered = filterPapers(searched, filters);
    return sortPapers(filtered);
  }, [papers, query, filters]);

  return (
    <div className="layout">
      <FilterSidebar filters={filters} onChange={setFilters} papers={papers} />
      <div className="content">
        <div className="section-title">搜索</div>
        <div className="search-bar">
          <input
            type="search"
            placeholder="搜索 标题 / 作者 / 摘要 / 中文摘要 / 方法 / arXiv ID / Venue / Research Topic ..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="meta-row" style={{ marginBottom: 10 }}>
          <span className="tag topic">命中 {result.length} 篇</span>
        </div>
        {result.length === 0 ? (
          <div className="empty">无匹配论文</div>
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
