# Kimi 任务：脱敏脱密自动闸门（check_credentials）+ 修 calib 硬编码

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + `docs/remaining-tasks-20260919.md`（本轮安全整改背景）
2. 本批 = ①修 1 处代码硬编码 ②新建**入库的脱敏闸门脚本** + pre-commit hook + 哨兵测试
3. **脚本自身不得含任何真实凭证**（只含模式）；输出**一律打码**（见红线）
4. 汇报 400 字内

## 背景
用户要求：**保证以后上传仓库的代码都做脱敏脱密处理**——不能靠"记得住"，要有**自动化拦截机制**。现状：仓库已有两个同类入库守护脚本（`scripts/check_layering.py` 分层单向、`scripts/check_typing_imports.py` typing/import 面），本批加第三个，并接到 commit 前。

## 任务 A：修硬编码路径（真缺口，1 行）
`mangpai/calib_zhenbao.py:5` → `sys.path.insert(0, '/root/metaphysics')`
- 改为锚定 `__file__`（同 B 方案先例：`Path(__file__).resolve().parents[1]`——注意 `mangpai/` 是一级目录，请自行核实层级）
- 全仓确认这是**代码文件里最后一处**本机绝对路径（`git grep -nE "/root/|/Users/|C:\\\\Users" -- "*.py"`）

## 任务 B：新建 `scripts/check_credentials.py`（脱敏闸门，入库）

**用途**：入仓前自动扫描凭证/隐私/本机路径；可独立跑，也可被 pre-commit hook 调用。

**扫描模式**（分类分级）：
- **P0 真凭证**（**阻止**）：`ark-[A-Za-z0-9]{6,}`、`sk-[A-Za-z0-9]{16,}`、`ghp_`/`gho_`/`github_pat_`、`AKIA[A-Z0-9]{16}`、`xox[bp]-`、`-----BEGIN [A-Z ]*PRIVATE KEY`、`Bearer <20+ 字符>`、`[A-Za-z0-9_-]{32,}` 高熵串（**须带误报控制**：如要求邻近出现 key/secret/token 字样）
- **P1 隐私**（**默认阻止**）：中国大陆手机号 `1[3-9]\d{9}`、身份证 18 位、非 example 域名的邮箱
- **P2 本机路径**（**默认仅警告**）：`/root/`、`/Users/`、`C:\Users\`、`/home/<真实用户名>/`

**白名单/豁免**（必须实现，否则不可用）：
- 占位符：`your-`、`xxx`、`<REDACTED>`、`example`、`test@`、`127.0.0.1`、`localhost`、`0.0.0.0`、`192.168.*`、`10.*`
- 测试假值：`sk-file`、`sk-fake*`、`***`
- 模式描述自身：脚本/文档里作为**扫描模式**出现的字符串（如 `ark-[A-Za-z0-9]`）

**关键技术设计（务必照做）**：
1. **默认只扫暂存区新增行**（`git diff --cached --unified=0` 解析 `+` 行）——**存量不干扰**（仓库已有 165 文件含 `/root/` 存量路径，全量扫会被永久卡住）；提供 `--all` 做全量审计模式、`--staged`（默认）供 hook 用
2. **输出一律打码**：命中片段只输出"前 4 + 后 2"或 `<REDACTED>`，**绝不打印完整敏感串**（本批红线；前次事故就是打码失败——字符类漏掉 `-` 导致正则不匹配而**原样打印**，请在实现里对"打码结果"做断言）
3. **退出码**：P0/P1 命中 → 1（阻止 commit）；仅 P2 → 0 + 警告（`--strict` 可升级为 1）
4. **零依赖**（纯标准库）；`--help` 说明用法

**配套**：
- `scripts/install_git_hooks.sh`（或 README 段落）：把 `pre-commit` 装到 `.git/hooks/`（`.git/hooks/` 不入库，故需可安装脚本 + 文档说明）；hook 内容 = 调用 `python3 scripts/check_credentials.py --staged`，非 0 则拒绝提交并打印修复指引
- 在 `README.md`（或 `docs/` 相应节）加一小节说明：**入仓前的脱敏闸门**怎么用/怎么装

## 任务 C：哨兵测试 `mangpai/tests/test_credential_gate.py`（先红后绿）
必测：
1. 合成假凭证（如 `ark-` + 32 位假串）→ **必须命中 P0 且退出码 1**
2. 占位符（`your-api-key-here`、`sk-xxx`）→ **必须放行**
3. 打码函数**单测**：给定完整假 key → 输出中**不得包含**原串（断言 `full not in masked`）
4. 本机路径新增行 → P2 警告但退出码 0；`--strict` 时退出码 1
5. 暂存区模式：用一个临时 git 仓库（`tmp_path`）构造带/不带敏感串的 staged 文件，验证拦截行为

## DoD（逐项实跑）
- [ ] A：`calib_zhenbao.py` 改后从**非仓库目录**可运行（路径解析正确）；`git grep -nE "/root/" -- "*.py"` 零命中
- [ ] B：脚本 `--help` 可用；`--all` 全量扫跑通（P2 存量会大量命中属预期，不得报错退出）；`--staged` 在干净工作区退出 0
- [ ] B：打码断言通过（输出中无完整敏感串）
- [ ] C：哨兵 5 类全绿（先红后绿：先写测试跑红，再实现到绿）
- [ ] 六件套：pytest 全绿（新增测试计入）+ verify 432/70/64/20 + **blind vs `snapshots/20260918_t1.json` 零翻转** + 双 seed + 分层两件套
- [ ] `git status --short` 核对改动范围；提交（不 push）
- [ ] 汇报 400 字内

## 红线
- **任何输出（含报告/stdout/commit message/测试 fixture）不得含真实凭证明文**；测试用**合成假值**
- 脚本零依赖、纯标准库
- 不动引擎判定；不改历史文档（166 文件存量路径不清理，闸门只对**新增**生效）
- 不调外部 API
