# Kimi 任务：LLM 通道打磨（峰谷价更新 _PRICING + 正式通道文档）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/llm-batch-report-20260818.md`（批量校验报告：4 轮迭代轨迹 L1 40.21%→3.41%→remap 0.00%，L0 0.36/N1 0.36/L2 4.98 达标）+ `/root/metaphysics/mangpai/subjective/llm_backend.py`（当前 `_PRICING` = 旧平价 $0.14/$0.28）+ `/root/metaphysics/mangpai/subjective/llm_channel.py` + `llm_prompt.py`
2. 本批 = **打磨收尾**（引擎零改动；llm 模块可改）
3. 汇报 300 字内

## 任务
### 1. 峰谷价更新 _PRICING
- DeepSeek 官方峰谷（你在迭代 4 已确认）：peak=UTC 01:00-04:00/06:00-10:00（北京 09:00-12:00、14:00-18:00），其余 off-peak **半价**
- 更新 `llm_backend.py`：_PRICING 增加 peak/off-peak 两档（v4-flash peak $0.14/$0.28、off-peak 半价 $0.07/$0.14——**以官方最新口径为准，重新核一次**）；`_estimate_cost` 按请求时间自动选档（北京时间 09-12/14-18 为 peak）
- 成本计数随实际时段出（历史数据成本不重算，标注即可）
- 测试：构造 peak/off-peak 两个时间点验证计价

### 2. 正式通道文档
- 新建 `docs/llm-channel-20260818.md`（通道交付文档）：
  - §1 接口（llm_channel 单命入口/参数/返回结构/validate 三模式 mark/reject/off）
  - §2 验证记录（四指标达标线 + 迭代轨迹表 + remap 规则表 + L1=0）
  - §3 使用指南（成本实测 + 峰谷价 + 批次脚本一键命令 + 低峰期建议）
  - §4 安全红线（死亡 scrub + prompt 禁令双保险、LLM 不落 compute_all、只吃 trainset）
  - §5 维护项（峰谷价机制说明、未来迭代记录位、与 narrative.py 的关系）
- KB §8 工具链补 llm 通道条目 + CHANGELOG 记录本批

## 红线
- 引擎零改动（llm_* 模块可改，compute_all 链不碰）
- 文档数字全部以实测为准（不估）

## 验证
1. pytest 全绿（llm_backend 计价测试新增）
2. 计价探针：peak/off-peak 两时间点各估一次，确认档位正确
3. 文档抽查（grep 关键数字：0.00%/0.36/4.98/¥/半价）

## 汇报（300 字内）
峰谷价更新细节（官方最新价/时段/计价逻辑）+ 正式通道文档结构 + pytest + 计价探针结果
