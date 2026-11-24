"""T3 校准：读取当前批次高危集，报告实际样本范围与翻转率上界。"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (
    load_id_file, load_json, load_jsonl, review_stats, agreement_stats,
    agreement_quality, judge_stats, judge_acceptance,
    without_fewshot_contamination)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1')
DIMS_R = ('财命', '官命', '职业', '婚姻', '应期')
DIMS_J = ('cai', 'guan', 'zhi', 'hun', 'ying')
MAP = dict(zip(DIMS_R, DIMS_J))


def clopper_pearson_upper(k, n, alpha=0.05):
    if n <= 0:
        return None
    if k == n:
        return 1.0
    if k == 0:
        return 1 - alpha ** (1 / n)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        p = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * p**i * (1 - p)**(n - i)
                  for i in range(k + 1))
        if cdf > alpha:
            lo = p
        else:
            hi = p
    return (lo + hi) / 2


def main():
    l2_path = os.path.join(OUT, 'l2_ids.json')
    if not os.path.exists(l2_path):
        raise SystemExit(f'缺少当前批次高危名单: {l2_path}')
    _, l2 = load_id_file(l2_path)
    l2 = set(l2)
    review = without_fewshot_contamination(
        load_jsonl(os.path.join(OUT, 'review30.jsonl')))
    judge = without_fewshot_contamination(
        load_jsonl(os.path.join(OUT, 'judge281.jsonl')))
    sample = without_fewshot_contamination(
        load_json(os.path.join(OUT, 'sample30.json'))['sample'])
    r_stat, r_flips, _, r_tot = review_stats(review, sample, DIMS_R, l2)
    r_flip_cases = sorted({x['id'] for x in r_flips})
    agree, tot, hit, flip_tot, per_dim, divergences = agreement_stats(
        review, judge, sample, DIMS_R, MAP, divergence_detail=True)
    j_stat, j_flips, _, j_tot = judge_stats(judge, DIMS_R, MAP, flip_with_ref=True)
    j_flip_cases = sorted({x['id'] for x in j_flips})
    quality = agreement_quality(review, judge, sample, DIMS_R, MAP)
    agree_rate, recall, accept = judge_acceptance(
        agree, tot, hit, flip_tot, quality=quality)
    dump_path = os.path.join(OUT, 'dump.json')
    dump_n = len(without_fewshot_contamination(load_json(dump_path))) \
        if os.path.exists(dump_path) else None
    judge_n = sum(1 for r in judge.values() if 'result' in r)
    full = dump_n is not None and judge_n >= dump_n
    accept_full = accept and full
    scope = '全量' if full else '抽样'
    cal = {
        'review30': {
            'n': len(sample),
            'per_dim': {d: {'0': r_stat[(d, 0)], '1': r_stat[(d, 1)],
                            '2': r_stat[(d, 2)], 'N/A': r_stat[(d, 'N/A')]} for d in DIMS_R},
            'flip_cases': r_flip_cases, 'flips': r_flips,
            'flip_rate_ci95_upper': clopper_pearson_upper(len(r_flip_cases), len(sample)),
            'soft_rate': sum(v for (d, s), v in r_stat.items() if s == 1) / r_tot if r_tot else 0,
        },
        'agreement': {
            'quality': quality, 'cells': tot, 'agree': agree, 'rate': round(agree_rate, 4),
            'per_dim': {d: {'tot': per_dim[(d, 'tot')], 'agree': per_dim[(d, 'agree')]} for d in DIMS_R},
            'flip_recall': f'{hit}/{flip_tot}', 'accept_judge_full': accept_full,
            'accept_judge': accept, 'judge_scope': scope, 'divergences': divergences,
        },
        'judge281': {
            'n': judge_n, 'dump_n': dump_n, 'scope': scope,
            'per_dim': {d: {'0': j_stat[(d, 0)], '1': j_stat[(d, 1)], '2': j_stat[(d, 2)]} for d in DIMS_R},
            'cells': j_tot, 'flip_cases': j_flip_cases, 'flips': j_flips,
            'soft_rate': sum(v for (d, s), v in j_stat.items() if s == 1) / j_tot if j_tot else 0,
        },
    }
    with open(os.path.join(OUT, 'calibration.json'), 'w', encoding='utf-8') as f:
        json.dump(cal, f, ensure_ascii=False, indent=1)
    upper = cal['review30']['flip_rate_ci95_upper']
    print(f'评审 {len(sample)} 例: 翻转例 {len(r_flip_cases)}/{len(sample)} = {r_flip_cases}；'
          f'95%上界={upper:.1%}' if upper is not None else '评审无有效样本')
    print(f'  L2 高危例中翻转: {sorted({x["id"] for x in r_flips if x["l2"]})}')
    print(f'  放大缩水率: {cal["review30"]["soft_rate"] * 100:.1f}%')
    print(f'一致率: {agree}/{tot} = {agree_rate * 100:.1f}%（线 85%）；翻转召回 {hit}/{flip_tot}')
    print('  分维一致: ' + ', '.join(
        f'{d} {per_dim[(d, "agree")]}/{per_dim[(d, "tot")]}' for d in DIMS_R))
    print(f'judge {scope} {judge_n}/{dump_n} 例: 翻转例 {len(j_flip_cases)}，'
          f'放大缩水率 {cal["judge281"]["soft_rate"] * 100:.1f}%')
    print(f'  judge 翻转例: {j_flip_cases}')
    print(f'采信判定: {"采信 judge " + scope if accept else "以评审样本为准，judge 降级为筛子"}')


if __name__ == '__main__':
    main()
