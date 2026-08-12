import { Link } from "react-router-dom";
import type { Paper } from "../types";

function starsToScore(s: string): number | null {
  const n = (s.match(/★/g) || []).length;
  return n > 0 ? n : null;
}

export default function PaperCard({ paper }: { paper: Paper }) {
  const authors = paper.authors.slice(0, 3).join(", ") + (paper.authors.length > 3 ? " 等" : "");
  const starN = starsToScore(paper.relevance_stars);
  return (
    <div className="paper-card">
      <Link to={`/paper/${encodeURIComponent(paper.paper_id)}`} className="title">
        {paper.title}
      </Link>
      <div className="authors">{authors}</div>
      <div className="meta-row">
        <span>{paper.published_date}</span>
        <span>·</span>
        <span>{paper.venue}</span>
        {paper.year && (
          <>
            <span>·</span>
            <span>{paper.year}</span>
          </>
        )}
        <span className="score-badge">{paper.relevance_score}</span>
        {starN && <span className="stars">{paper.relevance_stars}</span>}
      </div>
      {paper.summary_one_sentence && <div className="one-line">{paper.summary_one_sentence}</div>}
      <div className="meta-row">
        {paper.research_topics.slice(0, 3).map((t) => (
          <span key={t} className="tag topic">
            {t}
          </span>
        ))}
        {paper.keywords.slice(0, 3).map((k) => (
          <span key={k} className="tag">
            {k}
          </span>
        ))}
        {paper.core_candidate === "Yes" && <span className="tag core">Core</span>}
      </div>
      <div className="card-actions">
        <Link to={`/paper/${encodeURIComponent(paper.paper_id)}`} className="btn primary">
          详细分析
        </Link>
        <a className="btn" href={paper.paper_url} target="_blank" rel="noreferrer">
          Paper
        </a>
        <a className="btn" href={paper.pdf_url} target="_blank" rel="noreferrer">
          PDF
        </a>
        {paper.code_url && (
          <a className="btn" href={paper.code_url} target="_blank" rel="noreferrer">
            Code
          </a>
        )}
      </div>
    </div>
  );
}
