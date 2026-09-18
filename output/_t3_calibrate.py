"""T3-S1 第四层：评审（30）vs judge（281）一致率校准 + 达标判定汇总（零 API）。

校准口径（§5.2-3 / §5.4）：
- 逐维一致率 = 30 例重叠样本上 judge 与评审评分（0/1/2，N/A 双方剔除）完全相同比例；
- 翻转召回 = 评审判 2 的格中 judge 也判 2 的比例（须 100%）；
- 达标线：翻转 ≤1/30 且 L2 高危 14 例零翻转（≥3 例一票否决）；放大缩水 ≤20%。

H-fix-7：一致率/翻转召回/达标判定下沉 output/_eval_common.py
（薄包装，cal schema 与打印格式不变）。

产出: output/t3_s1/calibration.json + stdout 汇总
用法: python3 output/_t3_calibrate.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (  # noqa: E402
    load_json, load_jsonl, review_stats, agreement_stats, judge_stats,
    judge_acceptance)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1')
DIMS_R = ('财命', '官命', '职业', '婚姻', '应期')
DIMS_J = ('cai', 'guan', 'zhi', 'hun', 'ying')
MAP = dict(zip(DIMS_R, DIMS_J))
L2 = {'cj-1209', 'cj-1331', 'cj-1687', 'cj-平财弱财少', 'cj-校长', 'cj-歌唱家', 'cj-贫一生不富穷命',
      'reg67-普例4千万', 'yx-7842', 'yx-书法家', 'yx-建筑', 'yx-记者-2', 'yx-贫打工不赚钱无', 'zj-收入一般'}


def main():
    review = load_jsonl(os.path.join(OUT, 'review30.jsonl'))
    judge = load_jsonl(os.path.join(OUT, 'judge281.jsonl'))
    sample = load_json(os.path.join(OUT, 'sample30.json'))['sample']

    # ---------- 评审样本汇总 ----------
    r_stat, r_flips, _, r_tot = review_stats(review, sample, DIMS_R, L2)
    r_flip_cases = sorted({x['id'] for x in r_flips})

    # ---------- 一致率 ----------
    agree, tot, flip_recall_hit, flip_recall_tot, per_dim, divergences = \
        agreement_stats(review, judge, sample, DIMS_R, MAP,
                        divergence_detail=True)

    # ---------- judge 全量汇总 ----------
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
            'accept_judge_full': accept_judge,
            'divergences': divergences,
        },
        'judge281': {
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
    print(f'judge 全量 {cal["judge281"]["n"]} 例: 翻转例 {len(j_flip_cases)}，放大缩水率 {cal["judge281"]["soft_rate"]*100:.1f}%')
    print(f'  judge 翻转例: {j_flip_cases}')
    print(f'采信判定: {"采信 judge 全量" if accept_judge else "以评审样本为准，judge 降级为筛子"}')


if __name__ == '__main__':
    main()
