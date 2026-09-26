# 任务书：清理外部路径依赖 + 补齐优雅降级

> **路径约定**：`<REPO>` = 仓库根；`<VENV>` = 项目 venv 的解释器。
> 本机对照只在此声明一次：`<REPO>` = `/root/metaphysics`，`<VENV>` = `/root/fate-venv` 下的 `bin/python`。
> （正文一律用占位符——避免任务书本身携带本机绝对路径，那属脱敏闸门的 P2 项。）
>
> 来源：2026-09-25 引擎体检。三项问题**均不影响引擎本体**（排盘/做功/功量全链路正常、pytest 1172+1xf 全绿），
> 但影响本地脚本的可移植性与验证体验。范围明确、互不耦合。

---

## 任务 A：`output/_kang_*.py` 去除 openclaw 路径依赖（2 文件，**不产生提交**）

**现状**：这两个文件里有

```python
sys.path.insert(0, '/root/.openclaw/workspace/fate-system/fate-objective')
from main import calc_bazi_full
```

它们用的是**另一个系统里的旧排盘器**，而不是我们自己的。

**改成**（删掉上面两行，改用自家排盘器）：

```python
from mangpai.objective.bazi_calc import calc_bazi_full
```

**⚠️ 铁律（最重要）**：**绝对不读、不列、不写、不改 openclaw 目录下的任何内容**（那是另一个系统的领地，用户已明令不碰；其本机字面路径见上方代码块内那一行，此处不再复写）。
本任务**只改我们自己这两个文件**，判断依据仅限本任务书给出的行内容。

**验收**：
1. 改之前先跑一次并存基线：`cd <REPO> && /usr/bin/python3 output/_kang_verify.py > /tmp/kang_before.txt 2>&1`
2. 改之后再跑一次：`... > /tmp/kang_after.txt`
3. `diff /tmp/kang_before.txt /tmp/kang_after.txt` → **必须无差异**（逐字段一致）
4. `_kang_dump.py` 同样处理（如它也 import）

**注意**：`output/_kang*` 被 `.gitignore` 排除 → 本任务**不产生 git 提交**，属本地修正。请在报告中说明。

---

## 任务 B：heldout 诊断脚本的 `/tmp` 硬编码（5 文件，**入库**）

这些是一次性诊断流水线的成员——dump 脚本**产出** /tmp 数据，sim/detail 脚本**消费**它。dump 消失后消费方会直接崩。

| 文件 | 行 | 行为 |
|------|----|------|
| `mangpai/tests/heldout/_gm40_diag.py` | 66 | 写 `/tmp/gm40.json` |
| `mangpai/tests/heldout/_gm_all_dump.py` | 41 | 写 `/tmp/gm_all.json` |
| `mangpai/tests/heldout/_gm_sim.py` | 7 | 读 `/tmp/gm_all.json` |
| `mangpai/tests/heldout/_zy2_detail.py` | 18 | 读 `/tmp/zy_all.json` |
| `mangpai/tests/heldout/_zy2_sim.py` | 25 | 读 `/tmp/zy_all.json` |

**改成**：
1. **统一目录解析**（两个方向都用）：
   ```python
   import os, tempfile
   DIAG_DIR = os.environ.get('MANGPAI_DIAG_DIR') or tempfile.gettempdir()
   ```
   路径拼接用 `os.path.join(DIAG_DIR, '<name>.json')`
2. **读的一方加优雅降级**：目标文件不存在时，打印友好提示（说明该文件由哪个 dump 脚本生成、可用 `MANGPAI_DIAG_DIR` 指定目录），然后 `sys.exit(0)` —— **不要抛栈**。
3. **不改任何计算/断言/输出格式逻辑**（纯路径改造）。

**验收**：
1. 设目录后全链路可跑：
   ```bash
   export MANGPAI_DIAG_DIR=/tmp/mpdiag && mkdir -p /tmp/mpdiag
   <VENV> mangpai/tests/heldout/_gm_all_dump.py     # 产出到 /tmp/mpdiag/
   <VENV> mangpai/tests/heldout/_gm_sim.py          # 能读到，正常出结果
   ```
2. 不设环境变量时行为与现状等价（仍指向系统临时目录）
3. 缺文件时 `_gm_sim.py` 退 0 + 友好提示（把 dump 删掉实测一次）
4. **pytest 全量不回退**：`<VENV> -m pytest mangpai/tests/ -q` → 1172 passed + 1 xfailed

---

## 任务 C：`verify_layer1.py` 缺 sxtwl 时优雅降级（1 文件，**入库**）

**现状**：`mangpai/verify_layer1.py:75` 是裸 `import sxtwl`。在没有 sxtwl 的环境（如 `/usr/bin/python3`）里
**直接崩**、退 1、打栈回溯：

```
Traceback (most recent call last):
  File ".../verify_layer1.py", line 75, in <module>
    import sxtwl
ModuleNotFoundError: No module named 'sxtwl'
```

对比：`verify_mangpai.py` 遇到同样情况是**优雅降级**（打印提示、继续跑其余节）。请对齐这个风格。

**改成**：
```python
try:
    import sxtwl
except ImportError:
    sxtwl = None
```
节气抽样节在 `sxtwl is None` 时**打印一行跳过说明**（说明装了 sxtwl 才会跑该节、可用 `<VENV>` 解释器）并继续；
最终统计行如实反映跳过项数（风格与 `verify_mangpai` 一致）。

**⚠️ 不改节气校验逻辑本身**；装了 sxtwl 时**输出与现在逐字节一致**（改前存基线 → 改后 diff 必须无差异）。

**验收**：
1. `/usr/bin/python3 mangpai/verify_layer1.py` → **退 0**，打印跳过说明，**不崩**
2. `<VENV> mangpai/verify_layer1.py` → **64 passed, 0 failed**（与现状逐字节一致）
3. 六件套全绿

---

## 通用铁律

1. **不碰 openclaw 目录**（不读、不列、不写、不改、不移；磁盘排查也只报数字）
2. **不对 GitHub 仓库做任何写操作**（description / topics / issue / PR / 设置全不动）——需要同步的内容写在报告里，由 Hermes 执行
3. **解释器**：跑测试/闸门一律 `<VENV>`；`/usr/bin/python3` 只用于零依赖脚本
4. **不破坏既有闸门**：六件套全绿（分层 / typing / 键契约 / 防假-green / 脱敏 / 文档数字）、pytest **1172 passed + 1 xfailed** 不回退
5. **交付附 DoD 自证清单**，每条附**实测输出**（不接受"应该没问题"这类表述）；改前/改后有基线对比要求的，必须贴 diff 结果

## 交付

- 改后代码 + 自证清单
- 任务 A 单独说明「未产生提交」及其原因
- 任务 B / C 可提交（commit message 用中文，主题如 `fix: 诊断脚本路径可移植化 + verify_layer1 优雅降级`），**不要**把两个任务混在一个提交里
- 若发现任务书描述与现状不符（如某行号已漂移），**如实报告并以现状为准**，不要硬套
