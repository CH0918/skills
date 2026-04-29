# Demand Find Report

Date: 2026-03-22
Database: Semrush US
Sources:
- `./.codex/skills/demand-find/references/root-words.md`
- `./.codex/skills/demand-find/references/model-to-saas.md`
- `https://sem.3ue.co/analytics/keywordoverview/?fid=11102252&__gmitm=ayWzA3*l4EVcTpZei43sW*qRvljSdU`

## 方法

先用词根资料筛出适合做工具站和 SaaS 的英文需求词，再按当前模型能力做能力映射：

- `OpenRouter`: 助手、Agent、RAG、代码、总结、结构化提取
- `fal.ai`: 图像、视频、TTS、配音、媒体工作流
- `Replicate`: OCR、文档解析、转录、检测、长尾媒体工具

随后在 Semrush 的 `关键词概览 -> 批量分析` 里一次性跑了 100 个英文需求词，重点看：

- Search Volume
- KD
- CPC
- Competition
- Intent
- 是否和现有模型能力强匹配

筛选原则不是单纯追高搜索量，而是优先找：

1. 真实可做
2. 有明确使用场景
3. SEO 还有切入口
4. 有付费意图或 B2B 采购信号

## Top 10 机会词

| Rank | Keyword | Volume | KD | CPC | Intent | Build Difficulty | Why it made the list |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | `customer service chatbot` | 1,900 | 53 | 14.87 | Commercial | Medium | 采购意图强，CPC 很高，`OpenRouter + RAG` 就能快速做出能卖的版本。 |
| 2 | `youtube transcript generator` | 22,200 | 66 | 0.73 | Commercial | Low-Medium | 搜索量足够大，需求明确，`ASR + transcript formatting` 非常直接。 |
| 3 | `chart maker` | 8,100 | 47 | 1.86 | Commercial | Medium | KD 相对可控，适合用 `LLM -> chart spec -> render/export` 做工具站。 |
| 4 | `resume parser` | 1,000 | 39 | 2.36 | Informational | Medium | HR/B2B 场景稳定，`OCR + extraction + field mapping` 已经成熟。 |
| 5 | `text to speech api` | 880 | 49 | 5.11 | Commercial | Medium | API 型需求，CPC 不低，容易做成开发者产品或嵌入能力。 |
| 6 | `job description generator` | 720 | 33 | 3.07 | Commercial | Low | SEO 难度低，商业意图明确，落地极快，适合从模板化工具切入。 |
| 7 | `podcast transcription` | 590 | 29 | 1.80 | Commercial | Low-Medium | KD 很友好，问题明确，`ASR + speaker split + summary` 足够形成产品。 |
| 8 | `pdf data extractor` | 260 | 38 | 5.57 | Informational | Medium | B2B 文档自动化场景，虽然量不大，但质量高、付费更稳。 |
| 9 | `invoice parser` | 110 | 2 | 15.48 | Commercial | Medium | 超低 KD + 超高 CPC，量小但很有 B2B 价值，适合打垂直行业。 |
| 10 | `video summarizer` | 14,800 | 64 | 0.39 | Informational | Medium | 搜索量大，做法清晰，适合走 `video transcript + summary + highlights`。 |

## Top 10 详细判断

### 1. `customer service chatbot`

- 解决问题: 企业希望把 FAQ、产品文档、订单/售后流程接进一个可部署的客服机器人。
- 为什么值得做: `Volume 1,900 / KD 53 / CPC 14.87`，不是超大词，但采购意图非常强。
- 适合的能力栈: `OpenRouter + RAG + workflow + handoff to human`
- 实现难度: 中
- 备注: 适合先做垂直版本，比如 SaaS onboarding、Shopify 店铺客服、B2B 软件文档问答。

### 2. `youtube transcript generator`

- 解决问题: 用户想把视频快速转文字，用于学习、二次创作、SEO、笔记。
- 为什么值得做: `Volume 22,200 / KD 66 / CPC 0.73`，需求很直白，做对体验就有切口。
- 适合的能力栈: `Replicate/fal.ai ASR + OpenRouter summary/extract`
- 实现难度: 低到中
- 备注: 可以继续往 `chaptering / highlights / multilingual transcript / export to notion` 延展。

