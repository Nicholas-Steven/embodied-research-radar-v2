import { useEffect, useState } from "react";
import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import { TOPICS, ACTIVE_TOPIC } from "./data/topics";
import { fetchPapers, fetchSiteMeta } from "./lib/api";
import type { Paper, SiteMeta } from "./types";
import HomePage from "./pages/HomePage";
import TopicPage from "./pages/TopicPage";
import PaperDetailPage from "./pages/PaperDetailPage";
import SearchPage from "./pages/SearchPage";
import CorePapersPage from "./pages/CorePapersPage";
import ComingSoonPage from "./pages/ComingSoonPage";

function useTheme() {
  const [dark, setDark] = useState<boolean>(() => {
    const s = localStorage.getItem("theme");
    if (s === "light") return false;
    return true;
  });
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-theme", dark ? "dark" : "light");
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);
  return { dark, toggle: () => setDark((d) => !d) };
}

export default function App() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [meta, setMeta] = useState<SiteMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { dark, toggle } = useTheme();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [ps, m] = await Promise.all([fetchPapers(), fetchSiteMeta()]);
        if (cancelled) return;
        setPapers(ps);
        setMeta(m);
      } catch (e: any) {
        setError(e?.message ?? "load failed");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <div className="empty">加载论文数据中…</div>;
  }
  if (error) {
    return <div className="load-error">数据加载失败：{error}</div>;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          Embodied Research Radar V2 <small>具身智能科研雷达</small>
        </div>
        <nav className="nav">
          <NavLink to="/">今日雷达</NavLink>
          {TOPICS.map((t) => (
            <NavLink key={t.id} to={`/topic/${t.id}`}>
              {t.nav_label}
            </NavLink>
          ))}
          <NavLink to="/core">Core Papers</NavLink>
          <NavLink to="/search">搜索</NavLink>
        </nav>
        <button className="theme-toggle" onClick={toggle}>
          {dark ? "☀ 浅色" : "🌙 深色"}
        </button>
      </header>

      <div className="container">
        <Routes>
          <Route path="/" element={<HomePage papers={papers} meta={meta} />} />
          <Route path="/topic/:id" element={<TopicPage papers={papers} />} />
          <Route path="/paper/:id" element={<PaperDetailPage papers={papers} />} />
          <Route path="/core" element={<CorePapersPage papers={papers} />} />
          <Route path="/search" element={<SearchPage papers={papers} />} />
          <Route path="/coming-soon" element={<ComingSoonPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      <footer className="footer">
        Embodied Research Radar V2 · 数据来源 arXiv ·{" "}
        最近更新 {meta?.last_updated ?? "—"} · 共 {papers.length} 篇
      </footer>
    </div>
  );
}
