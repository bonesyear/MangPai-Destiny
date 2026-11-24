"""离线重评分：优先复用存档 features 与 as_of_year，零 API。
用法: python3 output/_llm_batch_rescore.py <batch_dir>"""
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import yaml

from _eval_common import (
    FEWSHOT_CONTAMINATED_IDS, engine_for_record, load_batch,
    without_fewshot_contamination)
from mangpai.subjective.llm_channel import validate_reading
from mangpai.tests.heldout.blind_eval import _git_sha, _worktree_meta


def main():
    if len(sys.argv) < 2:
        raise SystemExit('用法: python3 output/_llm_batch_rescore.py <batch_dir>')
    _, recs = load_batch(sys.argv[1])
    excluded = sorted({r['id'] for r in recs if r['id'] in FEWSHOT_CONTAMINATED_IDS})
    recs = without_fewshot_contamination(recs)
    print(f'few-shot 污染单列，不计入重评: {excluded}')
    with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'), encoding='utf-8') as f:
        cases = {c['id']: c for c in yaml.safe_load(f)}
    current_sha = {'git_sha': _git_sha(), **_worktree_meta()}
    case_layer = Counter()
    by_layer = Counter()
    l2_details = []
    skipped = []
    version_mismatch = []
    violation_mismatch = []
    legacy_time = []
    nv = 0
    for cid, r in recs:
        if 'reading' not in r:
            skipped.append(cid)
            continue
        res, features = engine_for_record(cases[cid], r)
        rep = validate_reading(r['reading'], features, res)
        nv += 1
        if r.get('engine_sha') != current_sha:
            version_mismatch.append(cid)
        if 'features' not in r or r.get('as_of_year') is None:
            legacy_time.append(cid)
        if 'violations' in r and r['violations'] != rep['violations']:
            violation_mismatch.append(cid)
        layers = set()
        for v in rep['violations']:
            by_layer[v['layer']] += 1
            layers.add(v['layer'])
            if v['layer'] == 'L2':
                l2_details.append((cid, v['detail']))
        for layer in layers:
            case_layer[layer] += 1
    print(f'重评分例数={nv}；跳过无 reading={len(skipped)}: {skipped}')
    print(f'引擎版本不同={len(version_mismatch)}；旧记录缺 features/as_of_year={len(legacy_time)}；'
          f'新旧违规清单不一致={len(violation_mismatch)}: {violation_mismatch}')
    for layer in ('L0', 'L1', 'L2', 'N1'):
        print(f'{layer}: 违规例={case_layer[layer]} '
              f'({case_layer[layer] / max(nv, 1) * 100:.2f}%) 条数={by_layer[layer]}')
    print('\nL2 明细:')
    for cid, detail in sorted(l2_details):
        print(' ', cid, '|', detail)


if __name__ == '__main__':
    main()
