# mangpai — 盲派命理计算包

## 当前结构

包按 Foundation → Objective → Subjective → Narrative 分层，共 59 个基础/客观/主观模块；编排器与叙事接入不计入该模块数。

```text
mangpai/
├── engine.py              # MangpaiEngine / calc_mangpai_full 主编排入口
├── objective/             # 27 个确定性计算与关系检测模块
├── subjective/            # 30 个解释、领域判断与 payload 模块
│   ├── schools.py         # 盲派 selectors（42 项）
│   ├── prompts/           # 当前理论及输出约束
│   └── llm_*.py           # 可选的结构化叙事通道
├── feishu/                # 可选的飞书 formatter 与接入层
└── tests/                 # 单元、契约、回测及 heldout 验证

foundation/                # 2 个跨流派基础模块
```

`mangpai/__init__.py` 与 `mangpai/objective/__init__.py` 提供公共导出；只 re-export 已存在的实现，不包含已删除的旧模块。

## 主调用方式

```python
from mangpai import calc_mangpai_full
from mangpai.subjective import build_payload

result = calc_mangpai_full(1992, 10, 9, 13, 58, 'male', 114.09)
features = build_payload(result)
```

- `build_payload` 按 selectors 投影引擎结果，保留嵌套的功量 `evidence/annotations`，不另建关系或层级字段。
- `gongliang.level` 是整数定性层级，`raw_level/boundary` 区分半层与无功；没有独立证据时，不由 level 推具体金额或官级。
- `llm_prompt`、`llm_channel`、narrative 与飞书 formatter 消费同一份引擎结果。真实 LLM 和飞书均为可选外部接入，不影响本地确定性计算。

## 验证

```bash
python mangpai/verify_mangpai.py
python -m pytest -q
bash mangpai/tests/backtest/verify_all.sh
```

当前验证数字以根目录 [README](../README.md) 和[知识库](../docs/knowledge-base.md)的实跑记录为准。快照链见[快照 README](tests/heldout/snapshots/README.md)；R9 仅统一消费端和文档，没有引擎行为变化时不新增基线。

## 当前文档

- [知识库](../docs/knowledge-base.md)：模块、规则与验证口径。
- [原著对照审计](../docs/audit-vs-originals-20261017.md)：书证、差异归因与未决专项。
- [变更记录](CHANGELOG.md)：各批实际改动及验证结果。
- [隐私说明](../docs/privacy-policy.md)：本地计算、可选外发与日志边界。
