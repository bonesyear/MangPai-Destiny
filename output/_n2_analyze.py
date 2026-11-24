"""N2 七维分析：空记录拒绝、跨维红线分类、名单带来源且防误覆盖。
用法: LLM_BATCH_DIR=<批次目录> T3_OUT_DIR=<分析目录> python3 output/_n2_analyze.py [--force]
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml

from mangpai.subjective.llm_channel import validate_reading
from mangpai.subjective.xiangmao import marker_descriptions
from _eval_common import (
    engine_for_record, load_batch, qianyi_honest_nosignal,
    xiangmao_honest_nosignal, xm_forbidden_scan, QIANYI_FORBID,
    without_fewshot_contamination)

BATCH = os.environ.get('LLM_BATCH_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'llm_batch_20260821_n2_r1')
OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')


def _has_qianyi_signal(fe):
    qy = fe.get('qianyi') or {}
    return bool((qy.get('qianyi_yuanju') or {}).get('markers')
                or (qy.get('qianyi_yingqi') or {}).get('move_windows'))


def _write_ids(path, doc):
    if os.path.exists(path) and '--force' not in sys.argv:
        with open(path, encoding='utf-8') as f:
            old = json.load(f)
        if old != doc:
            raise SystemExit(f'拒绝覆盖已有名单 {path}；确认批次后显式加 --force')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)


def main():
    _, recs = load_batch(BATCH)
    recs = without_fewshot_contamination(recs)
    if not recs:
        raise SystemExit(f'LLM_BATCH_DIR 无可分析记录: {BATCH}')
    with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'), encoding='utf-8') as f:
        cases = {c['id']: c for c in yaml.safe_load(f)}

    case_layer = Counter()
    by_layer = Counter()
    l2_details = []
    qy_forbid_hits = []
    xm_forbid_hits = []
    xm_stats = Counter()
    qy_stats = Counter()
    nv = 0
    for cid, r in sorted(recs, key=lambda item: item['id']):
        if 'reading' not in r:
            continue
        res, fe = engine_for_record(cases[cid], r)
        rep = validate_reading(r['reading'], fe, res)
        nv += 1
        layers = set()
        for v in rep['violations']:
            by_layer[v['layer']] += 1
            layers.add(v['layer'])
            if v['layer'] == 'L2':
                l2_details.append((cid, v))
        for layer in layers:
            case_layer[layer] += 1

        rd = r['reading']
        for dim, node in rd.items():
            text = str((node or {}).get('conclusion') or '')
            for word in QIANYI_FORBID:
                if word in text:
                    qy_forbid_hits.append((cid, dim, word))
            for word, _ctx in xm_forbidden_scan(text):
                xm_forbid_hits.append((cid, dim, word))
        qy_node = rd.get('迁移') or {}
        xm_node = rd.get('相貌') or {}
        qy_basis = ' '.join(str(b) for b in (qy_node.get('basis') or []))
        xm_basis = ' '.join(str(b) for b in (xm_node.get('basis') or []))
        if _has_qianyi_signal(fe):
            qy_stats['sig_total'] += 1
            qy_stats['sig_basis'] += 'qianyi' in qy_basis
        else:
            qy_stats['nosig_total'] += 1
            qy_stats['nosig_honest'] += qianyi_honest_nosignal(
                str(qy_node.get('conclusion') or ''))
        if marker_descriptions(fe.get('xiangmao')):
            xm_stats['mk_total'] += 1
            xm_stats['mk_basis'] += 'xiangmao' in xm_basis
        else:
            xm_stats['nomk_total'] += 1
            xm_stats['nomk_honest'] += xiangmao_honest_nosignal(
                str(xm_node.get('conclusion') or ''))
        if cid == 'zhenbao-23a':
            zy = res.get('zhiye') or {}
            print(f'== zhenbao-23a: zhiye.primary={zy.get("primary")} '
                  f'label={zy.get("primary_label")}')
            print(f'   事业维 conclusion: '
                  f'{str((rd.get("事业") or {}).get("conclusion") or "")[:200]}')
    if nv == 0:
        raise SystemExit(f'LLM_BATCH_DIR 无有效 reading，拒绝写出空名单: {BATCH}')

    os.makedirs(OUT, exist_ok=True)
    l2_ids = sorted({cid for cid, _ in l2_details})
    newdim_ids = sorted({cid for cid, v in l2_details
                         if v.get('kind') in ('qianyi_redline', 'xiangmao_redline')
                         or v['detail'].startswith(('迁移', '相貌'))})
    _write_ids(os.path.join(OUT, 'l2_ids.json'),
               {'batch': BATCH, 'n': nv, 'ids': l2_ids})
    _write_ids(os.path.join(OUT, 'newdim_ids.json'),
               {'batch': BATCH, 'n': nv, 'ids': newdim_ids})

    def is_kind(v, kind, legacy):
        return v.get('kind') == kind or (not v.get('kind') and v['detail'].startswith(legacy))

    qy_v = [(cid, v['detail']) for cid, v in l2_details
            if is_kind(v, 'qianyi_redline', '迁移')]
    xm_v = [(cid, v['detail']) for cid, v in l2_details
            if is_kind(v, 'xiangmao_redline', '相貌')]
    other_v = [(cid, v['detail']) for cid, v in l2_details
               if (cid, v['detail']) not in qy_v + xm_v]
    print(f'\n== N2 分析（{BATCH}）例数={nv}')
    for layer in ('L0', 'L1', 'L2', 'N1'):
        print(f'{layer}: 违规例={case_layer[layer]} '
              f'({case_layer[layer] / max(nv, 1) * 100:.2f}%) 条数={by_layer[layer]}')
    print(f'\n迁移维违规 {len(qy_v)}: {qy_v}')
    print(f'相貌维违规 {len(xm_v)}: {xm_v}')
    print(f'全维原文出境直扫 {len(qy_forbid_hits)}: {qy_forbid_hits}')
    print(f'全维原文相貌直扫 {len(xm_forbid_hits)}: {xm_forbid_hits}')
    print(f'既有 L2（非新维）{len(other_v)}: {other_v}')
    print(f'\n迁移锚定引用率: 有信号 basis 引 qianyi '
          f'{qy_stats["sig_basis"]}/{qy_stats["sig_total"]}；'
          f'无信号如实 {qy_stats["nosig_honest"]}/{qy_stats["nosig_total"]}')
    print(f'相貌锚定引用率: 有 marker basis 引 xiangmao '
          f'{xm_stats["mk_basis"]}/{xm_stats["mk_total"]}；'
          f'无 marker 如实 {xm_stats["nomk_honest"]}/{xm_stats["nomk_total"]}')


if __name__ == '__main__':
    main()
