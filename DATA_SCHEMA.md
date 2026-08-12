# 数据 Schema 说明 (DATA_SCHEMA)

## 统一 Paper Schema

所有论文遵循 `scripts/schema.py` 中定义的 `Paper` dataclass。
数据以 JSONL 格式存储（每行一篇论文），构建期合并为 `frontend/public/papers.json`。

### 字段分组

#### 1. 基础信息（事实字段，来自数据源）

| 字段 | 类型 | 说明 |
|---|---|---|
| `paper_id` | string | 内部稳定 ID（`arxiv-<arxiv_id>`） |
| `title` | string | 论文标题（英文原样保留） |
| `authors` | string[] | 作者列表（英文原样） |
| `abstract` | string | 原始英文摘要 |
| `abstract_zh` | string | AI 生成中文摘要 |
| `published_date` | string | 发表日期 ISO `YYYY-MM-DD` |
| `updated_date` | string | 更新日期 |
| `year` | int\|null | 年份 |
| `venue` | string | 发表场所，arXiv-only 默认 `Preprint / arXiv` |
| `doi` | string\|null | DOI，无则 null |
| `arxiv_id` | string\|null | arXiv ID（含版本号 `v1`） |
| `paper_url` | string | 论文主页 URL |
| `pdf_url` | string | PDF URL |
| `code_url` | string\|null | 代码仓库 URL |
| `project_url` | string\|null | 项目主页 URL |
| `image` | string\|null | 缩略图 URL（V1 用占位） |
| `source` | string | 数据来源，例 `arxiv` |
| `last_checked` | string | 最近抓取日期 |

#### 2. 分类字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `research_topics` | string[] | Research Topic ID 列表，例 `["vision_force"]` |
| `literature_categories` | string[] | Literature Category，例 `["A"]` |
| `methods` | string[] | 方法标签 |
| `tasks` | string[] | 任务标签 |
| `sensors` | string[] | 传感器标签 |
| `keywords` | string[] | 关键词标签 |

#### 3. AI 分析字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `summary_one_sentence` | string | 一句话总结 |
| `research_problem` | string | 研究问题 |
| `core_contributions` | string[] | 核心贡献（1-3 条） |
| `method_summary` | string | 方法简述 |
| `experimental_setup` | string | 实验设置 |
| `key_results` | string[] | 关键结果（只总结明确数字） |
| `limitations` | string | 局限 |
| `why_it_matters` | string | 为什么重要 |
| `why_relevant` | string | 与具身智能/视觉力觉融合研究的相关性 |
| `reproduction_value` | string | 复现价值：`High` / `Medium` / `Low` |
| `reproduction_reason` | string | 复现价值原因 |
| `core_candidate` | string | 核心候选：`Yes` / `No` / `Review` |
| `ai_status` | string | AI 状态：`pending` / `done` / `skipped` / `failed` |

#### 4. 相关性评分

| 字段 | 类型 | 说明 |
|---|---|---|
| `relevance_score` | int | 相关度评分 0-100 |
| `relevance_reason` | string | 评分解释 |
| `relevance_stars` | string | 星级字符串，例 `"★★★★☆"` |

评分规则见 `config/scoring.yaml`：
- 核心词命中（force/torque/tactile/haptic/contact/vision-force/visuotactile）：每次 +20，上限 +60
- 机器人上下文命中（robot/manipulation/grasp/assembly/...）：每次 +8，上限 +32
- 排除上下文命中（physics/material science/fluid dynamics/...）：每次 -25
- 有代码 +5
- 摘要长度合理 +3

星级映射：
- ≥85 → ★★★★★
- ≥70 → ★★★★☆
- ≥55 → ★★★☆☆
- ≥40 → ★★☆☆☆
- <40 → ★☆☆☆☆（Stage 2 剔除）

#### 5. My Research 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `related_to_my_research` | string[] | 与用户研究的关联，例 `["小论文1", "方法参考"]` |
| `why_relevant` | string | 为什么值得看 |
| `recommended_reading` | string[] | 推荐阅读重点 |
| `reproduction_value` | string | 复现价值 |
| `reproduction_reason` | string | 复现价值原因 |
| `core_candidate` | string | 核心候选 |

> **注意**：My Research 字段当前保持通用占位。
> 用户论文库 ABCD 分类体系（`config/my_research.yaml`）的真实定义待用户提供后填充。
> 文档第四节明确要求"绝对不要自行编造我的 ABCD 定义"。

## 双分类体系

文档第四节要求同时支持两套分类：

### 第一套：Research Topic
- 例：`Vision-Force`、`Vision-Tactile`、`Contact State`、`Failure Detection`
- 存储于 `paper.research_topics`（topic ID 列表）
- Topic 定义在 `config/topics.yaml`
- 前端导航与筛选基于此

### 第二套：Literature Category（ABCD）
- 例：`A`、`B`、`C`、`D`，未来可扩展 `A1`、`A2`、`B1`...
- 存储于 `paper.literature_categories`
- Category 定义在 `config/my_research.yaml`（当前为通用占位）
- 前端筛选侧栏提供 ABCD 筛选项

**两套分类不机械绑定**：一篇论文可同时属于 Research Topic `vision_force` 和 Literature Category `A`，二者独立。

## 文件存储

```
data/
├── raw/
│   └── 2026-08-12_arxiv.jsonl     # 每日原始抓取（去重前）
└── processed/
    └── papers.jsonl               # 合并库（去重+评分+AI）
```

构建期：
```
frontend/public/
├── papers.json                    # 全量论文数组
└── site.json                      # 站点元数据（last_updated/total_papers/topic_counts）
```

## 去重策略

文档第二十三节去重至少处理：
- arXiv 版本重复（`2401.12345v1` / `v2`）
- title 轻微变化
- 更新版本
- 正式论文与 arXiv 可能重复
- 同一论文多次抓取

去重键优先级：`DOI > arXiv ID（去版本号）> Normalized Title`

## AI 输出可靠性

文档第二十二节：AI 不能虚构实验数字、DOI、Venue、代码地址、作者、发表状态。

实现：
- 事实字段（`doi` / `venue` / `authors` / `code_url` / `year` / `published_date`）只从数据源写入，AI 分析不覆盖
- AI prompt 明确要求："事实字段不要编造；不确定时用 null 或空字符串"
- `venue` 仅当论文明确发表在会议/期刊时填写，否则用 `Preprint / arXiv`，绝不猜 `ICRA` / `CoRL`
- `key_results` 只总结摘要中明确出现的数字
- 若 AI 不可用：管线继续，AI 字段标记 `pending`，前端显示"AI 分析待生成"
