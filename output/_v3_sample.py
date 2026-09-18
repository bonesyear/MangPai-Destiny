"""V3-S1 抽样 30 例（同 T3/D4 设计）：L2 违规例强制全取 + 规则锚命中例
（cand2 全取 + cand1 按维补：财命 cand1 全取、官命/职业各 1）+ 余量按
财命档（tier_static)×官命（is_guanming) 分层随机补足至 30。seed 固定可复现。

H-fix-7：分层补足下沉 output/_eval_common.py（薄包装，seed/强制集口径不变）。

产出: output/t3_s1_v3/sample30.json + stdout 构成清单
用法: T3_OUT_DIR=output/t3_s1_v3 python3 output/_v3_sample.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import load_json, stratified_fill  # noqa: E402

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_v3')
SEED = 20260821
N = 30


def main():
    dump = load_json(os.path.join(OUT, 'dump.json'))
    cands = load_json(os.path.join(OUT, 'anchor_candidates.json'))
    l2 = set(load_json(os.path.join(OUT, 'l2_ids.json')))
    rng = random.Random(SEED)

    forced = list(l2)
    cand2 = sorted(cid for cid, h in cands.items()
                   if any(x['cand'] == 2 for x in h.values()) and cid not in forced)
    forced += cand2
    # cand1 按维补：财命全取（稀少），官命/职业各 1（seed 抽）
    for dim, k in (('财命', None), ('官命', 1), ('职业', 1)):
        pool = sorted(cid for cid, h in cands.items()
                      if dim in h and h[dim]['cand'] == 1 and cid not in forced)
        rng.shuffle(pool)
        take = pool if k is None else pool[:k]
        forced += take
    forced = list(dict.fromkeys(forced))

    # 分层随机补足：tier_static × is_guanming
    fill = stratified_fill(dump, forced, N, rng)

    sample = forced + fill
    out = {'seed': SEED, 'l2': sorted(l2),
           'forced': forced, 'fill': fill, 'sample': sample}
    with open(os.path.join(OUT, 'sample30.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'forced {len(forced)} = L2 {len(l2)} + cand2 {len(cand2)} + cand1 补 '
          f'{len(forced) - len(l2) - len(cand2)}; fill {len(fill)}; 合计 {len(sample)}')
    print('forced:', json.dumps(forced, ensure_ascii=False))
    print('fill:', json.dumps(fill, ensure_ascii=False))


if __name__ == '__main__':
    main()
