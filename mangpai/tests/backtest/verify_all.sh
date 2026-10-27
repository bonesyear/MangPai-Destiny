#!/bin/bash
set -euo pipefail
# 全量验证 + 回归一键脚本。用法: bash mangpai/tests/backtest/verify_all.sh
# 可用 PYTHON=/path/to/python 指定解释器；默认 python。
cd "$(dirname "$0")/../../.." || exit 1
PYTHON="${PYTHON:-python}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
echo "=== verify checks（402 + 70 + 64 + 20）==="
VERIFY_MANGPAI_OUT="$("$PYTHON" mangpai/verify_mangpai.py 2>&1 | grep 验证结果)"
echo "verify_mangpai: $VERIFY_MANGPAI_OUT"
VERIFY_DAYUN_OUT="$("$PYTHON" mangpai/verify_dayun.py 2>&1 | grep 验证结果)"
echo "verify_dayun:   $VERIFY_DAYUN_OUT"
VERIFY_LAYER1_OUT="$("$PYTHON" mangpai/verify_layer1.py 2>&1 | grep 验证结果)"
echo "verify_layer1:  $VERIFY_LAYER1_OUT"
VERIFY_LAYER3_OUT="$("$PYTHON" mangpai/verify_layer3_checkpoint.py 2>&1 | grep 验证结果)"
echo "verify_layer3:  $VERIFY_LAYER3_OUT"
echo "=== pytest ==="
"$PYTHON" -m pytest mangpai/tests/ -q 2>&1 | tail -1
echo "=== 67 regression (vs baseline) ==="
"$PYTHON" mangpai/tests/backtest/regression67.py 2>&1 | grep -E "cat[0-9]|TOTAL|REGRESSION|IMPROVE|无变化"
echo "=== famous 23 regression (vs baseline) ==="
"$PYTHON" mangpai/tests/backtest/regression_famous.py 2>&1 | grep -E "zuogong|gongliang|guanming|caiming|zhiye|hunyin|laoyu|TOTAL|REGRESSION|IMPROVE|无变化"
echo "=== calib 46 assertions (vs baseline) ==="
"$PYTHON" mangpai/tests/calib_assertions.py 2>&1 | grep -E "财命|官命|婚姻|职业|应期|子息|层功|TOTAL|REGRESSION|IMPROVE|无变化"
