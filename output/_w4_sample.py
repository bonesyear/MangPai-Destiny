"""W4 七维体验样张抽查（零 API）：r4 存量 reading vs 引擎 marker/锚定行 对照。

H-fix-7：engine_fe/禁词扫描/无信号判定下沉 output/_eval_common.py
（薄包装，检查口径不变）。

用法: /usr/bin/python3 output/_w4_sample.py
产出: stdout（分类清单 + 样张详单 + 自动检查标记）
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from mangpai.subjective.llm_channel import (  # noqa: E402
    validate_reading, format_reading)
from mangpai.subjective.llm_prompt import (  # noqa: E402
    _qianyi_anchor, _xiangmao_anchor)
from _eval_common import (  # noqa: E402
    engine_fe, qianyi_info, xiangmao_info, xm_forbidden_scan,
    qianyi_honest_nosignal, QIANYI_FORBID, GANZHI_RE)

BATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'llm_batch_20260821_n2_r4')
_QIANYI_FORBID = QIANYI_FORBID  # 兼容别名（历史 print 引用名不变）
_GANZHI = GANZHI_RE


def qy_info(fe):
    return qianyi_info(fe)


def xm_info(fe):
    return xiangmao_info(fe)


def lcs(a, b):
    """最长公共子串（重叠度粗测）。"""
    best = ''
    for i in range(len(a)):
        for L in range(min(20, len(a) - i), 3, -1):
            s = a[i:i + L]
            if s in b and len(s) > len(best):
                best = s
    return best


def main():
    recs = {}
    for line in open(os.path.join(BATCH, 'batch_0_294.jsonl'),
                     encoding='utf-8'):
        r = json.loads(line)
        if r.get('ok') and 'reading' in r:
            recs[r['id']] = r
    cases = {c['id']: c for c in yaml.safe_load(
        open('mangpai/tests/trainset/cases.yaml', encoding='utf-8'))}

    rows = {}
    for cid, r in sorted(recs.items()):
        res, fe = engine_fe(cases[cid])
        rows[cid] = {'rec': r, 'fe': fe, 'res': res,
                     'qy': qy_info(fe), 'xm': xm_info(fe)}

    # ---- 分类 ----
    def has_ma_lin(qy):
        return any('马星临' in m for m in qy['markers'])

    qy_strong = [c for c, d in rows.items()
                 if has_ma_lin(d['qy']) and d['qy']['moves']]
    qy_win = [c for c, d in rows.items() if d['qy']['moves']]
    xm_multi = sorted(
        (c for c, d in rows.items() if len(d['xm']) >= 3),
        key=lambda c: -len(rows[c]['xm']))
    xm_weak = [c for c, d in rows.items()
               if 'meili' in d['xm'] or 'shencai' in d['xm']]
    nosig = [c for c, d in rows.items()
             if not d['qy']['markers'] and not d['qy']['moves']
             and not d['xm']]

    print(f'== 分类池: 迁移强(马临年时+应期窗)={len(qy_strong)} {qy_strong}')
    print(f'== 迁移应期窗命中={len(qy_win)}')
    print(f'== 相貌多marker(>=3线)={len(xm_multi)} {xm_multi}')
    print(f'== 相貌弱线命中={len(xm_weak)} {xm_weak}')
    print(f'== 双无信号={len(nosig)} {nosig}')

    picks = []
    for pool, n in ((qy_strong, 3), (xm_multi, 3), (nosig, 2)):
        picks += [c for c in pool if c not in picks][:n]
    for c in qy_win:   # 特殊：应期窗命中（优先非强信号盘）
        if c not in picks:
            picks.append(c)
            break
    for c in xm_weak:  # 特殊：弱线命中
        if c not in picks:
            picks.append(c)
            break
    print(f'\n== 样张 picks({len(picks)}): {picks}')

    # ---- 免责落点（format_reading 渲染验证，取首样张） ----
    r0 = recs[picks[0]]
    rep0 = validate_reading(r0['reading'], rows[picks[0]]['fe'],
                            rows[picks[0]]['res'])
    txt = format_reading(r0['reading'], rep0, r0)
    tail = txt.strip().splitlines()[-1]
    print(f'\n== format_reading 尾部行: 「{tail}」 '
          f'{"✅ 免责在尾" if tail == "命理分析仅供参考，不构成人生决策依据。" else "❌"}')

    # ---- 逐样张详查 ----
    for cid in picks:
        d = rows[cid]
        rd = d['rec']['reading']
        qy, xm = d['qy'], d['xm']
        qy_node = rd.get('迁移') or {}
        xm_node = rd.get('相貌') or {}
        yq_node = rd.get('应期') or {}
        xg_node = rd.get('性格') or {}
        qc = str(qy_node.get('conclusion') or '')
        xc = str(xm_node.get('conclusion') or '')
        print(f'\n{"="*72}\n### {cid} ({d["rec"].get("name")})')
        print(f'-- 引擎迁移: markers={qy["markers"]}')
        for w in qy['moves']:
            print(f'   move: {w.get("dayun")}/{w.get("liunian")} '
                  f'{w.get("mechanism")} conf={w.get("confidence")}')
        for w in qy['stays']:
            print(f'   stay: {w.get("dayun")}/{w.get("liunian")} '
                  f'{w.get("mechanism")} conf={w.get("confidence")}')
        print(f'-- 锚定行: {_qianyi_anchor(d["fe"])!r}')
        print(f'-- LLM迁移({qy_node.get("confidence")}): {qc}')
        print(f'   basis={qy_node.get("basis")}')
        # 迁移检查
        fb = [w for w in _QIANYI_FORBID if w in qc]
        if fb:
            print(f'   ❌ 迁移禁词: {fb}')
        win_gz = {str(w.get('dayun') or '') for w in qy['moves'] + qy['stays']}
        win_gz |= {str(w.get('liunian') or '') for w in qy['moves'] + qy['stays']}
        win_gz.discard('')
        cited = set(_GANZHI.findall(qc))
        phantom = cited - win_gz
        if phantom:
            print(f'   ⚠️ 迁移维引用锚外干支: {phantom}')
        if qy['moves'] and any(w in qc for w in win_gz):
            ok = qy_node.get('confidence') == '低'
            print(f'   应期窗被引用 → confidence={"低✅" if ok else "❌ "+str(qy_node.get("confidence"))}')
        if not qy['markers'] and not qy['moves']:
            honest = qianyi_honest_nosignal(qc)
            print(f'   无信号如实: {"✅" if honest else "❌"}')
        # 相貌检查
        print(f'-- 引擎相貌: {xm}')
        print(f'-- 锚定行: {_xiangmao_anchor(d["fe"])!r}')
        print(f'-- LLM相貌({xm_node.get("confidence")}): {xc}')
        print(f'   basis={xm_node.get("basis")}')
        xfb = xm_forbidden_scan(xc)
        if xfb:
            print(f'   ❌ 相貌禁词: {xfb}')
        if ('meili' in xm or 'shencai' in xm):
            ok = xm_node.get('confidence') == '低'
            print(f'   弱线命中 → confidence={"低✅" if ok else "❌ "+str(xm_node.get("confidence"))}')
        if not xm:
            print(f'   无marker如实: {"✅" if "无" in xc else "❌"}')
        # 重叠/篇幅
        ov1 = lcs(qc, str(yq_node.get('conclusion') or ''))
        ov2 = lcs(xc, str(xg_node.get('conclusion') or ''))
        lens = {dim: len(str((rd.get(dim) or {}).get('conclusion') or ''))
                for dim in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}
        print(f'-- 篇幅: {lens}')
        if ov1:
            print(f'   迁移vs应期最长重叠「{ov1}」({len(ov1)}字)')
        if ov2:
            print(f'   相貌vs性格最长重叠「{ov2}」({len(ov2)}字)')
        v = d['rec'].get('violations') or []
        if v:
            print(f'-- 批次留存 violations: {v}')


if __name__ == '__main__':
    main()
