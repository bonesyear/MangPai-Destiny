"""汇总批跑：最新记录判质量，全部尝试计成本与首轮失败率。
用法: python3 output/_llm_batch_analyze.py <batch_dir>"""
import json
import re
import sys
from collections import Counter

from _eval_common import (
    FEWSHOT_CONTAMINATED_IDS, load_batch, summarize_costs,
    without_fewshot_contamination)


def main():
    if len(sys.argv) < 2:
        raise SystemExit('用法: python3 output/_llm_batch_analyze.py <batch_dir>')
    attempts, recs = load_batch(sys.argv[1])
    excluded = sorted({r['id'] for r in attempts if r['id'] in FEWSHOT_CONTAMINATED_IDS})
    clean_attempts = without_fewshot_contamination(attempts)
    recs = without_fewshot_contamination(recs)
    print(f'few-shot 污染单列，不计入质量指标: {excluded}')
    n = len(recs)
    api_err = [r for r in recs if 'api_error' in r or 'engine_error' in r]
    parse_err = [r for r in recs if 'parse_error' in r]
    valid = [r for r in recs if 'violations' in r]

    by_layer = Counter()
    by_dim = Counter()
    by_path = Counter()
    case_layer = Counter()
    n1_cases = []
    for r in valid:
        layers = set()
        for v in r['violations']:
            by_layer[v['layer']] += 1
            layers.add(v['layer'])
            m = re.match(r'([^\s.：「(]+)', v['detail'])
            if m:
                by_dim[m.group(1)] += 1
            if v['layer'] == 'L1':
                pm = re.search(r': (\S+)$', v['detail'])
                if pm:
                    by_path[pm.group(1).split('.')[0]] += 1
            if v['layer'] == 'N1':
                n1_cases.append(r['id'])
        for layer in layers:
            case_layer[layer] += 1

    first = {}
    for index, rec in enumerate(clean_attempts):
        key = (rec.get('timestamp') or '', rec.get('run_id') or '', index)
        if rec['id'] not in first or key < first[rec['id']][0]:
            first[rec['id']] = (key, rec)
    first_parse = sum('parse_error' in rec for _, rec in first.values())
    nv = len(valid)
    print(f'总例数={n} api/engine错误={len(api_err)} JSON解析失败(L0级)={len(parse_err)}')
    print(f'首轮解析失败={first_parse}/{n} ({first_parse / max(n, 1) * 100:.2f}%)；'
          f'当前解析失败={len(parse_err)}/{n} ({len(parse_err) / max(n, 1) * 100:.2f}%)')
    print(f'有效校验例={nv}；L1/L2/N1 按有效例计，L0 与解析失败按全部例计')
    for layer in ('L0', 'L1', 'L2', 'N1'):
        count = case_layer[layer] + (len(parse_err) if layer == 'L0' else 0)
        denominator = n if layer == 'L0' else nv
        print(f'{layer}: 违规例={count} ({count / max(denominator, 1) * 100:.2f}%) '
              f'违规条数={by_layer[layer]}')
    print('\n违规维度分布:', by_dim.most_common(15))
    print('\nL1 无出处路径 top 键:', by_path.most_common(15))

    costs = summarize_costs(attempts)
    pin = sum((r.get('usage') or {}).get('prompt_tokens', 0) for r in attempts)
    pout = sum((r.get('usage') or {}).get('completion_tokens', 0) for r in attempts)
    elapsed = [r.get('elapsed_s', 0) for r in attempts if r.get('elapsed_s')]
    print(f'\n成本（全部尝试，分币别）: ¥{costs["cost_cny"]:.2f} + '
          f'${costs["cost_usd"]:.4f}（旧美元口径，未折算） | tokens in={pin} out={pout}')
    print(f'耗时: mean={sum(elapsed) / max(len(elapsed), 1):.1f}s '
          f'max={max(elapsed) if elapsed else 0:.1f}s')
    if api_err:
        print('\napi 错误例:', [
            (r['id'], str(r.get('api_error', r.get('engine_error', '')))[:80])
            for r in api_err])
    if parse_err:
        print('\n解析失败例:', [r['id'] for r in parse_err])


if __name__ == '__main__':
    main()
