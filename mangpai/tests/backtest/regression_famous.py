# -*- coding: utf-8 -*-
"""K6: 名人命例回归（《段氏理象学研究》附录博客文粹 20+ 例）。principled judge，跟踪 ✅/⚠️/❌。
用法:
  python3 mangpai/tests/backtest/regression_famous.py                  # 与 famous_baseline.json 对比
  python3 mangpai/tests/backtest/regression_famous.py --write-baseline # 当前判定写回 famous_baseline.json
  python3 mangpai/tests/backtest/regression_famous.py <other_baseline.json>
退出码: 有回归(✅/⚠️ -> 更差)则 1，否则 0。
判定口径（复用 regression67 语义）:
  zuogong : primary 命中书集 ✅；书集∩types 非 primary ⚠️；不在 types ❌
  gongliang: level 差 0 ✅；±1 ⚠️；其余 ❌
  guanming: is_guanming == 书断 ✅/❌
  caiming : 原局 tier_static 在书档集 ✅；相邻档 ⚠️；隔档 ❌（P0-a 口径：书断命=原局，取 tier_static）
  zhiye   : primary 命中书集 ✅；无明确倾向(空/fallback) ⚠️；其余 ❌
  hunyin/laoyu: 值相等 ✅/❌（同 regression67 cat5）
"""
import sys, json, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness import run
from famous_cases import FAMOUS, DROPPED

DEFAULT_BASELINE = os.path.join(_HERE, 'famous_baseline.json')
CURRENT_OUT = os.path.join(_HERE, 'current_famous.json')

VALID = set('甲乙丙丁戊己庚辛壬癸')
def fg(g): return ['己' if x == '已' else x for x in g]

_TIER_ORDER = ['贫', '小康', '富', '巨富']

def judge_zuogong(zg, book_set):
    pt = zg['primary_work']['type']
    types = set(zg['work_types'])
    if pt in book_set:
        return '✅'
    if types & book_set:
        return '⚠️'
    return '❌'

def judge_gongliang(gl, book_lv):
    d = gl['level'] - book_lv
    if d == 0: return '✅'
    if abs(d) == 1: return '⚠️'
    return '❌'

def judge_caiming(cm, book_tiers):
    tier = cm.get('tier_static') or cm.get('tier', '')
    if tier in book_tiers:
        return '✅'
    # 相邻档 ⚠️（与书档集最近距离 1）
    if tier in _TIER_ORDER:
        i = _TIER_ORDER.index(tier)
        dist = min(abs(i - _TIER_ORDER.index(t)) for t in book_tiers if t in _TIER_ORDER)
        if dist == 1:
            return '⚠️'
    return '❌'

def judge_zhiye(zy, book_prim):
    primary = zy.get('primary', '')
    if primary in book_prim:
        return '✅'
    if not primary or zy.get('fallback_no_clear'):
        return '⚠️'
    return '❌'

def judge_case(name, gans, zhis, gender, dims):
    """返回 {key: (verdict, detail)}，一书例可出多维度判定。"""
    out = {}
    r = run(fg(gans), zhis, gender=gender)
    if 'zuogong_primary_in' in dims:
        zg = r['zuogong']
        bset = set(dims['zuogong_primary_in'])
        out[f'zg:{name}'] = (judge_zuogong(zg, bset),
                             f"types={zg['work_types']} primary={zg['primary_work']['type']} 书={sorted(bset)}")
    if 'gongliang_level' in dims:
        gl = r['gongliang']
        blv = dims['gongliang_level']
        out[f'gl:{name}'] = (judge_gongliang(gl, blv),
                             f"level={gl['level']}(书{blv}) score={gl['score']}")
    if 'guanming' in dims:
        gm = r['guanming']
        exp = dims['guanming']
        got = gm.get('is_guanming')
        out[f'gm:{name}'] = ('✅' if got == exp else '❌',
                             f"is_guanming={got} 书={exp} combo={gm.get('combo_type', '')}")
    if 'caiming_tier_in' in dims:
        cm = r['caiming']
        bt = dims['caiming_tier_in']
        out[f'cm:{name}'] = (judge_caiming(cm, bt),
                             f"tier_static={cm.get('tier_static')} tier={cm.get('tier')} 书={bt}")
    if 'zhiye_primary_in' in dims:
        zy = r['zhiye']
        bp = dims['zhiye_primary_in']
        out[f'zy:{name}'] = (judge_zhiye(zy, bp),
                             f"primary={zy.get('primary')!r}({zy.get('primary_label', '')}) 书={bp}")
    if 'hunyin_quality' in dims:
        hy = r.get('hunyin', {}).get('quality', {}).get('quality', '')
        exp = dims['hunyin_quality']
        out[f'hy:{name}'] = ('✅' if hy == exp else '❌', f"quality={hy} 书={exp}")
    if 'laoyu_risk' in dims:
        ly = r.get('laoyu', {}).get('risk', '')
        exp = dims['laoyu_risk']
        out[f'ly:{name}'] = ('✅' if ly == exp else '❌', f"risk={ly} 书={exp}")
    return out

