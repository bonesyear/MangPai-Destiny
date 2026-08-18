# Kimi 任务：LLM 通路 MVP（方案 C 混合：升级 narrative 层）——骨架 + 单命示例

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md`（§0 分层铁律/§8 工具链）+ `/root/.claude/projects/-root-metaphysics/memory/kimi-llm-channel-2026-08-14.md`（可行性分析：方案 C 混合，70% 已存在——narrative.py 已有「引擎 dict→LLM 叙述→N1 数字校验」全链；增量仅三块：DeepSeek 后端/JSON mode 分维输出/三层依据校验）
2. **前置已完成**（修批 A/F14）：siwang 已 scrub（payload 零死亡词汇）、prompts 已解锁、39 键 payload 干净、gongmen 已摘除——LLM 通路安全前置全部就绪
3. 本批 = **MVP 骨架 + 单命示例跑通**（全量 294 例验证下一步）
4. 汇报 300 字内

## 背景
- narrative.py 已实现「引擎 dict→LLM 叙述→N1 数字校验」全链（N1=数字校验：LLM 输出数字与引擎一致）
- 增量三块：①DeepSeek 后端（urllib 直连，不引 SDK；key 在 /root/.hermes/.env 的 DEEPSEEK_API_KEY）②JSON mode 分维输出（性格/事业/财运/婚姻/应期 schema）③三层依据校验（schema + JSON-path 出处解析 + 枚举回对）

## 任务
1. **DeepSeek 后端**：urllib 直连 DeepSeek API（model=deepseek-v4-flash，thinking+json mode 按文档配置），封装 `llm_backend.py`（请求/重试/超时/成本计数）
2. **抽取器**：schools selectors 39 键 → 特征 JSON（按 llm-channel 归档）
3. **三层校验器**：schema 校验 + JSON-path 出处解析（LLM 每个结论可溯源到特征键）+ 枚举回对（档位/桶枚举值校验）
4. **prompt 模板**：段氏风格 few-shot（narrative 现有）+ 安全红线（死亡/寿数禁令——F14 ENVELOPE_RULES 同款）+ JSON mode 输出 schema
5. **narrative 接线**：现有 narrative 全链接入 DeepSeek 后端（或旁路新增通道，按方案 C 混合——LLM 输出永不入 compute_all dict）
6. **单命示例跑通**：取 1 个 trainset 案例（如李嘉诚造或某个书例）实跑——引擎特征 → LLM 叙述 → 三层校验 → 输出展示；记录成本（token/耗时）

## 红线
- **LLM 输出永不入 compute_all() dict**（六件套不受影响）
- prompt 调优只吃 trainset（不碰留出集）
- siwang 屏蔽保持（payload 已 scrub，prompt 禁令双保险）
- 本批不评估准确率（单命示例只验证链路通）

## 验证（轻量）
1. 单命示例链路全通（特征→LLM→校验→展示）
2. pytest 全绿（引擎零改动）
3. 成本记录（¥/命预估 vs 实测）

## 产出
1. llm_backend.py / 校验器 / prompt 模板文件
2. 单命示例输出（LLM 叙述成品）
3. 成本实测报告
4. 汇报 300 字内（链路状态/示例摘要/成本/下一步）
