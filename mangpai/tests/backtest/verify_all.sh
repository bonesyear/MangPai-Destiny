#!/bin/bash
set -uo pipefail
# 全量验证 + 回归一键脚本。用法: bash mangpai/tests/backtest/verify_all.sh
# 可用 PYTHON=/path/to/python 指定解释器；默认优先 python3，回退 python。
cd "$(dirname "$0")/../../.." || exit 1
if [[ -z "${PYTHON:-}" ]]; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    else
        PYTHON=python
    fi
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "找不到 Python 解释器: $PYTHON（可用 PYTHON=... 指定）" >&2
    exit 2
fi
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
rc=0
failed=()

run_suite() {
    local label="$1" pattern="$2"
    shift 2
    local output status
    output=$("$@" 2>&1)
    status=$?
    if [[ $status -ne 0 ]]; then
        rc=1
        failed+=("$label(exit=$status)")
        echo "---- $label 最后20行输出 ----"
        tail -n 20 <<< "$output"
    fi
    if ! grep -E "$pattern" <<< "$output"; then
        rc=1
        failed+=("$label(no-summary)")
        if [[ $status -eq 0 ]]; then
            echo "---- $label 最后20行输出 ----"
            tail -n 20 <<< "$output"
        fi
    fi
}

echo "=== verify checks（375 + 72 + 68 + 20）==="
run_suite verify_mangpai '验证结果' "$PYTHON" mangpai/verify_mangpai.py
run_suite verify_dayun '验证结果' "$PYTHON" mangpai/verify_dayun.py
run_suite verify_layer1 '验证结果' "$PYTHON" mangpai/verify_layer1.py --require-all
run_suite verify_layer3 '验证结果' "$PYTHON" mangpai/verify_layer3_checkpoint.py
echo "=== pytest ==="
run_suite pytest 'passed|failed|error' "$PYTHON" -m pytest mangpai/tests/ -q
echo "=== 67 regression (vs baseline) ==="
run_suite regression67 'cat[0-9]|TOTAL|REGRESSION|IMPROVE|无变化' \
    "$PYTHON" mangpai/tests/backtest/regression67.py
echo "=== famous 23 regression (vs baseline) ==="
run_suite regression_famous 'zuogong|gongliang|guanming|caiming|zhiye|hunyin|laoyu|TOTAL|REGRESSION|IMPROVE|无变化' \
    "$PYTHON" mangpai/tests/backtest/regression_famous.py
echo "=== calib 45 assertions (vs baseline) ==="
run_suite calib_assertions '财命|官命|婚姻|职业|应期|子息|层功|TOTAL|REGRESSION|IMPROVE|无变化' \
    "$PYTHON" mangpai/tests/calib_assertions.py
echo "=== 509 regression gate ==="
run_suite blind_eval '条翻转|文本抖动合计|门禁失败|引擎异常' \
    "$PYTHON" mangpai/tests/heldout/blind_eval.py --baseline latest

if [[ ${#failed[@]} -gt 0 ]]; then
    echo "失败套件: ${failed[*]}" >&2
fi
exit "$rc"
