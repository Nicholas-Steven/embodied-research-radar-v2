import type { Paper } from "../types";
import type { Filters } from "../lib/filter";
import { TOPICS } from "../data/topics";

const SENSORS = ["Vision", "RGB-D", "Force/Torque", "Tactile", "Proprioception"];
const CATS = ["A", "B", "C", "D"];

export default function FilterSidebar({
  filters,
  onChange,
  papers,
}: {
  filters: Filters;
  onChange: (f: Filters) => void;
  papers: Paper[];
}) {
  const years = Array.from(new Set(papers.map((p) => p.year).filter(Boolean) as number[])).sort(
    (a, b) => b - a
  );
  const venues = Array.from(new Set(papers.map((p) => p.venue).filter(Boolean))).sort();

  const update = (patch: Partial<Filters>) => onChange({ ...filters, ...patch });

  return (
    <aside className="sidebar">
      <h3>研究方向</h3>
      <select
        value={filters.research_topic ?? ""}
        onChange={(e) => update({ research_topic: e.target.value || undefined })}
      >
        <option value="">全部</option>
        {TOPICS.filter((t) => t.status === "active").map((t) => (
          <option key={t.id} value={t.id}>
            {t.name_zh}
          </option>
        ))}
      </select>

      <h3>年份</h3>
      <select
        value={filters.year ?? ""}
        onChange={(e) => update({ year: e.target.value ? Number(e.target.value) : undefined })}
      >
        <option value="">全部</option>
        {years.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>

      <h3>Venue</h3>
      <select
        value={filters.venue ?? ""}
        onChange={(e) => update({ venue: e.target.value || undefined })}
      >
        <option value="">全部</option>
        {venues.map((v) => (
          <option key={v} value={v}>
            {v}
          </option>
        ))}
      </select>

      <h3>最低相关度</h3>
      <input
        type="range"
        min={0}
        max={100}
        step={5}
        value={filters.min_relevance ?? 0}
        onChange={(e) => update({ min_relevance: Number(e.target.value) })}
      />
      <div style={{ fontSize: 12, color: "var(--fg-soft)", marginTop: 2 }}>
        ≥ {filters.min_relevance ?? 0}
      </div>

      <h3>传感器</h3>
      <select
        value={filters.sensor ?? ""}
        onChange={(e) => update({ sensor: e.target.value || undefined })}
      >
        <option value="">全部</option>
        {SENSORS.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      <h3>ABCD 分类</h3>
      <select
        value={filters.literature_category ?? ""}
        onChange={(e) => update({ literature_category: e.target.value || undefined })}
      >
        <option value="">全部</option>
        {CATS.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <h3>开关</h3>
      <label>
        <input
          type="checkbox"
          checked={!!filters.has_code}
          onChange={(e) => update({ has_code: e.target.checked || undefined })}
        />{" "}
        仅看有代码
      </label>
      <label>
        <input
          type="checkbox"
          checked={!!filters.core_only}
          onChange={(e) => update({ core_only: e.target.checked || undefined })}
        />{" "}
        仅看 Core
      </label>
    </aside>
  );
}
