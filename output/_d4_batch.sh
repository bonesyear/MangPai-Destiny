#!/bin/bash
# 谷段批跑驱动：失败即停，默认新目录，等待并复核谷段后运行。
set -euo pipefail
cd "$(dirname "$0")/.."
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
export LLM_BATCH_DIR="${LLM_BATCH_DIR:-output/llm_batch_${RUN_ID}}"
export MANGPAI_LLM_BUDGET_CNY="${MANGPAI_LLM_BUDGET_CNY:-${MANGPAI_BATCH_BUDGET_CNY:-0}}"

SLEEP_SECONDS="$(python3 -c 'from output._eval_common import seconds_to_valley; print(seconds_to_valley())')"
if (( SLEEP_SECONDS > 0 )); then
  echo "sleep ${SLEEP_SECONDS}s until next valley"
  sleep "$SLEEP_SECONDS"
fi
python3 -c 'from mangpai.subjective.llm_backend import _price_tier; import sys; sys.exit(_price_tier() != "offpeak")'

python3 output/_llm_batch_trainset.py
for i in 1 2; do
  python3 output/_llm_batch_retry.py
done
python3 output/_llm_batch_rescore.py "$LLM_BATCH_DIR"
