# Kimi 任务：H-fix-3 · 原子写批 + llm_channel 免责提级项

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H6 节**（写回原子性 P0）+ **H7 节**（基线写回无原子防护：blind_eval 快照 / calib_assertions.yaml / regression67/famous 的 `--write-baseline` 均原地覆盖）+ **H4 节**（llm_channel `validate='reject'` 降级缺免责声明 P1，本批提级）+ **H10 节**（build_book_index 无原子写）
2. 本批 = **H-fix-3（🔴 原子写 + 免责提级）**
3. 汇报 350 字内

## 阶段 0：写回点清点
实测清单（已初步 grep，请复核补全）：
- `mangpai/tests/heldout/blind_eval.py:494`（快照写）+ `:532`（payload 写）
- `mangpai/tests/heldout/curate.py:69`（merged.json）
- `mangpai/tests/heldout/extract_cases.py:269`（输出）
- `mangpai/tests/calib_assertions.py:328`（**calib YAML —— 评估基线，最高优先**）
- `regression67.py` / `regression_famous.py` 的 `--write-baseline`（复核具体行号）
- `scripts/build_book_index.py`（索引写回）
- 其余诊断脚本的 /tmp 写（低优先，顺带或标注不改）

## 阶段 1：原子写改造
**统一模式**（抽公共工具函数，避免重复）：
```python
def atomic_write(path, content, *, encoding='utf-8'):
    tmp = str(path) + '.tmp'
    with open(tmp, 'w', encoding=encoding) as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())      # 可选但推荐（基线文件）
    os.replace(tmp, path)          # 原子替换
```
建议放 `mangpai/tests/_atomic_io.py`（或 heldout 子目录的公共模块——按现有结构定）

**改造要点**：
1. 所有**基线/快照**写回（calib YAML / blind 快照 / regression baseline）必须原子
2. **写入前校验**（基线特有）：写出的内容可反解析（YAML/JSON 能 load 回来）+ 关键字段非空——不通过则拒绝写入并报错
3. **`--write-baseline` 加防护**：建议加确认提示或显式 `--force` 语义（防止误触覆盖基线）——若加需保持既有调用方兼容
4. 诊断脚本的 /tmp 写可顺带改（低风险）；若数量多则标注不改

## 阶段 2：llm_channel 免责提级项（H4 P1）
- `validate='reject'` 降级返回**缺免责声明**（其他三条降级都有）→ 补 `_DISCLAIMER_LINE`
- 红线一致性：所有降级路径都必须带免责（逐条核对四条路径）

## 阶段 3：哨兵
- 原子写测试：模拟写入中途失败（如 monkeypatch 让 write 抛异常）→ 断言原文件**未被破坏**（`.tmp` 残留但目标文件完好）
- 基线写回校验测试：注入非法 YAML 内容 → 断言拒绝写入
- 免责一致性测试：四条降级路径全带免责

## 验证（DoD）
- [ ] 写回点全部原子化（清单核对）
- [ ] 基线写回校验生效
- [ ] 四条降级路径免责齐全
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix2c.json` 零翻转零抖动**
- [ ] 引擎/主观层零改动（本批只改脚本 IO 与 llm_channel 降级文案）

## 产出
- 原子写工具 + 全部改造 + 哨兵
- backlog 追加「H-fix-3」节
- 汇报 350 字内：写回点清单（原子化数/未改数）+ 校验机制 + 免责四条 + 六件套结果

## 红线
- 不改引擎/主观层判定逻辑
- 不改既有命令行接口语义（除非显式说明兼容性）
- 不调外部 API
