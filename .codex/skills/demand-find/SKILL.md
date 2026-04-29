---
name: demand-find
description: 根据现有的模型平台能力，结合词根，找出可以做的100个需求词（英文），去 semrush平台 `https://sem.3ue.co/analytics/keywordoverview/?fid=11102252&__gmitm=ayWzA3*l4EVcTpZei43sW*qRvljSdU` 批量查询(关键词+换行的格式可以输入多个关键词批量查询)关键词难度、搜索量等信息 ，查出来之后，结合搜索量、关键词难度，实现难度等维度综合跳出十个可以做需求，汇总到一个 markdown 中给我
---

## 步骤说明

1. 查阅 `references/root-words.md` 和 `/references/model-to-saas.md` 确认可做的需求词
2. 用 chrome-dev-tools 打开`https://sem.3ue.co/analytics/keywordoverview/?fid=11102252&__gmitm=ayWzA3*l4EVcTpZei43sW*qRvljSdU` 批量查询
3. 结合搜索量、关键词难度，实现难度等维度综合跳出10可以做需求， 以各个需求词解决了什么问题、实现难度等维度分析汇总到一个 markdown 给我