# 任务：`check_doc_numbers.py` 增加「GitHub 仓库描述」核对（可选联网）

## 背景

`scripts/check_doc_numbers.py` 是常驻闸门六件套之一，离线校验仓库内 10 处**权威声明位**（README 首行/验证表/架构表 + KB §1/§8 的 pytest 与模块数），不一致退 1。

**本次要堵的缺口**：仓库的 **GitHub `description` 字段**（访客在仓库页标题下第一眼看到的那句话）也是"权威声明位"，且它在**站外**——闸门扫不到。实测：2026-09-25 发现它长期停在旧数字（`49 modules ... 919+ test cases`，实际应为 59 / 1158），是外部用户视角的失实。

目标：让闸门也能核这一项，但**不能破坏现有的一切**（见约束）。

## 硬约束（逐条遵守）

1. **默认行为逐字节零变化**：不带新开关时，脚本的离线检查项、输出格式、退出码语义**完全不变**（使用者 clone 后零配置、无网、无 token 也能跑，这是既定分享契约）。
2. **联网检查必须 opt-in**：新功能只在显式开关下启用，默认关闭。
3. **零本机路径**：脚本内不得出现本机绝对路径（形如用户 home 下的部署路径），既有代码风格照旧。
4. **零入库凭证 + 测试零外发**：不新增任何真实凭证；新增测试必须完全 mock 网络（monkeypatch `urllib.request.urlopen` 或等价注入），不得真实发起请求。
5. **纯标准库**：只用 `urllib.request` + `json`（不引入 `requests` / `httpx`）。
6. **防假-green**：显式开启了联网检查却**无法完成校验**时，**必须退 1 并说明原因**——绝不允许"没检查却报绿"。（这是本项目防假-green 闸门的既定精神。）

## 设计（已定，照此实现）

**开关**：`--github`

```
python3 scripts/check_doc_numbers.py              # 现状：只查仓库内 10 处，离线
python3 scripts/check_doc_numbers.py --github     # 追加：查 GitHub description
python3 scripts/check_doc_numbers.py --github --json
# 既有的 --quiet / --json / --strict 语义保持
```

**取值来源（全部环境变量，全部可选）**：

| 变量 | 默认 | 说明 |
|------|------|------|
| `MANGPAI_GITHUB_REPO` | `bonesyear/MangPai-Destiny` | 目标仓库 `owner/name` |
| `GITHUB_TOKEN` | 无 | 可选（仓库为 public，匿名亦可读；有 token 提高限速）。**读不到就匿名请求，不报错** |

**校验内容**：GET `https://api.github.com/repos/<repo>`（`Authorization: Bearer <token>` 仅在有 token 时带上；务必带 `Accept: application/vnd.github+json` 与 `User-Agent`），取 `description` 字段，用正则提取其中的数字声明：

- `(\d+)\s+modules` → 与实测模块数（脚本既有的模块计数口径）比对
- `(\d+)\s+test cases` → 与实测 pytest passed 数（脚本既有口径）比对

**行为矩阵（逐格实现 + 测试）**：

| 场景 | 退出码 | 输出 |
|------|--------|------|
| 不带 `--github` | 与现状完全一致 | 与现状一致 |
| `--github`，描述数字与实测一致 | 0 | 新增 1~2 行 ✅（标注 `github description`） |
| `--github`，数字不一致（如 49 / 919） | 1 | 精确报「期望 59 / 实际 49」这类差异行 |
| `--github`，正则**提不到**数字（描述被改写成别的措辞） | 1 | 报「无法从 description 提取数字声明」并打印当前描述 |
| `--github`，网络失败 / 非 200 / JSON 解析失败 | 1 | 报明原因（不吞异常） |
| `--github`，无 token | 正常匿名请求（不因缺 token 报错） | — |

**输出风格**：新增行要与既有 10 项**同一格式**（✅/❌ + 名称 + 期望 vs 实际），便于人读与 grep。

## 交付物

1. `scripts/check_doc_numbers.py` 改造（保持既有代码风格；网络调用抽成函数便于 mock）。
2. **哨兵测试**（扩展 `mangpai/tests/test_doc_numbers.py`）：**≥5 个新测**，覆盖上述矩阵中的每一格（一致 / 不一致 / 提不到数字 / 网络失败 / 匿名无 token 成功；再补一个「默认不带 `--github` 时行为不变」回归测）。
3. 文档同步：`README.md`（该脚本的说明处加 `--github` 用法与"需自备网络/可选 token"）与 `docs/knowledge-base.md`（工具表里该脚本一行补开关说明）。
4. **数字自洽**：加测试会让 pytest collected/passed 数变化 → **必须同步更新 README/KB 中的 pytest 数字**，否则 `check_doc_numbers` 会自己判红（这是自指校验，务必跑一遍确认）。

## DoD（逐项报告）

- [ ] 不带 `--github` 实跑：退出码与输出与改前一致（附改前/改后对照）
- [ ] `--github` 在**无 token**环境下能读到当前 description 并判绿（实测，附输出）
- [ ] 人为制造不一致（如临时把期望值改掉，或 mock）→ 精确报 ❌ 且退 1
- [ ] 网络失败/提不到数字两种情形各退 1 并给出明确原因（测试覆盖 + 至少一种真实演示）
- [ ] 新增测试 ≥5，全部 mock、零外发
- [ ] `python3 -m pytest mangpai/tests/ -q` 全绿，且 **README/KB 数字已同步**（跑 `python3 scripts/check_doc_numbers.py` 自证退 0）
- [ ] 六件套全绿（分层 / typing / 键契约 / 防假-green / 脱敏 / 文档数字）
- [ ] **零代码外改动**：不碰引擎、不改无关文件；`.gitignore` / 凭证相关不新增真实值
- [ ] 提交信息里**不得**出现任何 token 明文

## 禁止

- ❌ 把 token 或任何真实凭证写进代码/文档/测试/提交信息
- ❌ 让联网检查成为默认行为；❌ 在无网时静默跳过而不报错
- ❌ 引入第三方依赖
- ❌ 顺带重构无关代码（本次只做这一件事）

完成后按 DoD 逐项报告，附实测命令与输出。