### 3. `chart maker`

- 解决问题: 用户输入数据或一句话需求，自动生成图表并导出。
- 为什么值得做: `Volume 8,100 / KD 47 / CPC 1.86`，需求广，KD 也比纯红海词好。
- 适合的能力栈: `OpenRouter` 负责把自然语言转图表配置，前端负责渲染。
- 实现难度: 中
- 备注: 更好的切法不是“通用图表站”，而是 `marketing report chart maker`、`investor update chart maker`、`classroom chart maker`。

### 4. `resume parser`

- 解决问题: 招聘、HR、猎头需要把简历自动抽成结构化字段。
- 为什么值得做: `Volume 1,000 / KD 39 / CPC 2.36`，体量不算小，B2B 指向很明确。
- 适合的能力栈: `OCR + layout understanding + LLM field normalization`
- 实现难度: 中
- 备注: 很适合做 API、ATS 插件或 Chrome 扩展。

### 5. `text to speech api`

- 解决问题: 开发者和企业需要稳定的语音合成接口。
- 为什么值得做: `Volume 880 / KD 49 / CPC 5.11`，比纯 consumer 工具更容易收费。
- 适合的能力栈: `fal.ai / Replicate TTS + usage metering + API docs`
- 实现难度: 中
- 备注: 如果做，最好别只卖“API”，而是配 `voice presets / latency / dubbing / webhook`。

### 6. `job description generator`

- 解决问题: HR 和招聘经理需要快速生成岗位 JD、版本对比、改写和结构化输出。
- 为什么值得做: `Volume 720 / KD 33 / CPC 3.07`，SEO 进入难度低，工具站很容易起量。
- 适合的能力栈: `OpenRouter + templates + recruiter-specific prompting`
- 实现难度: 低
- 备注: 可以做成一个围绕招聘文档的整套工具，而不是单点生成。

### 7. `podcast transcription`

- 解决问题: 播客制作者需要把音频转文字，进一步做摘要、标题、show notes、短视频切片。
- 为什么值得做: `Volume 590 / KD 29 / CPC 1.80`，KD 低，问题稳定，容易把 ARPU 拉起来。
- 适合的能力栈: `ASR + speaker diarization + OpenRouter summarization`
- 实现难度: 低到中
- 备注: 如果加上 `podcast to blog / podcast to clips / podcast SEO`，产品会更完整。

### 8. `pdf data extractor`

- 解决问题: 从 PDF 里提取表格、字段、票据或合同信息。
- 为什么值得做: `Volume 260 / KD 38 / CPC 5.57`，典型低流量高价值 B2B 词。
- 适合的能力栈: `OCR + layout parser + field schema mapping`
- 实现难度: 中
- 备注: 适合垂直切票据、银行流水、采购单、 shipping docs。

### 9. `invoice parser`

- 解决问题: 财务、AP automation、ERP 流程里把发票转结构化数据。
- 为什么值得做: `Volume 110 / KD 2 / CPC 15.48`，量不大但信号极强。
- 适合的能力栈: `OCR + document extraction + validation rules`
- 实现难度: 中
- 备注: 这是标准的 B2B 小词大钱机会，SEO 可以吃到非常精准的买家流量。

### 10. `video summarizer`

- 解决问题: 用户希望快速看懂长视频，不想完整看完。
- 为什么值得做: `Volume 14,800 / KD 64 / CPC 0.39`，量大，需求明确，技术路径成熟。
- 适合的能力栈: `video/audio transcript + OpenRouter summary + chapter extraction`
- 实现难度: 中
- 备注: 可延伸到会议录屏、课程视频、播客视频、YouTube 批量摘要。

## 高搜索量但我不建议优先做的词

| Keyword | Volume | KD | Why not first |
| --- | ---: | ---: | --- |
| `background remover` | 1,000,000 | 100 | 需求太大但 SEO 太红海，免费工具和大站挤满。 |
| `resume builder` | 301,000 | 98 | 强品类但已被大品牌长期占据，SEO 成本很高。 |
| `logo maker` | 201,000 | 100 | 红海中的红海，做得出来不代表能拿到流量。 |
| `ai video generator` | 165,000 | 88 | 大词，但获客和供给都被头部品牌教育过，后进难度高。 |
| `paraphrasing tool` | 135,000 | 81 | 典型红海工具词，很难建立差异化。 |
| `contract review ai` | 480 | 56 | CPC 很强，但需要更高的准确性、法务信任和场景深度。 |
| `speech to text api` | 720 | 70 | 商业价值强，但开发者 API 竞争更集中。 |
| `face swap video` | 9,900 | 51 | 量不错，但内容安全、平台审核和合规负担更重。 |

