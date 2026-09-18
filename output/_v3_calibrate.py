"""V3-S1 复抽校准：同 _t3_calibrate.py 口径，唯 L2 高危集改从 OUT/l2_ids.json 读
（本批 L2=当前校验器对 e7 批的违规例，非 T3 旧 14 例）。judge 仅跑抽样 30 例
（预算 <¥6，协议允许「抽样一致率校准」），judge281.jsonl 里即该 30 例。

H-fix-7：一致率/翻转召回/达标判定下沉 output/_eval_common.py
（薄包装，cal schema 与打印格式不变）。

用法: T3_OUT_DIR=output/t3_s1_v3 python3 output/_v3_calibrate.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (  # noqa: E402
    load_json, load_jsonl, review_stats, agreement_stats, judge_stats,
    judge_acceptance)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_v3')
DIMS_R = ('财命', '官命', '职业', '婚姻', '应期')
DIMS_J = ('cai', 'guan', 'zhi', 'hun', 'ying')
MAP = dict(zip(DIMS_R, DIMS_J))
L2 = set(load_json(os.path.join(OUT, 'l2_ids.json')))


def main():
    review = load_jsonl(os.path.join(OUT, 'review30.jsonl'))
    judge = load_jsonl(os.path.join(OUT, 'judge281.jsonl'))
    sample = load_json(os.path.join(OUT, 'sample30.json'))['sample']

    r_stat, r_flips, _, r_tot = review_stats(review, sample, DIMS_R, L2)
    r_flip_cases = sorted({x['id'] for x in r_flips})

    agree, tot, flip_recall_hit, flip_recall_tot, per_dim, divergences = \
        agreement_stats(review, judge, sample, DIMS_R, MAP,
                        divergence_detail=True)

    j_stat, j_flips, _, j_tot = judge_stats(judge, DIMS_R, MAP,
                                            flip_with_ref=True)
    j_flip_cases = sorted({x['id'] for x in j_flips})

    agree_rate, recall, accept_judge = judge_acceptance(
        agree, tot, flip_recall_hit, flip_recall_tot)

    cal = {
        'review30': {
            'per_dim': {d: {'0': r_stat[(d, 0)], '1': r_stat[(d, 1)],
                            '2': r_stat[(d, 2)], 'N/A': r_stat[(d, 'N/A')]} for d in DIMS_R},
            'flip_cases': r_flip_cases,
            'flips': r_flips,
            'soft_rate': sum(v for (d, s), v in r_stat.items() if s == 1) / r_tot,
        },
        'agreement': {
            'cells': tot, 'agree': agree, 'rate': round(agree_rate, 4),
            'per_dim': {d: {'tot': per_dim[(d, 'tot')], 'agree': per_dim[(d, 'agree')]} for d in DIMS_R},
            'flip_recall': f'{flip_recall_hit}/{flip_recall_tot}',
            'accept_judge_sample': accept_judge,
            'divergences': divergences,
        },
        'judge_sample': {
            'n': sum(1 for r in judge.values() if 'result' in r),
            'per_dim': {d: {'0': j_stat[(d, 0)], '1': j_stat[(d, 1)], '2': j_stat[(d, 2)]} for d in DIMS_R},
            'cells': j_tot,
            'flip_cases': j_flip_cases,
            'flips': j_flips,
            'soft_rate': sum(v for (d, s), v in j_stat.items() if s == 1) / j_tot if j_tot else 0,
        },
    }
    with open(os.path.join(OUT, 'calibration.json'), 'w', encoding='utf-8') as f:
        json.dump(cal, f, ensure_ascii=False, indent=1)

    print(f'评审 30 例: 翻转例 {len(r_flip_cases)}/30 = {r_flip_cases}')
    print(f'  L2 高危例中翻转: {sorted({x["id"] for x in r_flips if x["l2"]})}')
    print(f'  放大缩水率: {cal["review30"]["soft_rate"]*100:.1f}%')
    print(f'一致率: {agree}/{tot} = {agree_rate*100:.1f}%（线 85%）；翻转召回 {flip_recall_hit}/{flip_recall_tot}')
    print(f'  分维一致: ' + ', '.join(
        f'{d} {per_dim[(d,"agree")]}/{per_dim[(d,"tot")]}' for d in DIMS_R))
    print(f'judge 抽样 {cal["judge_sample"]["n"]} 例: 翻转例 {len(j_flip_cases)}，放大缩水率 {cal["judge_sample"]["soft_rate"]*100:.1f}%')
    print(f'  judge 翻转例: {j_flip_cases}')
    print(f'采信判定: {"一致率达标" if accept_judge else "一致率不达标，judge 仅作筛子"}')


if __name__ == '__main__':
    main()
