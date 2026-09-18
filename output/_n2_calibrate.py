"""N2-S1 校准：同 _v3_calibrate.py 口径扩七维 + 新维红线统计。
judge 仅跑抽样 30 例（judge30.jsonl）。达标线：新维 red=0 且翻转=0；
既有五维翻转 ≤1/30；judge 采信需一致率 ≥85% 且翻转召回 100%。

H-fix-7：一致率/翻转召回/达标判定下沉 output/_eval_common.py
（薄包装，cal schema 与打印格式不变）。

用法: T3_OUT_DIR=output/t3_s1_n2 /usr/bin/python3 output/_n2_calibrate.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (  # noqa: E402
    load_json, load_jsonl, review_stats, agreement_stats, judge_stats,
    judge_acceptance)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')
DIMS_R = ('财命', '官命', '职业', '婚姻', '应期', '迁移', '相貌')
DIMS_J = ('cai', 'guan', 'zhi', 'hun', 'ying', 'qian', 'mao')
MAP = dict(zip(DIMS_R, DIMS_J))
NEW_DIMS = ('迁移', '相貌')
L2 = set(load_json(os.path.join(OUT, 'l2_ids.json')))


def main():
    review = load_jsonl(os.path.join(OUT, 'review30.jsonl'))
    judge = load_jsonl(os.path.join(OUT, 'judge30.jsonl'))
    sample = load_json(os.path.join(OUT, 'sample30.json'))['sample']

    r_stat, r_flips, r_reds, r_tot = review_stats(review, sample, DIMS_R, L2,
                                                  new_dims=NEW_DIMS)
    r_flip_cases = sorted({x['id'] for x in r_flips})

    agree, tot, flip_recall_hit, flip_recall_tot, per_dim, divergences = \
        agreement_stats(review, judge, sample, DIMS_R, MAP)

    j_stat, j_flips, j_reds, j_tot = judge_stats(judge, DIMS_R, MAP,
                                                 new_dims=NEW_DIMS)

    agree_rate, recall, accept_judge = judge_acceptance(
        agree, tot, flip_recall_hit, flip_recall_tot)
    new_flip = [x for x in r_flips if x['dim'] in NEW_DIMS]
    old_flip = [x for x in r_flips if x['dim'] not in NEW_DIMS]

    cal = {
        'review30': {
            'per_dim': {d: {'0': r_stat[(d, 0)], '1': r_stat[(d, 1)],
                            '2': r_stat[(d, 2)], 'N/A': r_stat[(d, 'N/A')]}
                        for d in DIMS_R},
            'flip_cases': r_flip_cases,
            'flips': r_flips,
            'newdim_flips': new_flip,
            'newdim_reds': r_reds,
            'soft_rate': sum(v for (d, s), v in r_stat.items() if s == 1) / r_tot,
        },
        'agreement': {
            'cells': tot, 'agree': agree, 'rate': round(agree_rate, 4),
            'per_dim': {d: {'tot': per_dim[(d, 'tot')],
                            'agree': per_dim[(d, 'agree')]} for d in DIMS_R},
            'flip_recall': f'{flip_recall_hit}/{flip_recall_tot}',
            'accept_judge_sample': accept_judge,
            'divergences': divergences,
        },
        'judge_sample': {
            'n': sum(1 for r in judge.values() if 'result' in r),
            'per_dim': {d: {'0': j_stat[(d, 0)], '1': j_stat[(d, 1)],
                            '2': j_stat[(d, 2)]} for d in DIMS_R},
            'cells': j_tot,
            'flip_cases': sorted({x['id'] for x in j_flips}),
            'flips': j_flips,
            'newdim_reds': j_reds,
            'soft_rate': sum(v for (d, s), v in j_stat.items() if s == 1) / j_tot if j_tot else 0,
        },
        'verdict': {
            'newdim_red_zero': len(r_reds) == 0,
            'newdim_flip_zero': len(new_flip) == 0,
            'old5_flips': len(old_flip),
            'old5_flip_cases': sorted({x['id'] for x in old_flip}),
        },
    }
    with open(os.path.join(OUT, 'calibration.json'), 'w', encoding='utf-8') as f:
        json.dump(cal, f, ensure_ascii=False, indent=1)

    print(f'评审 30 例: 翻转例 {len(r_flip_cases)}/30 = {r_flip_cases}')
    print(f'  新维翻转 {len(new_flip)}（线=0）: {[(x["id"], x["dim"]) for x in new_flip]}')
    print(f'  新维红线 {len(r_reds)}（线=0）: {[(x["id"], x["dim"]) for x in r_reds]}')
    print(f'  既有五维翻转 {len(old_flip)}（线 ≤1）: {[(x["id"], x["dim"]) for x in old_flip]}')
    print(f'  放大缩水率: {cal["review30"]["soft_rate"]*100:.1f}%')
    print(f'一致率: {agree}/{tot} = {agree_rate*100:.1f}%（线 85%）；翻转召回 {flip_recall_hit}/{flip_recall_tot}')
    print('  分维一致: ' + ', '.join(
        f'{d} {per_dim[(d,"agree")]}/{per_dim[(d,"tot")]}' for d in DIMS_R))
    print(f'judge 30 例: 翻转例 {sorted({x["id"] for x in j_flips})}，'
          f'新维红线 {len(j_reds)}，放大缩水率 {cal["judge_sample"]["soft_rate"]*100:.1f}%')
    print(f'采信判定: {"一致率达标" if accept_judge else "一致率不达标，judge 仅作筛子"}')


if __name__ == '__main__':
    main()
