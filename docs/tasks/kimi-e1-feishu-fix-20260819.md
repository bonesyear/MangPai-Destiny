# Kimi 任务：修批 E1 · 飞书必修（U2 P1×3 + P2-4 VT 强制）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + U2 报告（`docs/kimi-review4-u2-feishu-20260819.md` 的 P1 三项：①token 服务端作废 99991663 无刷新重试缓存期全断 ②bot.py:50 client.reply 在 try 外发送失败线程静默死用户零反馈 ③Encrypt Key 不支持且 README 未警示误配全拒/静默丢）+ 修批 E 规划（E1 定位：飞书上线闸，无依赖先做，离线 mock 验证）
2. **独立判断纪律**：以飞书官方文档 + 代码实际为准
3. 本批 = **E1 飞书必修**（mangpai/feishu/ 可改，引擎零改动）
4. 汇报 300 字内

## 任务（四项）
1. **token 刷新重试**（P1-1）：`client._api` 捕获飞书错误码 **99991663**（token 失效）→ 清缓存重新获取 → 重试一次（防服务端提前作废全断）；99991661 一并处理
2. **reply 兜底**（P1-2）：bot.py:50 `client.reply` 包 try——发送失败记日志 + 尽力回传（如发 fallback 消息或至少不静默死线程）
3. **Encrypt Key 警示**（P1-3）：README 加红线说明（不支持 Encrypt Key——控制台勿配，误配后果）；代码侧 detect 到 encrypt 配置给警告
4. **VT 强制**（P2-4）：verification token 未配置 → 启动即报错（不静默零校验）；README 上线 checklist 补「必配 VT」
5. 哨兵：test_feishu 补 2-3 测（99991663 重试路径/reply 失败兜底/VT 缺失报错）

## 红线
- 引擎零改动（feishu 外层包）
- 不连真实飞书（mock 验证）；不调 DeepSeek
- 行为兼容（正常路径行为不变——重试只发生在 99991663/99991661）

## 验证
1. 哨兵红绿（新增测试先红后绿）
2. pytest 全绿（762+新增）
3. mock 冒烟（token 失效模拟 → 重试成功；reply 失败 → 兜底不崩）

## 汇报（300 字内）
四项实现/行号 + 哨兵红绿 + pytest + mock 冒烟结果
