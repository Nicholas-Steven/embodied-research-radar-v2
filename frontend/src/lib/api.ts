import type { Paper, SiteMeta } from "../types";

// 数据文件由 build 时从 data/processed/papers.jsonl 生成
// (scripts/build_data.py -> frontend/public/papers.json, site.json)
const BASE = import.meta.env.BASE_URL;

export async function fetchPapers(): Promise<Paper[]> {
  try {
    const resp = await fetch(`${BASE}papers.json`);
    if (!resp.ok) return [];
    return await resp.json();
  } catch {
    return [];
  }
}

export async function fetchSiteMeta(): Promise<SiteMeta | null> {
  try {
    const resp = await fetch(`${BASE}site.json`);
    if (!resp.ok) return null;
    return await resp.json();
  } catch {
    return null;
  }
}
