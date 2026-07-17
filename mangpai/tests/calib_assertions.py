# -*- coding: utf-8 -*-
"""calib 金标准断言 runner — 郝金阳10例 × 46项 自动判定 + 回归对比。

金标准与判定规则见 calib_assertions.yaml 头部注释。六维度+层功全部自动判定：
财命方向 / 官命方向 / 应期commit / 层功level / 婚姻 / 职业 / 子息。

用法:
  python3 mangpai/tests/calib_assertions.py                  # 判定并与 YAML baseline 对比
  python3 mangpai/tests/calib_assertions.py --write-baseline # 当前判定写回 YAML baseline
退出码: 有回归(✅/⚠️ -> 更差)则 1，否则 0。
"""
import sys, os
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
for p in (_HERE, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml

from mangpai import MangpaiEngine
from mangpai.subjective.caiming import analyze_caiming
from mangpai.subjective.guanming import analyze_guanming
from mangpai.subjective.hunyin import analyze_hunyin
from mangpai.subjective.zhiye import analyze_zhiye
from mangpai.subjective.liuqin import analyze_liuqin
from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi

YAML_PATH = os.path.join(_HERE, 'calib_assertions.yaml')

_ORDER = {'✅': 0, '⚠️': 1, '❌': 2}


def run_case(case):
    """与 calib_zhenbao.run_case 同口径：引擎全量 + 六主观模块。"""
    gans, zhis = case['gans'], case['zhis']
    gender, year = case.get('gender', '男'), case.get('year', 1960)
    dayun, liunian = case.get('dayun'), case.get('liunian')
    bazi = {
        'year': gans[0] + zhis[0], 'month': gans[1] + zhis[1],
        'day': gans[2] + zhis[2], 'hour': gans[3] + zhis[3],
    }
    bazi_data = {
        'bazi': bazi, 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': gender, 'year': year},
    }
    if dayun:
        bazi_data['dayun'] = {'direction': '顺', 'start_age': 5,
                              'dayun': [{'gz': dayun[0] + dayun[1], 'start_age': 5}]}
    if liunian:
        bazi_data['liunian'] = [{'gz': liunian[0] + liunian[1], 'year': liunian[2]}]
    res = MangpaiEngine(bazi_data).compute_all()
    dg = gans[2]
    out = {
        'res': res,
        'gl': res.get('gongliang', {}),
        'cm': analyze_caiming(dg, gans, zhis),
        'gm': analyze_guanming(dg, gans, zhis),
        'hy': analyze_hunyin(dg, gans, zhis, gender=gender),
        'zy': analyze_zhiye(dg, gans, zhis),
        'lq': analyze_liuqin(dg, gans, zhis, gender=gender),
        'yq': None,
    }
    if dayun or liunian:
        out['yq'] = infer_comprehensive_yingqi(
            dg, gans, zhis,
            dayun_gan=(dayun[0] if dayun else ''), dayun_zhi=(dayun[1] if dayun else ''),
            liunian_gan=(liunian[0] if liunian else ''),
            liunian_zhi=(liunian[1] if liunian else ''))
    return out


# ── 各维度判定规则（rubric 与 YAML 头注释保持一致）──

_XIONG_MARKERS = ['破财', '比劫夺财', '坐牢', '牢狱', '官非', '下浮封顶']
_TIER_RANK = {'贫': 0, '小康': 1, '富': 2, '巨富': 3}


def judge_caiming(gold, cm):
    tier = cm.get('tier', '')
    summary = str(cm.get('summary', ''))
    has_xiong = any(m in summary for m in _XIONG_MARKERS)
    d = gold['direction']
    if d == '破财':
        if has_xiong or tier == '贫':
            return '✅'
        return '⚠️' if tier == '小康' else '❌'
    if d == '凶':  # 因财致祸(坐牢/官非)：需凶向标记，贫=方向不富但漏官非
        if has_xiong:
            return '✅'
        return '⚠️' if tier == '贫' else '❌'
    # 正向 (贫/小康/富/巨富)
    if has_xiong:
        return '❌'
    diff = _TIER_RANK.get(tier, -1) - _TIER_RANK[d]
    v = '✅' if diff == 0 else ('⚠️' if abs(diff) == 1 else '❌')
    if v == '✅' and any(m in summary for m in gold.get('magnitude_absurd_if', [])):
        v = '⚠️'
    return v


def judge_guanming(gold, gm):
    if bool(gm.get('is_guanming')) != bool(gold['is_guanming']):
        return '❌'
    v = '✅'
    gl = gold.get('level')
    if gl is not None:
        lv = gm.get('level', {})
        el = lv.get('level') if isinstance(lv, dict) else None
        if el is None:
            v = '⚠️'
        elif el == gl:
            pass
        elif abs(el - gl) == 1:
            v = '⚠️'
        else:
            return '❌'
    ind = gold.get('industry_contains')
    if v == '✅' and ind:
        hay = str(gm.get('primary_hangye', '')) + str(gm.get('summary', ''))
        if not any(s in hay for s in ind):
            v = '⚠️'
    return v


def judge_yingqi(gold, yq):
    if not yq:
        return '❌'
    concl = str(yq.get('conclusion', ''))
    commit = concl.startswith('应期成立') or concl.startswith('真应期成立')
    return '✅' if commit == bool(gold['commit']) else '❌'


def judge_gongliang(gold, gl):
    lv = gl.get('level')
    if lv is None:
        return '❌'
    if 'level' in gold:
        d = lv - gold['level']
        return '✅' if d == 0 else ('⚠️' if abs(d) == 1 else '❌')
    lo, hi = gold.get('level_min', 0), gold.get('level_max', 4)
    if lo <= lv <= hi:
        return '✅'
    if lv == hi + 1 or lv == lo - 1:
        return '⚠️'
    return '❌'


_HY_ORDER = {'差': 0, '平': 1, '好': 2}


def judge_hunyin(gold, hy):
    q = hy.get('quality', {})
    q = q.get('quality', '') if isinstance(q, dict) else str(q)
    gq = gold['quality']
    d = abs(_HY_ORDER.get(q, -1) - _HY_ORDER[gq])
    v = '✅' if d == 0 else ('⚠️' if d == 1 else '❌')
    if 'duohun' in gold:
        dh = bool(hy.get('duohun', {}).get('is_duohun'))
        if dh != bool(gold['duohun']):
            v = '❌' if v == '⚠️' else '⚠️'  # 降一档
    return v


def judge_zhiye(gold, zy):
    p = zy.get('primary', '') or ''
    if p and p in gold.get('primary_in', []):
        return '✅'
    if p and p in gold.get('partial_in', []):
        return '⚠️'
    if not p:
        return '✅' if gold.get('allow_empty') else '⚠️'
    return '❌'


def judge_zixi(gold, lq):
    hz = lq.get('zixi_youwu', {}).get('has_zixi')
    if hz is None:
        return '❌'
    return '✅' if bool(hz) == bool(gold['has_zixi']) else '❌'


_JUDGES = {
    '财命': lambda gold, out: judge_caiming(gold, out['cm']),
    '官命': lambda gold, out: judge_guanming(gold, out['gm']),
    '应期': lambda gold, out: judge_yingqi(gold, out['yq']),
    '层功': lambda gold, out: judge_gongliang(gold, out['gl']),
    '婚姻': lambda gold, out: judge_hunyin(gold, out['hy']),
    '职业': lambda gold, out: judge_zhiye(gold, out['zy']),
    '子息': lambda gold, out: judge_zixi(gold, out['lq']),
}


def _detail(dim, out):
    if dim == '财命':
        return f"tier={out['cm'].get('tier')}"
    if dim == '官命':
        lv = out['gm'].get('level', {})
        return f"is={out['gm'].get('is_guanming')} lv={lv.get('level') if isinstance(lv, dict) else lv}"
    if dim == '应期':
        return f"concl={str((out['yq'] or {}).get('conclusion', ''))[:18]}"
    if dim == '层功':
        return f"level={out['gl'].get('level')}"
    if dim == '婚姻':
        q = out['hy'].get('quality', {})
        q = q.get('quality') if isinstance(q, dict) else q
        return f"q={q} duohun={out['hy'].get('duohun', {}).get('is_duohun')}"
    if dim == '职业':
        return f"primary={out['zy'].get('primary') or '(空)'}"
    if dim == '子息':
        return f"has_zixi={out['lq'].get('zixi_youwu', {}).get('has_zixi')}"
    return ''


def compute(doc):
    """返回 {(case_id, dim): (verdict, detail)}，按 YAML 顺序。"""
    results = {}
    for case in doc['cases']:
        out = run_case(case)
        for item in case['items']:
            dim = item['dim']
            v = _JUDGES[dim](item['gold'], out)
            results[(case['id'], dim)] = (v, _detail(dim, out))
    return results


def main():
    write_baseline = '--write-baseline' in sys.argv
    doc = yaml.safe_load(open(YAML_PATH, encoding='utf-8'))
    cur = compute(doc)

    cnt = Counter(v for v, _ in cur.values())
    print('=== 当前判定 ===')
    for dim in ['财命', '官命', '婚姻', '职业', '应期', '子息', '层功']:
        c = Counter(v for (cid, d), (v, _) in cur.items() if d == dim)
        if c:
            print(f"  {dim}: ✅{c.get('✅', 0)} ⚠️{c.get('⚠️', 0)} ❌{c.get('❌', 0)}")
    print(f"  TOTAL: ✅{cnt.get('✅', 0)} ⚠️{cnt.get('⚠️', 0)} ❌{cnt.get('❌', 0)}  (n={sum(cnt.values())})")

    n_reg = 0
    reg, imp = [], []
    for case in doc['cases']:
        for item in case['items']:
            key = (case['id'], item['dim'])
            bv = item.get('baseline')
            v, d = cur[key]
            if bv and bv != v:
                if _ORDER[v] > _ORDER[bv]:
                    reg.append((key, bv, v, d))
                else:
                    imp.append((key, bv, v, d))
    print('\n=== vs baseline (calib_assertions.yaml) ===')
    if reg:
        print(f"  ⚠️ REGRESSION ({len(reg)}):")
        for (cid, dim), bv, v, d in reg:
            print(f"    {cid}/{dim}: {bv}->{v}  [{d}]")
    if imp:
        print(f"  ✅ IMPROVE ({len(imp)}):")
        for (cid, dim), bv, v, d in imp:
            print(f"    {cid}/{dim}: {bv}->{v}  [{d}]")
    if not reg and not imp:
        print('  无变化')
    n_reg = len(reg)

    if write_baseline:
        _write_baseline(cur, cnt)
        print(f'\n(baseline 写回 -> {YAML_PATH})')
    sys.exit(1 if n_reg else 0)


def _write_baseline(cur, cnt):
    """按行改写 baseline（保留注释/flow 格式；items 须单行 flow 风格）。"""
    import re
    lines = open(YAML_PATH, encoding='utf-8').read().splitlines(keepends=True)
    case_id = None
    n_sub = 0
    id_re = re.compile(r'^\s+- id: (\S+)')
    item_re = re.compile(r'^(?P<head>\s+- \{dim: (?P<dim>\S+),.*baseline: )[✅⚠️❌](?P<tail>\}.*)$')
    for i, ln in enumerate(lines):
        m = id_re.match(ln)
        if m:
            case_id = m.group(1)
            continue
        m = item_re.match(ln)
        if m and case_id:
            key = (case_id, m.group('dim'))
            if key not in cur:
                raise SystemExit(f'write-baseline: {key} 不在计算结果中（YAML 结构异常）')
            lines[i] = m.group('head') + cur[key][0] + m.group('tail') + '\n'
            n_sub += 1
    if n_sub != len(cur):
        raise SystemExit(f'write-baseline: 替换 {n_sub} 行 != 计算 {len(cur)} 项（YAML 结构异常）')
    # baseline_counts 同步
    txt = ''.join(lines)
    txt = re.sub(r'baseline_counts: \{[^}]*\}',
                 f"baseline_counts: {{✅: {cnt.get('✅', 0)}, ⚠️: {cnt.get('⚠️', 0)}, ❌: {cnt.get('❌', 0)}}}",
                 txt)
    open(YAML_PATH, 'w', encoding='utf-8').write(txt)


if __name__ == '__main__':
    main()
