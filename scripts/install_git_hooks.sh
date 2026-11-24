#!/usr/bin/env bash
# 安装凭证闸门到 Git 实际 hooks 目录；已有非本脚本钩子不覆盖。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$(git -C "$ROOT" rev-parse --path-format=absolute --git-path hooks)"
mkdir -p "$HOOKS_DIR"
MARKER="mangpai-credential-gate-v1"
COMMON="$HOOKS_DIR/mangpai-credential-gate"

if [ -e "$COMMON" ] && ! grep -q "$MARKER" "$COMMON"; then
    echo "refuse to overwrite existing hook: $COMMON" >&2
    exit 1
fi
cat > "$COMMON" <<'EOF'
#!/usr/bin/env bash
# mangpai-credential-gate-v1
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
PYTHON=()
if [ -n "${MANGPAI_PYTHON:-}" ]; then
    PYTHON=("$MANGPAI_PYTHON")
elif command -v python3 >/dev/null 2>&1; then
    PYTHON=(python3)
elif command -v python >/dev/null 2>&1; then
    PYTHON=(python)
elif command -v py >/dev/null 2>&1; then
    PYTHON=(py -3)
else
    echo "[credentials] 未找到 Python 3.10+，闸门未运行" >&2
    exit 3
fi
if ! "${PYTHON[@]}" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo "[credentials] 需要 Python 3.10+，闸门未运行" >&2
    exit 3
fi
run_gate() {
    "${PYTHON[@]}" scripts/check_credentials.py "$@"
    rc=$?
    case "$rc" in
        0) return 0 ;;
        1) echo "[credentials] 命中凭证/隐私，请移除或改用明确假值" >&2 ;;
        2) echo "[credentials] 闸门异常或存在未扫描文件，请检查环境" >&2 ;;
        *) echo "[credentials] 闸门运行失败（${rc}）" >&2 ;;
    esac
    return "$rc"
}
case "${1:-commit}" in
    commit)
        run_gate --staged || exit "$?"
        for gate in check_layering.py check_typing_imports.py check_doc_links.py; do
            "${PYTHON[@]}" "scripts/$gate" || exit "$?"
        done
        ;;
    push)
        EMPTY_TREE="$(git hash-object -t tree /dev/null)"
        while read -r _local_ref local_sha _remote_ref remote_sha; do
            local_sha="${local_sha%$'\r'}"
            remote_sha="${remote_sha%$'\r'}"
            if printf '%s' "$local_sha" | grep -Eq '^0+$'; then
                continue
            fi
            if printf '%s' "$remote_sha" | grep -Eq '^0+$'; then
                remote_sha="$EMPTY_TREE"
            fi
            run_gate --range "${remote_sha}..${local_sha}" || exit "$?"
        done
        ;;
    *) echo "[credentials] 未知钩子模式" >&2; exit 2 ;;
esac
EOF
chmod +x "$COMMON"

install_wrapper() {
    name="$1"
    mode="$2"
    target="$HOOKS_DIR/$name"
    if [ -e "$target" ] && ! grep -q "$MARKER" "$target"; then
        echo "refuse to overwrite existing hook: $target" >&2
        exit 1
    fi
    cat > "$target" <<EOF
#!/usr/bin/env bash
# $MARKER
exec "$HOOKS_DIR/mangpai-credential-gate" "$mode"
EOF
    chmod +x "$target"
    echo "installed: $target"
}
install_wrapper pre-commit commit
install_wrapper pre-merge-commit commit
install_wrapper pre-push push
