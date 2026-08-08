# -*- coding: utf-8 -*-
"""职业55❌ fn侧加信号模拟：重算八字结构特征（食伤/官杀柱数、桃花、羊刃、财五行），
在条款分解基础上模拟「对桶 boost + 错桶收窄」组合。纯分析用。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.subjective.zhiye import (_pillar_cats, _compute_shishen,
                                      _MIN_SCORE_THRESHOLD)
from mangpai.objective.shensha import compute_shensha_ext

d = json.load(open('/tmp/zy55.json'))

CLAUSE = {
    'accountant': [('亥子辰水现', None), ('财穿印做功', 2), ('金水财星组合', 1),
                   ('食伤带财', 1), ('财/印库不开', 1)],
    'doctor': [('火克金', 2), ('金针刀+火炎症并存', 1), ('七杀+伤官包制', 1),
               ('食伤做功', 1), ('金羊刃带丑库', 1), ('食神合印', 1),
               ('丑金库', 1), ('辰中药库', 1)],
    'teacher': [('木火通明', 2), ('地支木火共存', 1), ('食伤在时柱门户', 2),
                ('月令印星', 1), ('财星虚透合印', 1), ('金水伤官见印', 1)],
    'lawyer': [('申酉金/辛金', None), ('伤官制官', 2), ('食神制官', 1),
               ('卯酉冲', 2), ('卯午破', 2)],
    'merchant': [('财星入局做功', 2), ('主位合财/制财做功', 2), ('食伤生财做功', 2),
                 ('财/印在时柱门户', 1), ('官杀当财被制', 1), ('冲财做功', 1),
                 ('自坐财库', 1), ('内食神格', 2), ('坐根制财', 2),
                 ('金水→', 0), ('木火→', 0), ('土金→', 0), ('火土→', 0)],
    'military': [('官杀成势', 2), ('七杀透干', 1), ('羊刃', 1), ('灾煞', 1),
                 ('申酉金/辛（律令', 1)],
    'performer': [('食伤+桃花+财', 4), ('食伤+桃花（', 3), ('桃花+财', 1),
                  ('桃花居日柱', 2), ('食伤在时柱门户', 1), ('丙丁火+桃花', 1)],
}


def decompose(bucket, ev_lines):
    clauses = []
    for line in ev_lines:
        for prefix, val in CLAUSE[bucket]:
            if line.startswith(prefix):
                if val is None:
                    val2 = (2 if '配会计组合' in line else 1) if bucket == 'accountant' \
                        else (2 if '配对抗组合' in line else 1)
                    clauses.append((prefix, val2))
                else:
                    clauses.append((prefix, val))
                break
    return clauses


_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')

# ── 结构特征重算 ──
cases = {}
for cid, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    pcats = [_pillar_cats(day_gan, gans[i], zhis[i]) for i in range(4)]
    n_shishang = sum(1 for c in pcats if '食伤' in c)
    n_guansha = sum(1 for c in pcats if '官杀' in c)
    n_yin = sum(1 for c in pcats if '印' in c)
    try:
        ss = compute_shensha_ext(day_gan, zhis)
    except Exception:
        ss = {}
    yangren = bool((ss.get('羊刃') or {}).get('in_pillars'))
    tao = bool((ss.get('桃花') or {}).get('in_pillars'))
    hour_shishang = '食伤' in pcats[3]
    scores, corros = {}, {}
    for bucket, score in e['scores'].items():
        ev = e['evidence'].get(bucket, [])
        if any('gating' in line for line in ev):
            clauses = []
        else:
            clauses = decompose(bucket, ev)
        scores[bucket] = clauses
        corros[bucket] = score - sum(v for _, v in clauses)
    cases[cid] = {'gold': set(e['gold_buckets']), 'scores': scores,
                  'corro': corros, 'n_shishang': n_shishang,
                  'n_guansha': n_guansha, 'n_yin': n_yin,
                  'yangren': yangren, 'tao': tao,
                  'hour_shishang': hour_shishang,
                  'orig_primary': e['primary']}

# 特征分布速览（fn 侧验证）
print('== 金标桶 vs 结构特征 ==')
for feat in ('n_shishang', 'n_guansha'):
    print(f'-- {feat} --')
    from collections import Counter, defaultdict
    m = defaultdict(Counter)
    for cid, rec in cases.items():
        g = '+'.join(sorted(rec['gold']))
        m[g][rec[feat]] += 1
    for g, c in sorted(m.items()):
        print(f'  {g}: {dict(sorted(c.items()))}')
print('-- 桃花×金标桶 --')
from collections import Counter, defaultdict
m = defaultdict(Counter)
for cid, rec in cases.items():
    g = '+'.join(sorted(rec['gold']))
    m[g][rec['tao']] += 1
for g, c in sorted(m.items()):
    print(f'  {g}: 桃花={dict(c)}')
print('-- 羊刃×military金标 --')
for cid, rec in cases.items():
    if 'military' in rec['gold']:
        print(f'  {cid}: 羊刃={rec["yangren"]} 官杀柱={rec["n_guansha"]}')


# ── fn侧 boost 模拟 ──
def recompute2(rec, adj_clauses, boosts, corro_scale=1.0):
    scores = {}
    for bucket, clauses in rec['scores'].items():
        b = 0
        for name, val in clauses:
            ov = adj_clauses.get(bucket, {}).get(name, val)
            if ov is not None:
                b += ov
        scores[bucket] = b + int(round(rec['corro'][bucket] * corro_scale))
    for bucket, func, val in boosts:
        if func(rec):
            scores[bucket] = scores.get(bucket, 0) + val
    primary = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return primary if scores[primary] >= 6 else '', scores


def run2(name, adj_clauses=None, boosts=(), corro_scale=1.0, verbose=True):
    adj_clauses = adj_clauses or {}
    flips = []
    for cid, rec in cases.items():
        p, _s = recompute2(rec, adj_clauses, boosts, corro_scale)
        if p != rec['orig_primary']:
            mark = '✅' if p in rec['gold'] else ('⚠️' if p == '' else '❌->' + p)
            flips.append((cid, rec['orig_primary'], p, mark))
    ok = sum(1 for f in flips if f[3] == '✅')
    unk = sum(1 for f in flips if f[3] == '⚠️')
    wrong = len(flips) - ok - unk
    if verbose:
        print(f'\n== {name}: 翻转{len(flips)} (✅{ok} ⚠️空{unk} 换错桶{wrong}) ==')
        for f in flips:
            print('  ', f[0], f[1], '->', f[2], f[3])
    return flips


# 结构谓词
def has_cai(rec):
    return any(any('财' in c for c in e['evidence'].get(b, [])) for b in ('merchant', 'accountant'))


# B_acc: 金融象——申酉金重+财金/水 → accountant+2（书：金=金融/银行）
def _jin_heavy(rec):
    return rec.get('_jin_cnt', 0) >= 2


# 预计算申酉金柱数（支申酉+干庚辛）
for cid, rec in cases.items():
    bz = d[cid]['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    rec['_jin_cnt'] = sum(1 for z in zhis if z in ('申', '酉')) + \
        sum(1 for g in gans if g in ('庚', '辛'))
    rec['_is_gm'] = d[cid]['is_guanming']

NARROW = {
    'performer': {'桃花居日柱': None, '桃花+财': None},
    'merchant': {'财/印在时柱门户': None, '官杀当财被制': None},
}

# B1: accountant 金融象（申酉金重≥2 → +2）
run2('B1 accountant金融+2', NARROW,
     [('accountant', _jin_heavy, 2)])
# B2: military 官命联动（is_guanming+官杀≥2 → +3；羊刃+官杀≥1 → +2）
run2('B2 military官命联动', NARROW,
     [('military', lambda r: r['_is_gm'] and r['n_guansha'] >= 2, 3),
      ('military', lambda r: r['yangren'] and r['n_guansha'] >= 1, 2)])
# B3: performer 食伤成象（食伤≥2柱 → +2，替代桃花）
run2('B3 performer食伤≥2+2', NARROW,
     [('performer', lambda r: r['n_shishang'] >= 2, 2)])
# B4: teacher 月令印+食伤时柱（文化成象 → +2）
run2('B4 teacher印+食伤门户+2', NARROW,
     [('teacher', lambda r: r['n_yin'] >= 1 and r['hour_shishang'], 2)])
# B5: 全组合
run2('B5 全组合 B1+B2+B3+B4', NARROW,
     [('accountant', _jin_heavy, 2),
      ('military', lambda r: r['_is_gm'] and r['n_guansha'] >= 2, 3),
      ('military', lambda r: r['yangren'] and r['n_guansha'] >= 1, 2),
      ('performer', lambda r: r['n_shishang'] >= 2, 2),
      ('teacher', lambda r: r['n_yin'] >= 1 and r['hour_shishang'], 2)])
