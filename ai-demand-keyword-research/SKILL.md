---
name: ai-demand-keyword-research
description: 从本地 models 目录提炼 AI 模型已经具备的能力，结合飞书词根表生成可落地的需求关键词，并在 sem.3ue.co 的关键词概览/批量分析中评估搜索量、关键词难度、CPC、竞争度和意图，最后输出 Markdown 机会清单。用户要求做 AI 能力盘点、需求词挖掘、关键词组合、批量关键词难度分析、SEO 选词，或明确提供 models 目录、飞书表格、sem.3ue.co 这三个输入时使用。
---

# AI 需求词研究

## 概览

按固定链路工作：
1. 读取本地 `models/` 资料，把已经成熟的 AI 能力折叠成几个可售卖的能力族。
2. 从飞书词根表提取词根，生成最多 100 个需求关键词。
3. 在 `https://sem.3ue.co/analytics/keywordoverview/` 的 `批量分析` 里跑指标。
4. 导出 `CSV`，再生成 Markdown 汇总表。

默认优先做英文关键词和 `US` 数据库，除非用户明确要求别的国家库或中文词。

## 工作流

### 1. 盘点本地模型能力

先读用户当前工作区里的 `models/` 目录，不要先凭空假设能力边界。

把大量模型名称收敛成能力族，而不是逐个模型重复罗列。优先保留这些能直接转成需求词的能力方向：
- 通用助手 / 自动化
- 代码生成 / Copilot / API 构建
- 图像生成
- 图像编辑 / 超分 / 背景移除
- 视频生成
- 视频编辑 / 延长 / 混剪
- 语音合成 / 语音转写 / 声音克隆
- 音乐 / 音效
- OCR / 文档解析
- 虚拟人 / 口型同步
- 3D / SVG / Lottie
- 视觉检测 / 图像理解 / 内容安全

优先运行内置脚本生成能力摘要和候选词：

```bash
python3 scripts/generate_keyword_seed_list.py \
  --models-dir /绝对路径/models \
  --roots-file /绝对路径/roots.txt \
  --count 100 \
  --output-prefix /绝对路径/ai-demand-keywords
```

如果用户没有准备 `roots.txt`，稍后用 `--roots-text` 直接粘贴飞书词根列。

### 2. 获取飞书词根

优先打开用户给的飞书表格并读取 `词根` 列。这个页面可能只暴露壳层，不一定稳定地暴露单元格内容，所以按下面顺序降级：

1. 先尝试直接复制词根列。
2. 如果页面快照没有单元格内容，尝试复制可见区域文本。
3. 如果仍然拿不到，要求用户提供导出的词根列文本，或让用户把词根列粘贴成纯文本。

清洗规则：
- 删除序号、表头、空行、UI 噪声词。
- 保留名词或短语词根，不保留整句解释。
- 去重，保持原始顺序。
- 词根明显是英文时，生成英文需求词；词根明显是中文时，先确认用户想跑哪个国家库。

直接把复制结果喂给脚本即可：

```bash
python3 scripts/generate_keyword_seed_list.py \
  --models-dir /绝对路径/models \
  --roots-text "$(pbpaste)" \
  --count 100 \
  --output-prefix /绝对路径/ai-demand-keywords
```

### 3. 生成需求关键词

脚本会输出三份文件：
- `*-capabilities.md`: 从 `models/` 提炼出的能力摘要。
- `*-seeds.csv`: 候选关键词及其词根、能力族、模板。
- `*-seeds.txt`: 纯关键词列表，适合直接粘到 `sem.3ue.co`。

生成后必须人工过一遍，只保留“像真实用户会搜的词”。

重点删掉这些坏词：
- 过于空泛的词，比如只有一个泛词根，没有动作和场景。
- 品牌词或明显侵权词，除非用户明确要做竞品词。
- 语法不通顺的组合词。
- 同义重复词，只保留一个主写法。

目标是得到恰好 `100` 个关键词。如果第一次生成不满 100 个，就补充更多词根；如果超过 100 个，就优先保留交易意图更强、表达更自然的词。

### 4. 在 sem.3ue.co 批量分析

打开用户给的页面：

`https://sem.3ue.co/analytics/keywordoverview/?fid=11102252&__gmitm=...`

使用顺序固定：
1. 进入 `关键词概览`。
2. 切到 `批量分析`。
3. 选择数据库，默认 `US`。
4. 粘贴 `*-seeds.txt` 里的 100 个词。
5. 点击 `分析`。
6. 检查页面标题区下方是否显示 `批量分析 N 个关键词`，确认 `N = 100` 再继续。
7. 通过 `导出 -> CSV` 导出结果。

注意：
- 页面支持最多 `100` 个关键词。
- 页面有时不会把粘贴框中的全部关键词送进结果表，必须以结果区显示的 `N` 为准，不要以输入框内容自我安慰。
- 如果只分析了部分关键词，优先重新发送缺失关键词，再导出。
- 默认先导出 `CSV`，不要优先导出 `XLSX`，这样可以避免额外依赖。

### 5. 生成 Markdown 汇总

拿到导出的 `CSV` 后，运行：

```bash
python3 scripts/sem_export_to_markdown.py \
  --input /绝对路径/sem-export.csv \
  --seed-csv /绝对路径/ai-demand-keywords-seeds.csv \
  --top 100 \
  --output /绝对路径/ai-demand-keywords-report.md
```

脚本会输出：
- 汇总说明
- 平均搜索量、平均 KD、平均 CPC、低难度词数量等统计
- 按 `机会分` 排序的 Markdown 表格

### 6. 交付前质检

最终 Markdown 至少要满足：
- 明确写出分析日期。
- 明确写出数据库，例如 `US`。
- 表格行数为 `100`，除非 `sem.3ue.co` 实际只返回更少的结果，此时要在文档里解释缺口。
- 至少包含 `关键词 / 词根 / 能力族 / 意图 / 搜索量 / KD / CPC / 竞争度 / 机会分`。
- 如果脚本没能从导出里读到某列，要在文档中注明缺失列，而不是默默省略。

## 常用命令

### 生成候选词

```bash
python3 scripts/generate_keyword_seed_list.py \
  --models-dir /绝对路径/models \
  --roots-file /绝对路径/roots.txt \
  --count 100 \
  --output-prefix /绝对路径/ai-demand-keywords
```

### 把 Sem 导出转成 Markdown

```bash
python3 scripts/sem_export_to_markdown.py \
  --input /绝对路径/sem-export.csv \
  --seed-csv /绝对路径/ai-demand-keywords-seeds.csv \
  --output /绝对路径/ai-demand-keywords-report.md
```

## 参考文件

- `references/keyword-rules.md`: 词根清洗、模板策略、手工质检规则。
- `scripts/generate_keyword_seed_list.py`: 能力摘要和关键词候选生成。
- `scripts/sem_export_to_markdown.py`: 读取 Sem 导出并生成最终 Markdown。
