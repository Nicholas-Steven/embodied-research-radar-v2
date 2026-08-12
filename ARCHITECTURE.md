# 架构说明 (ARCHITECTURE)

## 总体架构

```
┌─────────────────────────────────────────────────────┐
│  GitHub Actions (每日 UTC 00:00)                    │
│  update-papers.yml                                  │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  Python 数据管线 (scripts/)                         │
│                                                     │
│  run_pipeline.py                                    │
│    ├─ arxiv_fetcher.py   → arXiv REST API 检索      │
│    ├─ dedup.py            → DOI/arXiv ID/Title 去重 │
│    ├─ relevance.py        → 相关性评分 (0-100)     │
│    ├─ ai_analyzer.py       → OpenAI 兼容 AI 分析   │
│    └─ utils.py            → JSONL 读写              │
│                                                     │
│  config/*.yaml         → 配置驱动 (Topics/Queries) │
│  schema.py             → 统一 Paper Schema          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  数据层 (data/)                                     │
│                                                     │
│  raw/<date>_arxiv.jsonl     → 每日原始抓取           │
│  processed/papers.jsonl     → 合并库（去重+评分+AI）│
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  构建期数据生成 (scripts/build_data.py)             │
│                                                     │
│  papers.jsonl  ──►  frontend/public/papers.json     │
│                      frontend/public/site.json      │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  前端 (frontend/)  Vite + React + TypeScript        │
│                                                     │
│  App.tsx                → 路由 + 数据加载            │
│  pages/                                            │
│    ├─ HomePage           → 今日雷达 + 科研情报      │
│    ├─ TopicPage          → 各研究分支论文列表       │
│    ├─ PaperDetailPage    → 单篇论文详情             │
│    ├─ SearchPage         → 搜索                     │
│    ├─ CorePapersPage     → 核心必读                 │
│    └─ ComingSoonPage     → 占位                     │
│  components/                                       │
│    ├─ PaperCard          → 列表卡片                 │
│    └─ FilterSidebar      → 筛选侧栏                 │
│  lib/                                              │
│    ├─ api.ts             → fetch papers.json        │
│    └─ filter.ts          → 搜索/筛选/排序           │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│  GitHub Pages 部署 (deploy.yml)                     │
│                                                     │
│  npm run build → frontend/dist/ → upload-pages     │
│  → https://nicholas-steven.github.io/              │
│    embodied-research-radar-v2/                     │
└─────────────────────────────────────────────────────┘
```

## 关键设计决策

### 1. 为什么用 Python 管线 + Vite 静态前端，而非全栈框架？

- **零服务器**：GitHub Pages 只托管静态文件，无需 Node/Python 后端
- **解耦**：数据管线与前端完全独立，管线更新数据 → 前端读 JSON
- **低成本维护**：Python 管线 < 1000 行，前端 < 10 个组件

### 2. 为什么用 JSONL 而非 SQLite？

- 文档第十九节要求"数据层与 UI 解耦"，JSONL 是最简单的可读格式
- 管线产出直接可 `git diff` 审查，SQLite 是二进制无法审查
- 规模小（数百到数千篇），JSONL 足够；如需复杂查询可后续引入 SQLite

### 3. 为什么 AI Provider 抽象为 OpenAI 兼容协议？

- 主流模型（OpenAI / DeepSeek / ModelScope / Moonshot / Together）均兼容此协议
- 一套 `chat/completions` 接口即可切换 provider，无需为每家写 SDK
- 通过环境变量读取 Key，绝不写入代码或仓库（文档第二十六节）

### 4. 为什么相关性评分用规则而非 AI？

- **可解释**：评分由关键词命中+上下文校验组成，每篇有 `relevance_reason` 解释
- **稳定**：AI 评分可能因 prompt 波动产生不一致结果
- **省成本**：评分在 AI 分析之前完成，AI 只对已筛选的高相关论文做深度分析

### 5. 为什么前端路由用 BrowserRouter + basename？

- GitHub Pages project site 是二级目录 `/embodied-research-radar-v2/`
- `BrowserRouter basename={import.meta.env.BASE_URL}` 自动适配 base path
- 避免使用 HashRouter 的 `#` URL，更符合现代 SEO 与分享需求

### 6. 为什么 V1 不抓论文图片？

- 文档第三十五节明确：宁可使用占位，不增加版权风险
- daily-arxiv-vla 的 Playwright 兜底机制复杂度高，V1 优先保证管线稳定
- 图片可作为后续迭代项

## 数据流时序

```
T+0    update-papers.yml 触发 (cron 或 dispatch)
T+0    Python 管线启动
T+1    arXiv 检索 (5 个 Query Group，每组间隔 4 秒)
T+3    去重 + 相关性评分
T+4    AI 分析 (若配置了 LLM_API_KEY)
T+8    写入 papers.jsonl
T+9    build_data.py 生成 papers.json / site.json
T+10   git commit + push 数据更新
T+11   deploy.yml 触发 (push to main)
T+12   npm install + tsc --noEmit + vite build
T+13   upload-pages-artifact + deploy-pages
T+14   网站更新完成
```

## 错误处理与降级

| 故障点 | 降级策略 |
|---|---|
| arXiv API 超时 | 重试 3 次，失败则跳过该 Query Group |
| AI API 不可用 | 管线继续，AI 字段标记 `pending`，前端显示"AI 分析待生成" |
| AI 返回非 JSON | `_parse_ai_json` 容错解析，失败则 `ai_status=failed` |
| papers.json 加载失败 | 前端显示"数据加载失败"，不崩溃 |
| 前端构建类型错误 | `deploy.yml` 中 `npm run typecheck` 先行，失败则阻断部署 |

## 扩展点

1. **新增研究分支**：`config/topics.yaml` + `config/queries.yaml` + `frontend/src/data/topics.ts`
2. **新增数据源**：在 `scripts/` 添加 `openreview_fetcher.py` 等，复用 `Paper` Schema
3. **新增 AI Provider**：在 `ai_analyzer.py` 的 `AIProvider` 添加新协议适配
4. **新增前端页面**：在 `frontend/src/pages/` 添加，并在 `App.tsx` 注册路由
