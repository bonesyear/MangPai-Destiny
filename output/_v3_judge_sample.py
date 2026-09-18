"""V3-S1：judge 只跑抽样 30 例（预算 <¥6，协议允许抽样一致率校准）。
复用 _t3_eval.run（双实例隔离 judge prompt 原样，与 D4 可比）。
用法: T3_OUT_DIR=output/t3_s1_v3 T3_BATCH_DIR=output/llm_batch_20260819_e7 \
      python3 output/_v3_judge_sample.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_v3')

import _t3_eval  # noqa: E402


def main():
    with open(os.path.join(OUT, 'dump.json'), encoding='utf-8') as f:
        dump = json.load(f)
    sample = json.load(open(os.path.join(OUT, 'sample30.json'), encoding='utf-8'))['sample']
    _t3_eval.run('judge', sample, dump)


if __name__ == '__main__':
    main()
