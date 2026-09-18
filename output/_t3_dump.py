"""T3 端到端审查 · 公共数据 dump（零 API，只测不改）。

复用 v5 批跑 reading（rescore 口径 281 例：glob batch_*.jsonl 同序合并，
主批覆盖 retry——与 _llm_batch_rescore.py 完全同口径），逐例重跑引擎，
落盘：引擎 digest/关键键值、payload features、payload 保真 diff
（scrub 删除项 / zaihuo_llm_view 降级项 / selector 缺失项）、v5 reading。

产出: output/t3_s1/dump.json + output/t3_s1/payload_fidelity.json
用法: python3 output/_t3_dump.py

H-fix-7：引擎重算入口下沉 output/_eval_common.py（engine_fe，构造逐字相同）。
"""
import difflib
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from mangpai.subjective import _resolve, _jsonable, _MISSING  # noqa: E402
from mangpai.subjective.schools import MANGPAI_SCHOOL  # noqa: E402
from mangpai.subjective.narrative import summarize_engine_result, _bazi_line  # noqa: E402
from mangpai.subjective.llm_channel import validate_reading  # noqa: E402
from mangpai.subjective.zaihuo import zaihuo_llm_view  # noqa: E402
from _eval_common import engine_fe  # noqa: E402

OUT_DIR = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1')
V5_DIR = os.environ.get('T3_BATCH_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'llm_batch_20260818_v5')


def _diff_removed(raw, cur, prefix=''):
    """raw(未scrub) vs cur(scrub后) 递归找被删/被改路径。返回 [(path, raw_value摘要)]。"""
    out = []

    def short(v):
        s = json.dumps(v, ensure_ascii=False)
        return s[:80] + ('…' if len(s) > 80 else '')

    if isinstance(raw, dict) and isinstance(cur, dict):
        for k, v in raw.items():
            p = f'{prefix}.{k}' if prefix else str(k)
            if k not in cur:
                out.append((p, short(v)))
            else:
                out.extend(_diff_removed(v, cur[k], p))
    elif isinstance(raw, list) and isinstance(cur, list):
        if all(isinstance(x, str) for x in raw + cur):
            # 字符串列表：SequenceMatcher 定位真实被删条目（scrub 删中段会位移，
            # 尾部归因会张冠李戴——2026-08-18 实测 wood_type.rules 即踩此坑）
            sm = difflib.SequenceMatcher(a=raw, b=cur, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'delete':
                    for x in raw[i1:i2]:
                        out.append((f'{prefix}[-]', short(x)))
                elif tag == 'replace':
                    out.append((f'{prefix}[{i1}..{i2-1}]',
                                f'{short(raw[i1:i2])} → {short(cur[j1:j2])}'))
                elif tag == 'insert':
                    out.append((f'{prefix}[+]', short(cur[j1:j2])))
        elif len(cur) < len(raw):
            out.append((f'{prefix}[{len(cur)}..{len(raw)-1}]',
                        f'{len(raw)-len(cur)} 条被删: {short(raw[len(cur):])}'))
        else:
            for i, (a, b) in enumerate(zip(raw, cur)):
                out.extend(_diff_removed(a, b, f'{prefix}[{i}]'))
    elif raw != cur:
        out.append((prefix, f'{short(raw)} → {short(cur)}'))
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    # v5 记录（rescore 同口径：sorted(glob) 合并，后者覆盖前者——
    # batch_retry.jsonl 字母序在主批后，retry 记录恒赢；修 T3 §A.2 glob 顺序隐患）
    recs = {}
    for p in sorted(glob.glob(os.path.join(V5_DIR, 'batch_*.jsonl'))):
        for line in open(p, encoding='utf-8'):
            r = json.loads(line)
            recs[r['id']] = r
    with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
              encoding='utf-8') as f:
        cases = {c['id']: c for c in yaml.safe_load(f)}

    selectors = MANGPAI_SCHOOL.selectors
    dump = {}
    # 保真聚合
    key_stat = {s: Counter() for s in selectors}  # ok / missing / altered
    scrub_hits = Counter()   # 被 scrub 删除的路径前缀
    zaihuo_drop = Counter()  # zaihuo_llm_view 丢弃的顶层子键
    altered_cases = {}
    n = 0
    for cid, r in sorted(recs.items()):
        if 'reading' not in r:
            continue
        c = cases[cid]
        res, features = engine_fe(c)
        # 离线重校验（复核 v5 违规清单可复现）
        rep = validate_reading(r['reading'], features, res)

        # ---- payload 保真：无 scrub 对照 ----
        raw_payload = {}
        for sel in selectors:
            v = _resolve(res, sel)
            if v is not _MISSING:
                raw_payload[sel] = _jsonable(v)
                key_stat[sel]['ok'] += 1
            else:
                key_stat[sel]['missing'] += 1
        # zaihuo 视图降级明细
        if 'zaihuo' in raw_payload:
            view = zaihuo_llm_view(raw_payload['zaihuo'])
            for k in raw_payload['zaihuo']:
                if k not in view:
                    zaihuo_drop[k] += 1
        removed = _diff_removed(raw_payload, features)
        if removed:
            altered_cases[cid] = removed
            for pth, _ in removed:
                scrub_hits[pth.split('.')[0] + '.' + pth.split('.')[1] if '.' in pth else pth] += 1
            for sel in selectors:
                if sel in raw_payload and json.dumps(raw_payload[sel], ensure_ascii=False, sort_keys=True) \
                        != json.dumps(features.get(sel), ensure_ascii=False, sort_keys=True):
                    key_stat[sel]['altered'] += 1
                    key_stat[sel]['ok'] -= 1

        cm = res.get('caiming') or {}
        gm = res.get('guanming') or {}
        zy = res.get('zhiye') or {}
        hy = res.get('hunyin') or {}
        gl = res.get('gongliang') or {}
        zg = res.get('zuogong') or {}
        dump[cid] = {
            'id': cid, 'name': r.get('name', ''),
            'gender': c.get('gender', '男'), 'year': c.get('year', 1960),
            'verdicts': c.get('verdicts', {}),
            'bazi_line': _bazi_line(res),
            'digest': summarize_engine_result(res),
            'engine_key': {
                'caiming': {k: cm.get(k) for k in
                            ('tier', 'tier_static', 'summary', 'summary_static',
                             'primary_view', 'primary_method', 'xiong', 'level')},
                'guanming': {k: gm.get(k) for k in ('is_guanming', 'level', 'grade', 'summary')},
                'zhiye': {k: zy.get(k) for k in ('primary', 'primary_label', 'base_career', 'scores')},
                'hunyin': hy.get('quality') if isinstance(hy.get('quality'), dict) else {'summary': hy.get('quality')},
                'gongliang': {k: gl.get(k) for k in ('level', 'tier_name', 'score')},
                'zuogong': {k: zg.get(k) for k in ('work_types', 'work_efficiency')},
                'yingqi_subj': (res.get('yingqi_subj') or {}).get('conclusion'),
                'yunfan': {k: (res.get('yunfan') or {}).get(k) for k in
                           ('liunian_fan', 'liunian_ji', 'sui_yun_liandong')},
            },
            'features': features,
            'reading': r['reading'],
            'violations': rep['violations'],
            'payload_removed': removed,
        }
        n += 1

    with open(os.path.join(OUT_DIR, 'dump.json'), 'w', encoding='utf-8') as f:
        json.dump(dump, f, ensure_ascii=False)

    fidelity = {
        'n_cases': n,
        'selectors': {s: dict(key_stat[s]) for s in selectors},
        'scrub_removed_paths': dict(scrub_hits.most_common()),
        'zaihuo_view_dropped_keys': dict(zaihuo_drop.most_common()),
        'altered_case_count': len(altered_cases),
        'altered_cases': altered_cases,
    }
    with open(os.path.join(OUT_DIR, 'payload_fidelity.json'), 'w', encoding='utf-8') as f:
        json.dump(fidelity, f, ensure_ascii=False, indent=1)

    print(f'dump {n} 例 -> {OUT_DIR}/dump.json')
    print(f'保真: selector 缺失={sum(v["missing"] for v in key_stat.values())} '
          f'altered={sum(v["altered"] for v in key_stat.values())} '
          f'altered 例数={len(altered_cases)}')
    print('zaihuo 视图丢弃键:', dict(zaihuo_drop.most_common(8)))
    print('scrub 删除路径 top:', dict(scrub_hits.most_common(8)))


if __name__ == '__main__':
    main()