## 更适合继续观察的词

- `ocr api`: `390 / KD 53 / CPC 5.23`
- `study guide generator`: `1,300 / KD 20 / CPC 1.16`
- `worksheet generator`: `1,900 / KD 45 / CPC 0.74`
- `sql query generator`: `110 / KD 24 / CPC 3.60`
- `ad copy generator`: `320 / KD 44 / CPC 8.71`
- `customer support ai`: `720 / KD 81 / CPC 27.81`
- `video translator`: `8,100 / KD 65 / CPC 1.19`
- `image to video ai`: `27,100 / KD 60 / CPC 0.70`

## 100 个英文需求词清单

1. `background remover`
2. `object remover`
3. `watermark remover`
4. `image upscaler`
5. `photo enhancer`
6. `old photo restoration`
7. `ai headshot generator`
8. `headshot generator`
9. `ai avatar generator`
10. `profile picture maker`
11. `logo generator`
12. `logo maker`
13. `icon generator`
14. `product photo generator`
15. `ai product photo generator`
16. `ai poster generator`
17. `ai tattoo generator`
18. `coloring page generator`
19. `ai cartoon generator`
20. `anime avatar generator`
21. `ai interior design`
22. `floor plan generator`
23. `diagram generator`
24. `flow chart generator`
25. `chart maker`
26. `infographic generator`
27. `ai image editor`
28. `text summarizer`
29. `pdf summarizer`
30. `youtube summarizer`
31. `video summarizer`
32. `research paper summarizer`
33. `meeting notes ai`
34. `research assistant ai`
35. `ai writing assistant`
36. `paraphrasing tool`
37. `grammar checker ai`
38. `citation generator`
39. `resume builder`
40. `cover letter generator`
41. `job description generator`
42. `lesson plan generator`
43. `quiz generator`
44. `worksheet generator`
45. `flashcard generator`
46. `study guide generator`
47. `ocr api`
48. `image to text converter`
49. `pdf data extractor`
50. `invoice parser`
51. `receipt scanner`
52. `resume parser`
53. `contract review ai`
54. `table extraction from pdf`
55. `screenshot to text`
56. `document parser ai`
57. `chatbot builder`
58. `customer support ai`
59. `knowledge base ai`
60. `sales assistant ai`
61. `email assistant ai`
62. `coding assistant ai`
63. `sql query generator`
64. `api builder ai`
65. `workflow builder ai`
66. `app builder ai`
67. `website builder ai`
68. `landing page builder ai`
69. `dashboard builder ai`
70. `form builder ai`
71. `proposal generator ai`
72. `seo content generator`
73. `ad copy generator`
74. `customer service chatbot`
75. `agent builder ai`
76. `ai video generator`
77. `text to video ai`
78. `image to video ai`
79. `product video generator`
80. `ai video editor`
81. `video translator`
82. `video dubbing ai`
83. `lip sync video`
84. `face swap video`
85. `subtitle generator`
86. `ai subtitle generator`
87. `video caption generator`
88. `youtube transcript generator`
89. `audio to text`
90. `speech to text api`
91. `voice changer`
92. `ai voice generator`
93. `voice cloning ai`
94. `text to speech api`
95. `podcast transcription`
96. `interview transcription`
97. `meeting transcription`
98. `audio enhancer`
99. `noise remover audio`
100. `ai music generator`

## 一句话结论

如果只做一个方向，优先做 `customer service chatbot` 或 `youtube transcript generator`。

- 前者更偏 B2B，高客单价，更容易卖。
- 后者更偏 SEO 工具站，流量空间更大，起步更快。

如果想做低流量高价值的垂直 SaaS，优先看：

- `invoice parser`
- `pdf data extractor`
- `resume parser`
- `text to speech api`
