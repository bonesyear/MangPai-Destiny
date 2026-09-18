#!/usr/bin/env bash
# 安装 git hooks 到 .git/hooks/（该目录不入库，故需本脚本可重复执行）。
# 用法：bash scripts/install_git_hooks.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$ROOT/.git/hooks"
mkdir -p "$HOOKS_DIR"

cat > "$HOOKS_DIR/pre-commit" <<'EOF'
#!/usr/bin/env bash
# 脱敏脱密闸门：commit 前扫描暂存区新增行（P0 凭证 / P1 隐私 命中即拒绝）。
set -u
cd "$(git rev-parse --show-toplevel)"
python3 scripts/check_credentials.py --staged
rc=$?
if [ "$rc" -ne 0 ]; then
    echo ""
    echo "[pre-commit] 脱敏闸门拦截（退出码 $rc）。修复指引："
    echo "  - 真凭证/隐私：移除，改用环境变量或占位符（your-.../<REDACTED>/sk-fake...）"
    echo "  - 本机路径：改相对路径或 Path(__file__).resolve() 锚定"
    echo "  - 全量审计：python3 scripts/check_credentials.py --all"
    exit "$rc"
fi
EOF
chmod +x "$HOOKS_DIR/pre-commit"
echo "installed: $HOOKS_DIR/pre-commit"
