# 需求词生成规则

## 目标

把本地 `models/` 中已经成熟的能力，映射成可以卖、可以搜、可以在 SEO 工具里验证的需求关键词。

默认目标不是“模型名词表”，而是“用户会搜的产品需求词”。

## 词根清洗

保留：
- 行业词：`real estate`、`resume`、`podcast`
- 任务词：`subtitle`、`invoice`、`avatar`
- 对象词：`logo`、`product photo`、`meeting notes`

删除：
- 序号、表头、空白、重复项
- 飞书界面噪声词，例如 `加载中`、`只能阅读`
- 一整句描述或备注
- 过长词组，尤其是超过 8 个英文单词的句子

## 能力族到模板的映射

常用能力族：
- 通用助手 / 自动化
- 代码生成 / Copilot
- 图像生成
- 图像编辑
- 视频生成
- 视频编辑
- 语音 / 转写 / 声音克隆
- OCR / 文档解析
- 虚拟人 / 口型同步
- 3D / SVG / Lottie

模板方向：
- `{root} ai assistant`
- `{root} copilot`
- `{root} image generator`
- `{root} photo editor`
- `{root} video generator`
- `{root} video editor`
- `{root} text to speech`
- `{root} speech to text`
- `{root} document parser`
- `{root} ocr`
- `{root} avatar generator`
- `{root} svg generator`

不要强行把每个词根套进每个能力族。模板自然度比数量更重要。

## 需求词质检

优先保留：
- 有明确动作的词：`generator`、`editor`、`assistant`、`copilot`、`parser`
- 有明确对象的词：`invoice`、`resume`、`product photo`
- 能暗示购买或试用意图的词

优先删除：
- 语义重复词
- 词序明显不自然的词
- 只有能力、没有对象的泛词
- 只适合学术搜索、不适合产品搜索的长句

## Sem 批量分析规则

进入 `批量分析` 后，不要只看输入框，必须核对结果区显示的数量。

导出前检查：
- 数据库是否正确，默认 `US`
- 行数是否达到预期
- 结果里是否包含 `搜索量 / KD / CPC / 竞争程度 / 意图`

优先导出 `CSV`，避免额外依赖。

## Markdown 交付格式

建议表头：

| 排名 | 关键词 | 词根 | 能力族 | 意图 | 搜索量 | KD | CPC | 竞争度 | 机会分 |
|---|---|---|---|---|---:|---:|---:|---:|---:|

文档开头补充：
- 分析日期
- 数据来源
- 数据库
- 关键词数量
- 机会分排序逻辑
