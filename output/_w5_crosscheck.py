"""W5 跨层一致性抽样对照（零 API，只审不改）：引擎特征层 / 锚定行层 / LLM 输出层 逐例对照。

H-fix-7：engine_fe/禁词扫描/无信号判定下沉 output/_eval_common.py
（薄包装，检查口径不变）；`_xm_sanitize` 已随 G3 删除（H10 P0 修复：
改为锚定行直传，desc 不再含「漂亮」措辞由 xiangmao F-N2-1 根治保证）。

用法: /usr/bin/python3 output/_w5_crosscheck.py
产出: stdout（每例三层原文 dump + (a)锚定忠实 (b)LLM语义一致 (c)断链点 自动检查标记）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from mangpai.subjective.llm_prompt import (  # noqa: E402
    _qianyi_anchor, _xiangmao_anchor)
from _eval_common import (  # noqa: E402
    engine_fe, xiangmao_info, xm_forbidden_scan, qianyi_honest_nosignal,
    QIANYI_FORBID, GANZHI_RE)

BATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'llm_batch_20260821_n2_r4')
SAMPLES = ['b67-制例一奥纳西斯', 'b67-复例二副总', 'b67-岳飞', 'gj-影星合杀',
           'yx-部长', 'b67-抢劫', 'cj-运动员', 'famous-唐明皇',
           'b67-初中', 'b67-李嘉诚']
_QIANYI_FORBID = QIANYI_FORBID  # 兼容别名（历史 print 引用名不变）
_GANZHI = GANZHI_RE


def flat_keys(d, prefix=''):
    """特征 JSON 全部点路径（数组不下标），供 basis 出处校验。"""
    out = set()
    if isinstance(d, dict):
        for k, v in d.items():
            p = f'{prefix}.{k}' if prefix else str(k)
            out.add(p)
            out |= flat_keys(v, p)
    elif isinstance(d, list):
        if prefix:
            out.add(prefix)
        for v in d:
            out |= flat_keys(v, prefix)
    return out


def main():
    recs = {}
    for line in open(os.path.join(BATCH, 'batch_0_294.jsonl'),
                     encoding='utf-8'):
        r = json.loads(line)
        if r.get('id') in SAMPLES and r.get('ok') and 'reading' in r:
            recs[r['id']] = r
    cases = {c['id']: c for c in yaml.safe_load(
        open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
             encoding='utf-8'))}

    for cid in SAMPLES:
        r = recs[cid]
        res, fe = engine_fe(cases[cid])
        keys = flat_keys(fe)
        rd = r['reading']
        qy_node = rd.get('迁移') or {}
        xm_node = rd.get('相貌') or {}
        qc = str(qy_node.get('conclusion') or '')
        xc = str(xm_node.get('conclusion') or '')

        qy = fe.get('qianyi') or {}
        yj = qy.get('qianyi_yuanju') or {}
        yq = qy.get('qianyi_yingqi') or {}
        markers = [str(m) for m in (yj.get('markers') or [])]
        moves = yq.get('move_windows') or []
        stays = yq.get('stay_windows') or []
        xm_hits = xiangmao_info(fe, require_desc=True)

        a_qy = _qianyi_anchor(fe)
        a_xm = _xiangmao_anchor(fe)

        print(f'\n{"=" * 76}\n### {cid} ({r.get("name")})')
        print('-- [L1 引擎] 迁移 markers:')
        for m in markers:
            print(f'    {m}')
        for w in moves:
            print(f'    move: {w.get("dayun") or "-"}/{w.get("liunian") or "-"} '
                  f'{w.get("mechanism")} pillar={w.get("pillar")} '
                  f'conf={w.get("confidence")}\n      note={w.get("note")}')
        for w in stays:
            print(f'    stay: {w.get("dayun") or "-"}/{w.get("liunian") or "-"} '
                  f'{w.get("mechanism")} pillar={w.get("pillar")} '
                  f'conf={w.get("confidence")}\n      note={w.get("note")}')
        print(f'    qianyi.summary={qy.get("summary")!r}')
        print(f'    yingqi_desc={yq.get("desc")!r}')
        print('-- [L1 引擎] 相貌命中线:')
        for k, v in xm_hits.items():
            print(f'    {k}: {v}')
        if not xm_hits:
            print('    (无线命中)')
        print(f'-- [L2 锚定] 迁移: {a_qy!r}')
        print(f'-- [L2 锚定] 相貌: {a_xm!r}')
        print(f'-- [L3 LLM] 迁移(conf={qy_node.get("confidence")}): {qc}')
        print(f'    basis={qy_node.get("basis")}')
        print(f'-- [L3 LLM] 相貌(conf={xm_node.get("confidence")}): {xc}')
        print(f'    basis={xm_node.get("basis")}')

        # ---- (a) 锚定行忠实性 ----
        print('-- (a) 锚定忠实性检查:')
        if not markers and not moves:
            ok = '无迁移信号' in a_qy
            print(f'    迁移无信号锚: {"✅" if ok else "❌"}')
        for m in markers:
            print(f'    marker透传: {"✅" if m in a_qy else "❌ 缺失/改写"} 「{m[:28]}…」')
        for w in moves:
            seg = (f"{w.get('dayun') or ''}/{w.get('liunian') or ''}"
                   f" {w.get('mechanism') or ''}({w.get('confidence') or ''})")
            print(f'    迁移窗透传 {seg!r}: {"✅" if seg in a_qy else "❌"}'
                  f'{"  ⚠️note未入锚: " + str(w.get("note")) if str(w.get("note") or "") not in a_qy else ""}')
        for w in stays:
            seg = (f"{w.get('dayun') or ''}/{w.get('liunian') or ''}"
                   f" {w.get('mechanism') or ''}")
            print(f'    安居窗透传 {seg!r}: {"✅" if seg in a_qy else "❌"}'
                  f'{"  ⚠️note未入锚" if str(w.get("note") or "") not in a_qy else ""}')
        eng_gz = set(_GANZHI.findall(' '.join(markers)))
        for w in moves + stays:
            for f in ('dayun', 'liunian'):
                if w.get(f):
                    eng_gz.add(str(w[f]))
        anc_gz = set(_GANZHI.findall(a_qy))
        extra_gz = anc_gz - eng_gz
        if extra_gz:
            print(f'    ❌ 迁移锚含引擎外干支: {extra_gz}')
        if not xm_hits:
            ok = '无显著相貌' in a_xm
            print(f'    相貌无信号锚: {"✅" if ok else "❌"}')
        for k, v in xm_hits.items():
            tag = '✅' if v in a_xm else '❌ 缺失/改写'
            print(f'    相貌线透传[{k}]: {tag}')
        # ---- (b) LLM 语义一致/无臆造 ----
        print('-- (b) LLM 一致性检查:')
        fb = [w for w in _QIANYI_FORBID if w in qc]
        if fb:
            print(f'    ❌ 迁移禁词: {fb}')
        win_gz = set()
        for w in moves + stays:
            for f in ('dayun', 'liunian'):
                if w.get(f):
                    win_gz.add(str(w[f]))
        cited = set(_GANZHI.findall(qc))
        phantom = cited - win_gz
        if phantom:
            print(f'    ⚠️ 迁移维引用锚外干支: {phantom}')
        if moves:
            refd = win_gz & cited
            if refd:
                ok = qy_node.get('confidence') == '低'
                print(f'    应期窗被引用{sorted(refd)} → conf={"低✅" if ok else "❌ " + str(qy_node.get("confidence"))}')
            else:
                print(f'    ⚠️ 引擎有迁移窗但LLM未引用任何窗干支')
            oran = [w for w in moves if w.get('confidence') == '或然']
            if oran:
                has_hedge = any(h in qc for h in ('或', '可能', '未必', '或然'))
                print(f'    或然窗{len(oran)}个 → LLM或然措辞: {"✅" if has_hedge else "❌ 未保住"}')
        if not markers and not moves:
            honest = qianyi_honest_nosignal(qc)
            print(f'    无信号如实: {"✅" if honest else "❌"}: {qc[:40]}')
            b = qy_node.get('basis')
            print(f'    无信号 basis==[]: {"✅" if b == [] else "❌ " + str(b)}')
        # marker 核心短语是否被 LLM 覆盖（遗漏提示，非臆造）
        for m in markers:
            core = re.split(r'（', m)[0]
            probe = core[:6]
            if probe and probe not in qc:
                print(f'    ⚠️ marker核心「{probe}…」未见于LLM迁移文: {core}')
        xfb = xm_forbidden_scan(xc)
        if xfb:
            print(f'    ❌ 相貌禁词: {xfb}')
        if 'meili' in xm_hits or 'shencai' in xm_hits:
            ok = xm_node.get('confidence') == '低'
            print(f'    弱线命中 → conf={"低✅" if ok else "❌ " + str(xm_node.get("confidence"))}')
        if not xm_hits:
            print(f'    无marker如实: {"✅" if "无显著相貌" in xc else "❌"}: {xc[:40]}')
        for k, v in xm_hits.items():
            core = re.split(r'（', v)[0]
            probe = core[:5]
            if probe and probe not in xc:
                print(f'    ⚠️ 相貌线[{k}]核心「{probe}…」未见于LLM相貌文')
        # basis 出处校验
        for dim, node in (('迁移', qy_node), ('相貌', xm_node)):
            b = node.get('basis')
            if isinstance(b, list):
                bad = [x for x in b
                       if str(x).replace('[]', '') not in keys]
                if bad:
                    print(f'    ❌ {dim} basis 臆造键: {bad}')
        v = r.get('violations') or []
        if v:
            print(f'-- 批次留存 violations: {v}')


if __name__ == '__main__':
    main()
