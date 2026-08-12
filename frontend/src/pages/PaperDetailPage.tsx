import { useParams, Link } from "react-router-dom";
import type { Paper } from "../types";

export default function PaperDetailPage({ papers }: { papers: Paper[] }) {
  const { id } = useParams<{ id: string }>();
  const paper = papers.find((p) => p.paper_id === decodeURIComponent(id || ""));

  if (!paper) {
    return (
      <div className="empty">
        未找到论文：{id}
        <div style={{ marginTop: 12 }}>
          <Link to="/" className="btn primary">
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  const authors = paper.authors.join(", ");
  const aiPending = paper.ai_status === "pending" || paper.ai_status === "skipped";

  return (
    <div className="detail container" style={{ maxWidth: 920 }}>
      <div style={{ marginBottom: 8 }}>
        <Link to="/" className="btn">
          ← 返回
        </Link>
      </div>

      <h1>{paper.title}</h1>
      <div className="authors">{authors}</div>

      <div className="info-grid">
        <div><strong>Venue:</strong> {paper.venue}</div>
        <div><strong>Year:</strong> {paper.year ?? "—"}</div>
        <div><strong>Published:</strong> {paper.published_date || "—"}</div>
        <div><strong>arXiv ID:</strong> {paper.arxiv_id ?? "—"}</div>
        <div><strong>DOI:</strong> {paper.doi ?? "—"}</div>
        <div><strong>Source:</strong> {paper.source}</div>
      </div>

      <div className="meta-row" style={{ marginBottom: 14 }}>
        <span className="score-badge">{paper.relevance_score}</span>
        <span className="stars">{paper.relevance_stars}</span>
        {paper.research_topics.map((t) => (
          <span key={t} className="tag topic">{t}</span>
        ))}
        {paper.literature_categories.map((c) => (
          <span key={c} className="tag">{c}</span>
        ))}
        {paper.core_candidate === "Yes" && <span className="tag core">Core</span>}
      </div>

      <div className="card-actions" style={{ marginBottom: 18 }}>
        <a className="btn primary" href={paper.paper_url} target="_blank" rel="noreferrer">Paper</a>
        <a className="btn" href={paper.pdf_url} target="_blank" rel="noreferrer">PDF</a>
        {paper.code_url && <a className="btn" href={paper.code_url} target="_blank" rel="noreferrer">Code</a>}
        {paper.project_url && <a className="btn" href={paper.project_url} target="_blank" rel="noreferrer">Project</a>}
      </div>

      {aiPending && (
        <div className="insight-block">
          <h4>AI 分析待生成</h4>
          <div className="item">该论文的 AI 分析字段尚未生成（{paper.ai_status}）。运行 AI 分析模块后会自动填充。</div>
        </div>
      )}

      {paper.abstract && (
        <section>
          <h2>Abstract</h2>
          <div style={{ whiteSpace: "pre-wrap" }}>{paper.abstract}</div>
        </section>
      )}

      {paper.abstract_zh && (
        <section>
          <h2>中文摘要</h2>
          <div style={{ whiteSpace: "pre-wrap" }}>{paper.abstract_zh}</div>
        </section>
      )}

      {paper.summary_one_sentence && (
        <section>
          <h2>一句话总结</h2>
          <div>{paper.summary_one_sentence}</div>
        </section>
      )}

      {paper.research_problem && (
        <section>
          <h2>研究问题</h2>
          <div>{paper.research_problem}</div>
        </section>
      )}

      {paper.core_contributions.length > 0 && (
        <section>
          <h2>核心贡献</h2>
          <ul>{paper.core_contributions.map((c, i) => <li key={i}>{c}</li>)}</ul>
        </section>
      )}

      {paper.method_summary && (
        <section>
          <h2>方法</h2>
          <div>{paper.method_summary}</div>
        </section>
      )}

      {paper.experimental_setup && (
        <section>
          <h2>实验设置</h2>
          <div>{paper.experimental_setup}</div>
        </section>
      )}

      {paper.key_results.length > 0 && (
        <section>
          <h2>关键结果</h2>
          <ul>{paper.key_results.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </section>
      )}

      {paper.limitations && (
        <section>
          <h2>局限</h2>
          <div>{paper.limitations}</div>
        </section>
      )}

      {paper.why_it_matters && (
        <section>
          <h2>为什么重要</h2>
          <div>{paper.why_it_matters}</div>
        </section>
      )}

      <section>
        <h2>与我的研究关系</h2>
        {paper.related_to_my_research.length > 0 ? (
          <div className="meta-row" style={{ marginBottom: 6 }}>
            {paper.related_to_my_research.map((r) => (
              <span key={r} className="related-badge">{r}</span>
            ))}
          </div>
        ) : (
          <div style={{ color: "var(--fg-soft)" }}>待人工确认</div>
        )}
        {paper.why_relevant && <div style={{ marginTop: 6 }}>{paper.why_relevant}</div>}
      </section>

      <section>
        <h2>复现价值</h2>
        <div>
          <strong>{paper.reproduction_value || "—"}</strong>
          {paper.reproduction_reason && <span> · {paper.reproduction_reason}</span>}
        </div>
      </section>

      {paper.recommended_reading.length > 0 && (
        <section>
          <h2>推荐阅读重点</h2>
          <ul>{paper.recommended_reading.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </section>
      )}

      <section>
        <h2>相关度说明</h2>
        <div>{paper.relevance_reason}</div>
      </section>

      <section>
        <h2>分类标签</h2>
        <div className="meta-row">
          {paper.methods.map((m) => <span key={m} className="tag">{m}</span>)}
          {paper.tasks.map((t) => <span key={t} className="tag">{t}</span>)}
          {paper.sensors.map((s) => <span key={s} className="tag">{s}</span>)}
          {paper.keywords.map((k) => <span key={k} className="tag">{k}</span>)}
        </div>
      </section>

      <section>
        <h2>链接</h2>
        <div className="info-grid">
          <div><strong>Paper URL:</strong> <a href={paper.paper_url} target="_blank" rel="noreferrer">{paper.paper_url}</a></div>
          <div><strong>PDF URL:</strong> <a href={paper.pdf_url} target="_blank" rel="noreferrer">{paper.pdf_url}</a></div>
          {paper.code_url && <div><strong>Code:</strong> <a href={paper.code_url} target="_blank" rel="noreferrer">{paper.code_url}</a></div>}
          {paper.project_url && <div><strong>Project:</strong> <a href={paper.project_url} target="_blank" rel="noreferrer">{paper.project_url}</a></div>}
        </div>
      </section>

      <div style={{ color: "var(--fg-soft)", fontSize: 12, marginTop: 18 }}>
        Last checked: {paper.last_checked} · AI status: {paper.ai_status}
      </div>
    </div>
  );
}
