# Kimi 任务：飞书集成工程（机器人对接 + 命令路由 + 引擎/LLM 通道接线）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + `/root/metaphysics/docs/llm-channel-20260818.md`（LLM 通道接口/安全红线）+ 收工记录（引擎终态）
2. **本工程开发验证不用 DeepSeek**（用户明确）：LLM 叙述用 mock 或 call_llm=False 验证链路，真实 DeepSeek 调用留运行时
3. 本批 = **飞书集成工程**（纯开发，本地 mock 验证）
4. 汇报 300 字内

## 任务
### 1. 飞书 API 客户端（mangpai/feishu/ 新目录或合适位置）
- 获取 tenant_access_token（app_id/app_secret → 凭证缓存）
- 接收消息（长连接 or webhook——按飞书开放平台标准）
- 发送消息（text/markdown/post；支持回复原消息）
- 配置从环境变量读（FEISHU_APP_ID/FEISHU_APP_SECRET——**不硬编码**，留配置位）

### 2. 命令路由
- 设计命令（自然语言为主）：
  - 排盘：用户发「阳历 1992-10-09 13:58 男 河南信阳」或四柱直输 → 引擎 compute_all
  - 输出：格式化结论（盲派做功→层功→财命→官命→婚姻→职业→应期）+ 可选 LLM 五维叙述
  - 辅助命令：/help、/ver（版本基线）、细挖命令预留（focus=财运/婚姻——二期）
- 输入解析：农历需用户自行转阳历（引擎不做农历转阳历——产品约束不变）；性别必填（D2 入口已强制）

### 3. 引擎/通道接线
- compute_all 全链（引擎键 45）
- LLM 通道：默认开（DeepSeek 谷段），validate=mark；**失败降级=引擎直出格式化结论**（validate=off 语义）
- 输出模板：Markdown 结构化（功神→层功→三维→婚姻→职业→应期→一句话总结——沿用 SOUL 输出风格）

### 4. 安全
- siwang scrub 保持（LLM 叙述零死亡词汇——F14/修批A 机制不动）
- 输入校验（D2 入口：性别/年份/lon 已强制）
- 超时/重试（LLM 调用超时 → 降级）

### 5. 测试（本地 mock，不连真实飞书）
- API 客户端 mock（token 获取/消息收发 mock 化）
- 命令路由测试（解析/分发）
- 全链路测试（mock 输入 → 引擎 → mock LLM → 输出格式）
- pytest 全绿（不破坏现有 739）

## 红线
- 引擎零改动（feishu 是外层应用，不碰 compute_all 链）
- LLM 输出不落 compute_all dict（维持）
- 不硬编码任何凭证（环境变量配置位）
- 开发验证不调真实 DeepSeek

## 验证
1. pytest 全绿（新增 feishu 测试 + 原有 739 不回归）
2. mock 全链路跑通（示例：康老师盘或李嘉诚盘 → 格式化输出展示）
3. 输出示例展示（Markdown 成品）

## 产出
1. feishu 模块代码（客户端/路由/接线/模板）
2. 测试
3. mock 全链路示例输出
4. 上线说明（填什么环境变量/怎么跑）
5. 汇报 300 字内
