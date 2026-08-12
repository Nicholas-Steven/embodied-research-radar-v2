import type { Paper } from "../types";
import { sortPapers, topPapers, potentialCompetitions, borrowableMethods } from "../lib/filter";
import PaperCard from "../components/PaperCard";
import type { SiteMeta } from "../types";

export default function HomePage({ papers, meta }: { papers: Paper[]; meta: SiteMeta | null }) {
  const today = new Date().toISOString().slice(0, 10);
  const todayNew = papers.filter((p) => p.last_checked === today);
  const top = topPapers(papers, 5);
  const comps = potentialCompetitions(papers).slice(0, 5);
  const borrow = borrowableMethods(papers, 5);
  const sorted = sortPapers(papers);

  return (
    <div>
      <div className="meta-grid">
        <div className="meta-card">
          <div className="num">{meta?.total_papers ?? papers.length}</div>
          <div className="lbl">总论文数</div>
        </div>
        <div className="meta-card">
          <div className="num">{todayNew.length}</div>
          <div className="lbl">今日新增</div>
        </div>
        <div className="meta-card">
          <div className="num">{comps.length}</div>
          <div className="lbl">潜在竞争工作</div>
        </div>
        <div className="meta-card">
          <div className="num">{meta?.last_updated ?? "—"}</div>
          <div className="lbl">最近更新</div>
        </div>
      </div>

      <div className="section-title">今日最值得关注</div>
      {top.length === 0 ? (
        <div className="empty">暂无数据</div>
      ) : (
        <div className="paper-list">
          {top.map((p) => (
            <PaperCard key={p.paper_id} paper={p} />
          ))}
        </div>
      )}

      <div className="section-title">潜在竞争工作</div>
      {comps.length === 0 ? (
        <div className="empty">暂无高相关竞争工作（相关度 ≥ 85 且属 vision_force）</div>
      ) : (
        <div className="paper-list">
          {comps.map((p) => (
            <PaperCard key={p.paper_id} paper={p} />
          ))}
        </div>
      )}

      <div className="section-title">可以借鉴的方法</div>
      {borrow.length === 0 ? (
        <div className="empty">暂无数据</div>
      ) : (
        <div className="paper-list">
          {borrow.map((p) => (
            <PaperCard key={p.paper_id} paper={p} />
          ))}
        </div>
      )}

      <div className="section-title">最近新增高相关论文</div>
      {sorted.length === 0 ? (
        <div className="empty">暂无数据</div>
      ) : (
        <div className="paper-list">
          {sorted.slice(0, 10).map((p) => (
            <PaperCard key={p.paper_id} paper={p} />
          ))}
        </div>
      )}
    </div>
  );
}
