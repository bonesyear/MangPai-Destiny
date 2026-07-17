#!/bin/bash
# 全量验证 + 回归一键脚本。用法: bash mangpai/tests/backtest/verify_all.sh
cd "$(dirname "$0")/../../.." || exit 1
echo "=== 853 checks ==="
echo "verify_mangpai: $(python3 mangpai/verify_mangpai.py 2>&1 | grep 验证结果)"
echo "verify_dayun:   $(python3 mangpai/verify_dayun.py 2>&1 | grep 验证结果)"
echo "obj_verify:     $(python3 -c "import sys; sys.path.insert(0,'$PWD'); import runpy; runpy.run_path('$PWD/mangpai/objective/verify_mangpai.py', run_name='__main__')" 2>&1 | grep 验证结果)"
echo "=== pytest ==="
python3 -m pytest mangpai/tests/ -q 2>&1 | tail -1
echo "=== 67 regression (vs baseline) ==="
python3 mangpai/tests/backtest/regression67.py 2>&1 | grep -E "cat[0-9]|TOTAL|REGRESSION|IMPROVE|无变化"
echo "=== calib 46 assertions (vs baseline) ==="
python3 mangpai/tests/calib_assertions.py 2>&1 | grep -E "财命|官命|婚姻|职业|应期|子息|层功|TOTAL|REGRESSION|IMPROVE|无变化"
