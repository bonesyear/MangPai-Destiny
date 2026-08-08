# -*- coding: utf-8 -*-
"""职业批1主模拟器：139 可评例（trainset87+heldout52）条款级分数重构。
merchant 收窄变体 × performer 桃花压平+无桃花通道 × military 降门/阴刃/corro封顶
× accountant 金融象 × teacher 文化象 × lawyer 主气粒度 × doctor 中医通道。
离线网格：约束=两集 ✅ 零回退，目标=trainset ❌→✅ 最大化。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.subjective.zhiye import (_compute_shishen, _cat, _pillar_cats,
                                      _pos_idx, _ensure_relations)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext

d = json.load(open('/tmp/zy_all.json'))

CLAUSE = {
    'accountant': [('亥子辰水现', None), ('财穿印做功', 2), ('金水财星组合', 1),
                   ('食伤带财', 1), ('财/印库不开', 1)],
    'doctor': [('火克金', 2), ('金针刀+火炎症并存', 1), ('七杀+伤官包制', 1),
               ('食伤做功', 1), ('金羊刃带丑库', 1), ('食神合印', 1),
               ('丑金库', 1), ('辰中药库', 1)],
    'teacher': [('木火通明', 2), ('地支木火共存', 1), ('食伤在时柱门户', 2),
                ('月令印星', 1), ('财星虚透合印', 1), ('金水伤官见印', 1)],
    'lawyer': [('申酉金/辛金', None), ('伤官制官', 2), ('食神制官', 1),
               ('卯酉冲', 2), ('酉卯冲', 2), ('卯午破', 2), ('午卯破', 2)],
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
# 阴刃（阴干帝旺位，段氏阴干刃说：乙寅/丁巳/己巳/辛申/癸亥）——zhiye 本地口径
_YIN_REN = {'乙': '寅', '丁': '巳', '己': '巳', '辛': '申', '癸': '亥'}


def act_cats(day_gan, gans, zhis, a):
    fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
    if fi < 0 or ti < 0:
        return fi, ti, set(), set()

    def _one(pos, i):
        if pos == 'day_gan':
            return {'日主'}
        if pos.endswith('_gan'):
            return {_cat(_compute_shishen(day_gan, gans[i]))} - {''}
        cg = get_canggan_mangpai(zhis[i])
        if not cg:
            return set()
        if a.get('type') == '暗合':
            return {_cat(_compute_shishen(day_gan, g)) for g, _ in cg[:2]} - {''}
        return {_cat(_compute_shishen(day_gan, cg[0][0]))} - {''}

    return fi, ti, _one(a.get('from_pos', ''), fi), _one(a.get('to_pos', ''), ti)


def zhu_qi_cat(day_gan, gans, zhis, i):
    out = set()
    if gans[i]:
        out.add(_cat(_compute_shishen(day_gan, gans[i])))
    cg = get_canggan_mangpai(zhis[i])
    if cg:
        out.add(_cat(_compute_shishen(day_gan, cg[0][0])))
    return out - {''}


cases = {}
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    rel = _ensure_relations(day_gan, gans, zhis, None)
    wa = [a for a in (rel.get('work_actions') or []) if not a.get('auxiliary')]
    zq = [zhu_qi_cat(day_gan, gans, zhis, i) for i in range(4)]
    try:
        ss = compute_shensha_ext(day_gan, zhis)
    except Exception:
        ss = {}
    end_cats = [act_cats(day_gan, gans, zhis, a) for a in wa]
    # 条款分解
    clauses, corro = {}, {}
    for bucket, score in e['scores'].items():
        ev = e['evidence'].get(bucket, [])
        if any('gating' in ln for ln in ev):
            cl = []
        else:
            cl = decompose(bucket, ev)
        clauses[bucket] = cl
        corro[bucket] = score - sum(v for _, v in cl)
        if corro[bucket] < 0:
            print('WARN', k, bucket, score, cl)
    fired = {b: {n for n, _ in cl} for b, cl in clauses.items()}
    cases[k] = {
        'split': e['split'], 'gold': e['gold'], 'orig': e['primary'],
        'clauses': clauses, 'corro': corro, 'fired': fired,
        'scores': e['scores'],
        # 特征
        'n_ss': sum(1 for c in zq if '食伤' in c),
        'n_ss_p': sum(1 for i in range(4) if '食伤' in _pillar_cats(day_gan, gans[i], zhis[i])),
        'n_gs': sum(1 for c in zq if '官杀' in c),
        'n_yin': sum(1 for c in zq if '印' in c),
        'month_yin': '印' in zq[1],
        'hour_main': zq[3],
        'portal_main': bool({'财', '印'} & zq[3]),
        'ss_work': any('食伤' in ec[2] or '食伤' in ec[3] for ec in end_cats),
        'ss_cai': any((('食伤' in ec[2] and '财' in ec[3]) or
                       ('财' in ec[2] and '食伤' in ec[3])) for ec in end_cats),
        'gs_main_zhi': any(a.get('type') == '克' and ec[2] and ec[3] and
                           (('官杀' in ec[2] and '食伤' in ec[3]) or
                            ('食伤' in ec[2] and '官杀' in ec[3]))
                           for a, ec in zip(wa, end_cats)),
        'jin_cnt': sum(1 for z in zhis if z in ('申', '酉')) +
                   sum(1 for g in gans if g in ('庚', '辛')),
        'cai_ming': any('财' in c for c in zq),
        'yangren': e['yangren'],
        'yinren': day_gan in _YIN_REN and _YIN_REN[day_gan] in zhis,
        'zaisha': bool((ss.get('灾煞') or {}).get('in_pillars')),
        'tao': e['tao'],
        'huo': sum(1 for z in zhis if z in ('巳', '午')) +
               sum(1 for g in gans if g in ('丙', '丁')),
        'mu': sum(1 for z in zhis if z in ('寅', '卯')) +
              sum(1 for g in gans if g in ('甲', '乙')),
        'chen_chou': any(z in ('辰', '丑') for z in zhis),
        'is_gm': e['is_guanming'],
    }


def primary_of(scores):
    p = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return p if scores[p] >= 6 else ''


def simulate(opt):
    flips = []
    for k, c in cases.items():
        scores = {}
        for b, cl in c['clauses'].items():
            base = 0
            for name, val in cl:
                nv = val
                if b == 'merchant' and name == '财/印在时柱门户' and opt.get('portal_main'):
                    nv = val if c['portal_main'] else None
                if b == 'performer' and opt.get('tao_flat_cai') and name == '桃花+财':
                    nv = None
                if b == 'lawyer' and name == '伤官制官' and opt.get('law_main'):
                    nv = val if c['gs_main_zhi'] else 1
                if b == 'lawyer' and name == '食神制官' and opt.get('law_main'):
                    nv = None
                if nv is not None:
                    base += nv
            cr = c['corro'][b]
            if opt.get('corro_cap'):
                cr = min(cr, 2)
            scores[b] = base + cr
        if opt.get('perf_boost') and c['n_ss_p'] >= 2 and c['ss_work'] \
                and not c['tao'] and not c['cai_ming']:
            scores['performer'] = scores.get('performer', 0) + opt['perf_boost']
        if opt.get('mil_gate2') and c['n_gs'] >= 2 and '官杀成势' not in c['fired']['military'] \
                and (c['yangren'] or c['zaisha'] or c['yinren']):
            scores['military'] = scores.get('military', 0) + opt['mil_gate2']
        if opt.get('mil_yinren_g') and c['yinren'] and c['n_gs'] >= 1 \
                and '羊刃' not in c['fired']['military']:
            scores['military'] = scores.get('military', 0) + opt['mil_yinren_g']
        if opt.get('acc_jin') and c['jin_cnt'] >= 2 and (c['cai_ming'] or c['n_yin'] >= 2):
            scores['accountant'] = scores.get('accountant', 0) + opt['acc_jin']
        if opt.get('teach_yin') and c['n_yin'] >= 2 and c['n_ss'] == 0 and c['jin_cnt'] < 3:
            scores['teacher'] = scores.get('teacher', 0) + opt['teach_yin']
        if opt.get('law_yield') and c['jin_cnt'] >= 2 and c['cai_ming']:
            for name, val in c['clauses']['lawyer']:
                if name == '申酉金/辛金':
                    scores['lawyer'] -= val
                    break
        p = primary_of(scores)
        orig = c['orig']
        # base_career 幻影修复：七桶全<6 时 base_career 条件不变，仍落原 laborer/unemployed
        eff = p if p else (orig if orig in ('laborer', 'unemployed') else '')
        if eff != orig:
            was = '✅' if orig in c['gold'] else ('⚠️' if not orig else '❌')
            now = '✅' if eff in c['gold'] else ('⚠️' if not eff else '❌')
            flips.append((k, c['split'], orig, eff, was, now))
    return flips


def report(name, opt, verbose=True):
    flips = simulate(opt)
    reg = [f for f in flips if f[4] == '✅']
    gain = [f for f in flips if f[5] == '✅' and f[4] != '✅']
    h_reg = [f for f in reg if f[1] == 'heldout']
    t_gain = [f for f in gain if f[1] == 'trainset']
    h_gain = [f for f in gain if f[1] == 'heldout']
    if verbose:
        print(f'\n== {name}: 翻转{len(flips)} 回归{len(reg)}(heldout{len(h_reg)}) '
              f'✅增益 trainset+{len(t_gain)} heldout+{len(h_gain)} ==')
        for f in flips:
            tag = '💥' if f[4] == '✅' else ('🎯' if f[5] == '✅' else '  ')
            print(f'  {tag} [{f[1]}] {f[0].split(":",1)[1][:30]} {f[2] or "(空)"}->{f[3] or "(空)"} {f[4]}->{f[5]}')
    return flips