def compute():
    out = {}
    for name, g, z, gender, dims, note in FAMOUS:
        for k, v in judge_case(name, g, z, gender, dims).items():
            out[k] = v
    return out

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write_baseline = '--write-baseline' in sys.argv
    cur = compute()
    base_path = args[0] if args else DEFAULT_BASELINE
    from collections import Counter
    cnt = Counter(v for v, _ in cur.values())
    def cat_stats(prefix):
        c = Counter()
        for k, (v, _) in cur.items():
            if k.startswith(prefix):
                c[v] += 1
        return c
    print("=== 名人命例·当前判定 ===")
    for pref, label in [('zg:', 'zuogong 主做功'), ('gl:', 'gongliang 层功'),
                        ('gm:', 'guanming 官命'), ('cm:', 'caiming 财档'),
                        ('zy:', 'zhiye 职业'), ('hy:', 'hunyin 婚姻'), ('ly:', 'laoyu 牢狱')]:
        c = cat_stats(pref)
        if c:
            print(f"  {label}: ✅{c.get('✅',0)} ⚠️{c.get('⚠️',0)} ❌{c.get('❌',0)}")
    print(f"  TOTAL: ✅{cnt.get('✅',0)} ⚠️{cnt.get('⚠️',0)} ❌{cnt.get('❌',0)}  (n={sum(cnt.values())}, cases={len(FAMOUS)}, dropped={len(DROPPED)})")
    print("\n=== 明细 ===")
    for k, (v, d) in cur.items():
        print(f"  {v} {k}: {d}")
    n_reg = 0
    if base_path and os.path.exists(base_path):
        base = json.load(open(base_path))
        print(f"\n=== vs baseline ({os.path.basename(base_path)}) ===")
        reg, imp = [], []
        for k, (v, d) in cur.items():
            bv = base.get(k, {}).get('verdict')
            if bv and bv != v:
                order = {'✅': 0, '⚠️': 1, '❌': 2}
                if order[v] > order[bv]:
                    reg.append((k, bv, v, d))
                else:
                    imp.append((k, bv, v, d))
        n_reg = len(reg)
        if reg:
            print(f"  ⚠️ REGRESSION ({len(reg)}):")
            for k, bv, v, d in reg:
                print(f"    {k}: {bv}->{v}  [{d}]")
        if imp:
            print(f"  ✅ IMPROVE ({len(imp)}):")
            for k, bv, v, d in imp:
                print(f"    {k}: {bv}->{v}  [{d}]")
        if not reg and not imp:
            print("  无变化")
    else:
        print(f"\n(baseline 不存在: {base_path}，仅打印当前判定)")
    arch = {k: {'verdict': v, 'detail': d} for k, (v, d) in cur.items()}
    out_path = DEFAULT_BASELINE if write_baseline else CURRENT_OUT
    json.dump(arch, open(out_path, 'w'), ensure_ascii=False, indent=1)
    print(f"\n(archived -> {out_path})")
    sys.exit(1 if n_reg else 0)

if __name__ == '__main__':
    main()
