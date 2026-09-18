"""N2-S1 加严抽样 30 例：新维违规例全取 + zhenbao-23a 强制 + L2 高危例
+ 分层随机（tier_static × is_guanming）补足至 30。seed 固定可复现。

H-fix-7：分层补足下沉 output/_eval_common.py（薄包装，seed/强制集口径不变）。

产出: $T3_OUT_DIR/sample30.json
用法: T3_OUT_DIR=output/t3_s1_n2 /usr/bin/python3 output/_n2_sample.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import load_json, stratified_fill  # noqa: E402

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')
SEED = 20260821
N = 30


def main():
    dump = load_json(os.path.join(OUT, 'dump.json'))
    l2 = set(load_json(os.path.join(OUT, 'l2_ids.json')))
    newdim = set(load_json(os.path.join(OUT, 'newdim_ids.json')))
    rng = random.Random(SEED)

    forced = list(dict.fromkeys(
        sorted(newdim) + ['zhenbao-23a'] + sorted(l2)))
    forced = [c for c in forced if c in dump]

    fill = stratified_fill(dump, forced, N, rng)

    sample = forced + fill
    out = {'seed': SEED, 'newdim': sorted(newdim), 'l2': sorted(l2),
           'forced': forced, 'fill': fill, 'sample': sample}
    with open(os.path.join(OUT, 'sample30.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'forced {len(forced)} = 新维 {len(newdim)} + zhenbao-23a + L2 '
          f'{len(l2)}; fill {len(fill)}; 合计 {len(sample)}')
    print('forced:', json.dumps(forced, ensure_ascii=False))
    print('fill:', json.dumps(fill, ensure_ascii=False))


if __name__ == '__main__':
    main()
