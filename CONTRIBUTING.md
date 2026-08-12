# 维护说明 (CONTRIBUTING)

本项目是个人科研工具，维护以单人为主，但代码结构与文档支持后续扩展。

## 日常维护流程

### 1. 每日自动更新（无需手动）

GitHub Actions `update-papers.yml` 每天 UTC 00:00（北京时间 08:00）自动：
1. 抓取 arXiv 新论文
2. 去重 + 相关性评分
3. AI 分析（若配置了 `LLM_API_KEY`）
4. 提交数据更新到仓库
5. 触发 `deploy.yml` 重新部署网站

### 2. 手动触发更新

GitHub 仓库 → Actions → `Update Papers` → `Run workflow`：
- `init`：初始化大抓取（约 300-500 篇候选）
- `no_ai`：跳过 AI 分析（仅更新元数据）

### 3. 本地开发

```bash
# Python 管线
source .venv/bin/activate
python scripts/run_pipeline.py --no-ai   # 不耗 AI 额度
pytest tests/ -v                          # 跑测试

# 前端
cd frontend
npm run dev       # 开发服务器
npm run typecheck # 类型检查
npm run build     # 生产构建
```

## 新增研究分支

文档第三十三节要求配置化。新增分支步骤：

1. **`config/topics.yaml`**：添加 topic 条目
   ```yaml
   - id: "active_perception"
     name_zh: "主动感知"
     name_en: "Active Perception"
     status: "coming_soon"   # 或 active
     keywords: [...]
   ```

2. **`config/queries.yaml`**：添加对应 Query Group
   ```yaml
   query_groups:
     active_perception:
       - "active perception robot"
       - "next-best-view manipulation"
   group_topic_map:
     active_perception: "active_perception"
   ```

3. **`frontend/src/data/topics.ts`**：注册 topic 元数据

无需修改管线核心代码或前端路由。

## 修改相关性评分

编辑 `config/scoring.yaml`：
- 调整 `weights` 中的权重
- 增删 `core_terms` / `robot_context_terms` / `exclude_context_terms`
- 修改 `pass_threshold`（默认 40）

## 切换 AI Provider

编辑 `.env`（本地）或 GitHub Secrets（CI）：

```bash
# DeepSeek
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# OpenAI
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# ModelScope
LLM_BASE_URL=https://api-inference.modelscope.cn/v1/
LLM_MODEL=deepseek-ai/DeepSeek-V3.2
```

所有 Provider 走 OpenAI 兼容协议，切换只需改环境变量。

## 测试

```bash
# 全部 Python 测试
pytest tests/ -v

# 单个测试文件
pytest tests/test_relevance.py -v

# 前端
cd frontend && npm run typecheck && npm run build
```

测试覆盖：
- `test_schema.py`：统一 Paper Schema 字段完整性
- `test_arxiv_fetcher.py`：arXiv XML 解析、Query 构建
- `test_dedup.py`：DOI / arXiv ID / Title 去重
- `test_relevance.py`：相关性评分、排除上下文、Stage 2 筛选
- `test_utils.py`：JSONL 读写、合并、日期

## 添加测试

新功能需配套测试。测试文件放 `tests/test_<module>.py`，遵循现有命名约定。

## 填充真实 ABCD 定义

文档第四节：当前 `config/my_research.yaml` 中 ABCD 为通用占位。
用户提供真实定义后，编辑该文件：

```yaml
literature_categories:
  A:
    description: "视觉力觉融合核心方法"
    color: "#e74c3c"
  B:
    description: "..."
  ...
```

并在 `scripts/run_pipeline.py` 或新增的 `scripts/classify.py` 中实现自动分类逻辑。

## 部署验证

部署后访问 `https://nicholas-steven.github.io/embodied-research-radar-v2/` 验证：
- 首页今日雷达加载
- Vision-Force 分支论文列表显示
- 单篇论文详情页可访问
- 搜索与筛选功能正常
- 深色/浅色主题切换正常

## 常见问题

### Q: 抓取被 arXiv 限流？
A: 调大 `config/site.yaml` 中的 `sleep_seconds`（默认 4 秒）。arXiv 建议 ≥3 秒间隔。

### Q: AI 分析失败但管线中断？
A: 不会。`ai_analyzer.py` 捕获所有异常，标记 `ai_status=failed`，管线继续。

### Q: 如何回滚某天的数据更新？
A: `data/processed/papers.jsonl` 在 git 中有历史，`git checkout <commit> -- data/processed/papers.jsonl` 即可恢复。

### Q: 前端部署后白屏？
A: 检查 `vite.config.ts` 的 `base` 是否匹配 GitHub Pages 路径；检查浏览器控制台是否有资源 404。
