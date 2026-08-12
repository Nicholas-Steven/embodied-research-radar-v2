import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import type { Filters } from "../lib/filter";
import type { Paper } from "../types";
import { filterPapers, sortPapers } from "../lib/filter";
import FilterSidebar from "../components/FilterSidebar";
import PaperCard from "../components/PaperCard";
import { TOPICS } from "../data/topics";

export default function TopicPage({ papers }: { papers: Paper[] }) {
  const { id } = useParams<{ id: string }>();
  const topic = TOPICS.find((t) => t.id === id);
  const [filters, setFilters] = useState<Filters>({ research_topic: id });

  // 当路由切换时同步 research_topic
  useMemo(() => {
    setFilters((f) => ({ ...f, research_topic: id }));
  }, [id]);

  if (!topic) {
    return <div className="empty">未知研究方向：{id}</div>;
  }
  if (topic.status === "coming_soon") {
    return (
      <div className="coming-soon">
        <h2>{topic.name_en}</h2>
        <p>{topic.description_zh}</p>
        <p>该分支即将开放，敬请期待。</p>
      </div>
    );
  }

  const filtered = sortPapers(filterPapers(papers, filters));

  return (
    <div className="layout">
      <FilterSidebar filters={filters} onChange={setFilters} papers={papers} />
      <div className="content">
        <div className="section-title">{topic.name_en} · {topic.name_zh}</div>
        <p style={{ color: "var(--fg-soft)", marginTop: 0 }}>{topic.description_zh}</p>
        <div className="meta-row" style={{ marginBottom: 10 }}>
          <span className="tag topic">共 {filtered.length} 篇</span>
        </div>
        {filtered.length === 0 ? (
          <div className="empty">无符合筛选条件的论文</div>
        ) : (
          <div className="paper-list">
            {filtered.map((p) => (
              <PaperCard key={p.paper_id} paper={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
