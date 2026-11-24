"""N2 加严抽样：校验名单与 dump 同源，冻结 dump 哈希和分层键。"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (
    load_id_file, load_json, stratified_fill, stratification_key,
    without_fewshot_contamination)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')
SEED = 20260821
N = 30


def main():
    dump = without_fewshot_contamination(load_json(os.path.join(OUT, 'dump.json')))
    source = load_json(os.path.join(OUT, 'dump_source.json'))
    l2_doc, l2 = load_id_file(os.path.join(OUT, 'l2_ids.json'))
    newdoc, newdim = load_id_file(os.path.join(OUT, 'newdim_ids.json'))
    for doc in (l2_doc, newdoc):
        if doc['batch'] is not None and doc['batch'] != source['batch']:
            raise ValueError(f'名单与 dump 来源批次不一致: {doc["batch"]} != {source["batch"]}')
    l2, newdim = set(l2), set(newdim)
    rng = random.Random(SEED)
    forced = list(dict.fromkeys(sorted(newdim) + ['zhenbao-23a'] + sorted(l2)))
    forced = [cid for cid in forced if cid in dump]
    fill = stratified_fill(dump, forced, N, rng)
    sample = forced + fill
    out = {
        'seed': SEED, 'newdim': sorted(newdim), 'l2': sorted(l2),
        'forced': forced, 'fill': fill, 'sample': sample,
        'dump_sha256': source['dump_sha256'],
        'strata': {cid: stratification_key(dump[cid]) for cid in sample},
    }
    with open(os.path.join(OUT, 'sample30.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'forced {len(forced)} = 新维 {len(newdim)} + zhenbao-23a + L2 '
          f'{len(l2)}; fill {len(fill)}; 合计 {len(sample)}')
    print('forced:', json.dumps(forced, ensure_ascii=False))
    print('fill:', json.dumps(fill, ensure_ascii=False))


if __name__ == '__main__':
    main()
