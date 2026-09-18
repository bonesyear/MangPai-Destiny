#!/bin/bash
# D4 谷段批跑驱动：睡到 12:00 谷段起跑 294 例 v4-flash（迭代 5 prompt），
# 自动 retry 失败例两轮，最后离线 rescore。
set -u
cd /root/metaphysics
export LLM_BATCH_DIR=output/llm_batch_20260819_d4

now=$(date +%s)
target=$(date -d '12:00:03' +%s)
if [ "$target" -gt "$now" ]; then
  echo "sleep $((target-now))s until valley 12:00:03"
  sleep $((target-now))
fi

python3 output/_llm_batch_trainset.py 0 294
for i in 1 2; do
  python3 output/_llm_batch_retry.py
done
python3 output/_llm_batch_rescore.py "$LLM_BATCH_DIR"
