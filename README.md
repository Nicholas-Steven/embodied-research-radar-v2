# Embodied Research Radar

> 面向机器人操作与具身智能的个人科研论文雷达
>
> A Personal Research Radar for Embodied Intelligence and Robotic Manipulation

每日自动抓取 arXiv 上与具身智能、机器人操作、视觉力觉融合相关的论文，经二级相关性筛选与 AI 分析后，以静态网站形式发布到 GitHub Pages。

---

## 1. 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 数据管线 | Python 3.10+ | `arxiv` / `requests` / `PyYAML` |
| AI 分析 | OpenAI 兼容协议 | DeepSeek / OpenAI / ModelScope 等 |
| 前端 | Vite + React + TypeScript | 静态构建，GitHub Pages 友好 |
| 部署 | GitHub Actions + GitHub Pages | 零服务器 |
| 测试 | pytest + `tsc --noEmit` + `vite build` | |

**为什么选这套：**
- Python 管线成熟稳定，`arxiv` 库直接对接 arXiv REST API
- Vite + React 静态构建，无需后端，GitHub Pages 原生支持
- AI Provider 抽象为 OpenAI 兼容协议，一家 API Key 即可切换主流模型
- 全部静态资源，低成本、高可维护

---

## 2. 项目目录

```
embodied-research-radar/
├── config/                    # 配置文件（YAML）
│   ├── site.yaml              # 站点与 arXiv 抓取参数
│   ├── topics.yaml            # 研究分支定义
│   ├── queries.yaml           # arXiv Query Groups
│   ├── scoring.yaml           # 相关性评分规则
│   ├── my_research.yaml       # My Research 字段配置
│   └── ai.yaml                # AI Provider 配置
├── scripts/                   # Python 数据管线
│   ├── schema.py              # 统一 Paper Schema
│   ├── config_loader.py       # 配置加载器
│   ├── arxiv_fetcher.py       # arXiv 检索与解析
│   ├── dedup.py               # 去重
│   ├── relevance.py           # 相关性筛选与评分
│   ├── ai_analyzer.py         # AI 分析模块
│   ├── utils.py               # JSONL 读写等工具
│   ├── build_data.py          # 生成前端静态数据
│   └── run_pipeline.py        # 管线主入口
├── frontend/                  # Vite + React 前端
│   ├── src/
│   │   ├── pages/             # Home / Topic / Detail / Search / Core
│   │   ├── components/        # PaperCard / FilterSidebar
│   │   ├── lib/               # api / filter
│   │   ├── data/              # topics
│   │   └── types.ts
│   ├── public/                # 构建产物 papers.json / site.json
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── tests/                     # pytest 测试
├── data/
│   ├── raw/                   # 每日原始抓取（JSONL）
│   └── processed/             # 合并库 papers.jsonl
├── docs/                      # 架构与数据说明
├── .github/workflows/         # GitHub Actions
│   ├── update-papers.yml      # 每日抓取 + AI 分析
│   └── deploy.yml             # 构建前端 + Pages 部署
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── DATA_SCHEMA.md
└── CONTRIBUTING.md
```

---

## 3. 本地启动

### 3.1 安装

```bash
# 克隆
git clone https://github.com/Nicholas-Steven/embodied-research-radar-v2.git
cd embodied-research-radar-v2

# Python 依赖
python -m venv .venv
# Windows
.venv\Scripts\activate
# Ubuntu/macOS
source .venv/bin/activate
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

### 3.2 抓取论文

```bash
# 初始化大抓取（约 300-500 篇候选）
python scripts/run_pipeline.py --init

# 每日增量抓取
python scripts/run_pipeline.py

# 跳过 AI 分析（仅元数据）
python scripts/run_pipeline.py --no-ai
```

### 3.3 AI 分析配置

```bash
cp .env.example .env
# 编辑 .env，填入 LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
```

若未配置 AI，管线仍可运行，所有 AI 字段标记为 `pending`。

### 3.4 生成前端数据

```bash
python scripts/build_data.py
# 生成 frontend/public/papers.json 与 site.json
```

### 3.5 启动前端

```bash
cd frontend
npm run dev      # 开发模式 http://localhost:5173
npm run build    # 生产构建 -> dist/
npm run preview  # 本地预览构建产物
```

---

## 4. 部署到 GitHub Pages

目标仓库：`Nicholas-Steven/embodied-research-radar-v2`
预期 URL：`https://nicholas-steven.github.io/embodied-research-radar-v2/`

### 4.1 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 添加：

| Secret | 必需 | 说明 |
|---|---|---|
| `LLM_BASE_URL` | 是* | AI API 基础 URL，例 `https://api.deepseek.com/v1` |
| `LLM_API_KEY` | 是* | AI API Key |
| `LLM_MODEL` | 是* | 模型名，例 `deepseek-chat` |

\* 若不使用 AI 分析，可不配置；管线会自动跳过 AI 步骤。

### 4.2 启用 Pages

仓库 Settings → Pages：
- Source: **GitHub Actions**

### 4.3 自动部署

推送到 `main` 分支后，`deploy.yml` 自动构建前端并部署到 Pages。
`update-papers.yml` 每天北京时间 08:00 自动抓取新论文并提交数据。

---

## 5. 测试与构建

```bash
# Python 测试
pytest tests/ -v

# 前端类型检查
cd frontend && npm run typecheck

# 前端生产构建
cd frontend && npm run build
```

---

## 6. 可扩展性

新增一个研究分支只需 3 步：
1. 在 `config/topics.yaml` 添加 topic 条目（`status: coming_soon` 或 `active`）
2. 在 `config/queries.yaml` 添加对应的 Query Group
3. 在 `frontend/src/data/topics.ts` 注册 topic 元数据

无需重构整个项目。

---

## 7. 数据来源与版权

- **数据源**：arXiv REST API（遵循 [arXiv API Terms](https://info.arxiv.org/help/api/toc.html)）
- **不抓取**付费网站全文，不违反 robots 规则
- **PDF**：仅链接到 arXiv 合法 PDF 来源，不复制论文文件
- **图片**：V1 使用占位，不抽取论文首页图片以避免版权风险

---

## 8. 已知限制

1. **AI 字段质量依赖模型**：弱模型可能产生不准确的中文摘要或方法总结
2. **arXiv rate limit**：高频率抓取可能被限流，`sleep_seconds` 已设为 4 秒
3. **初始 demo 数据**：需联网运行管线抓取真实论文，仓库本身不含论文数据
4. **图片**：V1 不显示论文图片，使用纯文本卡片
5. **付费 venue 元数据**：IEEE/Springer 等需后续集成

---

## 9. 下一步最值得增加什么

1. **OpenReview / Semantic Scholar 集成**：补全 venue 与 DOI 元数据
2. **论文图片提取**：基于 arXiv HTML 的首图机制（参考 daily-arxiv-vla）
3. **Research Map 可视化**：用 D3 / Mermaid 展示论文关系图
4. **个性化推荐**：基于用户阅读历史的相关推荐算法
5. **全文检索**：Lunr.js 或 FlexSearch 实现纯前端全文搜索
