"""N2 七维复测 · 新维指标分析（零 API，只吃批次留存 reading）。

指标：
- 迁移维红线违规（出国/移民/海外/国外/外国）——来自校验器 L2 detail
- 相貌维违规（漂亮/美/丑/帅，排除窗美元/丑时/X丑）——同上
- 锚定行引用率：有信号例 basis 引 qianyi/xiangmao 键占比 + 无信号例如实率
  （迁移无信号例 conclusion 含「无」且不含迁移/远行断言；相貌无 marker 例
  conclusion 含「无」表述）
- 既有层回归：L0/L1/N1/L2 全量（rescore 同口径）
- zhenbao-23a 强制集：打印事业维 conclusion + 引擎 zhiye.primary 供人工核

H-fix-7：引擎重算入口/迁移禁词表/无信号判定下沉 output/_eval_common.py
（薄包装，统计口径不变）。

产出: stdout + $T3_OUT_DIR/l2_ids.json + newdim_ids.json
用法: LLM_BATCH_DIR=output/llm_batch_20260821_n2_r1 \
      T3_OUT_DIR=output/t3_s1_n2 /usr/bin/python3 output/_n2_analyze.py
"""
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from mangpai.subjective.llm_channel import validate_reading  # noqa: E402
from mangpai.subjective.xiangmao import marker_descriptions  # noqa: E402
from _eval_common import (  # noqa: E402
    engine_fe, qianyi_honest_nosignal, QIANYI_FORBID)

BATCH = os.environ.get('LLM_BATCH_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'llm_batch_20260821_n2_r1')
OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')

_QIANYI_FORBID = QIANYI_FORBID


def _has_qianyi_signal(fe):
    qy = fe.get('qianyi') or {}
    yj = qy.get('qianyi_yuanju') or {}
    yq = qy.get('qianyi_yingqi') or {}
    return bool(yj.get('markers') or yq.get('move_windows'))


def _has_xiangmao_marker(fe):
    # G2（W2 统计口径裁定后置项）：按「hit 且 desc 非空」判定——原只看 hit
    # 不看 desc，独癸类（yan.gui=True 但 desc 空）16 例误计「有 marker」；
    # 对齐锚定行口径后 251/251=100%。
    # H-fix-4b：判定下沉 mangpai.subjective.xiangmao.marker_descriptions
    # （与 llm_prompt._xiangmao_anchor 同一判据），本函数=薄包装。
    return bool(marker_descriptions(fe.get('xiangmao')))


def main():
    recs = {}
    for p in sorted(glob.glob(os.path.join(BATCH, 'batch_*.jsonl'))):
        for line in open(p, encoding='utf-8'):
            r = json.loads(line)
            recs[r['id']] = r
    cases = {c['id']: c for c in yaml.safe_load(
        open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
             encoding='utf-8'))}

    case_layer = Counter()
    by_layer = Counter()
    l2_details = []
    qy_forbid_hits = []   # 迁移维红线（原文直扫，复核校验器）
    xm_stats = Counter()
    qy_stats = Counter()
    nv = 0
    for cid, r in sorted(recs.items()):
        if 'reading' not in r:
            continue
        c = cases[cid]
        res, fe = engine_fe(c)
        rep = validate_reading(r['reading'], fe, res)
        nv += 1
        layers = set()
        for v in rep['violations']:
            by_layer[v['layer']] += 1
            layers.add(v['layer'])
            if v['layer'] == 'L2':
                l2_details.append((cid, v['detail']))
        for L in layers:
            case_layer[L] += 1

        rd = r['reading']
        qy_node = rd.get('迁移') or {}
        xm_node = rd.get('相貌') or {}
        qy_text = str(qy_node.get('conclusion') or '')
        xm_text = str(xm_node.get('conclusion') or '')
        qy_basis = ' '.join(str(b) for b in (qy_node.get('basis') or []))
        xm_basis = ' '.join(str(b) for b in (xm_node.get('basis') or []))

        # 迁移维原文红线直扫（与校验器互核）
        for w in _QIANYI_FORBID:
            if w in qy_text:
                qy_forbid_hits.append((cid, w))

        # 锚定行引用率
        if _has_qianyi_signal(fe):
            qy_stats['sig_total'] += 1
            if 'qianyi' in qy_basis:
                qy_stats['sig_basis'] += 1
        else:
            qy_stats['nosig_total'] += 1
            # 如实率：说「无…迁移/远行信号」类表述，且不断言迁移
            honest = qianyi_honest_nosignal(qy_text)
            if honest:
                qy_stats['nosig_honest'] += 1
        if _has_xiangmao_marker(fe):
            xm_stats['mk_total'] += 1
            if 'xiangmao' in xm_basis:
                xm_stats['mk_basis'] += 1
        else:
            xm_stats['nomk_total'] += 1
            if '无' in xm_text:
                xm_stats['nomk_honest'] += 1

        # zhenbao-23a 强制集
        if cid == 'zhenbao-23a':
            zy = (res.get('zhiye') or {})
            print(f'== zhenbao-23a: zhiye.primary={zy.get("primary")} '
                  f'label={zy.get("primary_label")}')
            print(f'   事业维 conclusion: '
                  f'{str((rd.get("事业") or {}).get("conclusion") or "")[:200]}')

    os.makedirs(OUT, exist_ok=True)
    l2_ids = sorted({cid for cid, _ in l2_details})
    newdim_ids = sorted({cid for cid, d in l2_details
                         if d.startswith('迁移') or d.startswith('相貌')})
    json.dump(l2_ids, open(os.path.join(OUT, 'l2_ids.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump(newdim_ids, open(os.path.join(OUT, 'newdim_ids.json'), 'w',
                               encoding='utf-8'), ensure_ascii=False)

    print(f'\n== N2 分析（{BATCH}）例数={nv}')
    for L in ('L0', 'L1', 'L2', 'N1'):
        print(f'{L}: 违规例={case_layer[L]} '
              f'({case_layer[L]/max(nv,1)*100:.2f}%) 条数={by_layer[L]}')
    qy_v = [(c, d) for c, d in l2_details if d.startswith('迁移')]
    xm_v = [(c, d) for c, d in l2_details if d.startswith('相貌')]
    other_v = [(c, d) for c, d in l2_details
               if not d.startswith('迁移') and not d.startswith('相貌')]
    print(f'\n迁移维违规 {len(qy_v)}: {qy_v}')
    print(f'相貌维违规 {len(xm_v)}: {xm_v}')
    print(f'迁移维原文红线直扫命中 {len(qy_forbid_hits)}: {qy_forbid_hits}')
    print(f'既有 L2（非新维）{len(other_v)}: {other_v}')
    print(f'\n迁移锚定引用率: 有信号 basis 引 qianyi '
          f'{qy_stats["sig_basis"]}/{qy_stats["sig_total"]}；'
          f'无信号如实 {qy_stats["nosig_honest"]}/{qy_stats["nosig_total"]}')
    print(f'相貌锚定引用率: 有 marker basis 引 xiangmao '
          f'{xm_stats["mk_basis"]}/{xm_stats["mk_total"]}；'
          f'无 marker 如实 {xm_stats["nomk_honest"]}/{xm_stats["nomk_total"]}')


if __name__ == '__main__':
    main()
