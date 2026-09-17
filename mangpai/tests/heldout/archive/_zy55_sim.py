# -*- coding: utf-8 -*-
"""职业55❌条款级模拟：从 dump 的 evidence 文本分解每桶 基础分/corroborate分，
模拟条款收窄/删除后 primary 重算，量化 ❌ 翻转收益。纯分析用。"""
import json

d = json.load(open('/tmp/zy55.json'))

# 每桶 evidence 首词 -> 分值（与 zhiye.py 条款一一对应）
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
    """evidence 文本 -> (base分, 各条款[(名,分)])。未匹配行视为 corroborate 外不明条款。"""
    clauses = []
    for line in ev_lines:
        for prefix, val in CLAUSE[bucket]:
            if line.startswith(prefix):
                if val is None:  # 变分条款
                    if bucket == 'accountant':
                        val2 = 2 if '配会计组合' in line else 1
                    elif bucket == 'lawyer':
                        val2 = 2 if '配对抗组合' in line else 1
                    clauses.append((prefix, val2))
                else:
                    clauses.append((prefix, val))
                break
    return clauses


_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')

# 分解 & 校验（base+corro = dump score）
cases = {}
for cid, e in d.items():
    rec = {'gold': set(e['gold_buckets']), 'scores': {}, 'corro': {}}
    for bucket, score in e['scores'].items():
        ev = e['evidence'].get(bucket, [])
        if any('gating' in line for line in ev):
            base, clauses = 0, []
        else:
            clauses = decompose(bucket, ev)
            base = sum(v for _, v in clauses)
        rec['scores'][bucket] = (clauses, score - base)  # (条款list, corroborate分)
        if score - base < 0:
            print(f'WARN decompose {cid} {bucket}: score={score} base={base} ev={ev}')
    cases[cid] = rec


def recompute(rec, adjust):
    """adjust: {bucket: {条款prefix: 新分或None删除}} + ('__corro_scale__', factor)"""
    scores = {}
    cs = adjust.get('__corro_scale__', 1.0)
    for bucket, (clauses, corro) in rec['scores'].items():
        b = 0
        for name, val in clauses:
            ov = adjust.get(bucket, {}).get(name, val)
            if ov is not None:
                b += ov
        scores[bucket] = b + int(round(corro * cs))
    primary = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return primary if scores[primary] >= 6 else ''


def run_sim(name, adjust):
    flips = []
    for cid, rec in cases.items():
        p = recompute(rec, adjust)
        if p != d[cid]['primary']:
            mark = '✅' if p in rec['gold'] else ('⚠️' if p == '' else '❌->' + p)
            flips.append((cid, d[cid]['primary'], p, mark))
    ok = sum(1 for f in flips if f[3] == '✅')
    unk = sum(1 for f in flips if f[3] == '⚠️')
    print(f'\n== {name}: 翻转{len(flips)} (✅{ok} ⚠️空{unk}) ==')
    for f in flips:
        print('  ', f[0], f[1], '->', f[2], f[3])
    return flips


# S1: corroborate 全删（上界测试：换象/包局/夹官/全阳加权全去）
run_sim('S1 corroborate全删', {'__corro_scale__': 0.0})
# S1b: corroborate 每条减半（整体权重×0.5）
run_sim('S1b corroborate×0.5', {'__corro_scale__': 0.5})
# S2: performer 桃花多重计分压平（桃花居日柱+2删、桃花+财+1删）
run_sim('S2 performer桃花压平', {'performer': {'桃花居日柱': None, '桃花+财': None}})
# S3: merchant 泛触条款收窄（门户删、官杀当财删、内食神2->1）
run_sim('S3 merchant收窄', {'merchant': {'财/印在时柱门户': None,
                                         '官杀当财被制': None, '内食神格': 1}})
# S3b: merchant 仅删门户+官杀当财
run_sim('S3b merchant仅删门户+官杀当财', {'merchant': {'财/印在时柱门户': None,
                                                       '官杀当财被制': None}})
# S4: lawyer 收窄（伤官制官2->1、食神制官删、申酉金配对抗2->1）
run_sim('S4 lawyer收窄', {'lawyer': {'伤官制官': 1, '食神制官': None,
                                     '申酉金/辛金': 1}})
# S5: military corroborate 不加（包局/全阳/夹官/换官对military）——用分项模拟:
# 近似=corro全删对military的极端，已在S1覆盖；此处测 成势门2柱（无法从dump模拟，跳过）
# S6: 组合 S2+S3
run_sim('S6 S2+S3组合', {'performer': {'桃花居日柱': None, '桃花+财': None},
                         'merchant': {'财/印在时柱门户': None,
                                      '官杀当财被制': None, '内食神格': 1}})
# S7: 组合 S2+S3+S4
run_sim('S7 S2+S3+S4组合', {'performer': {'桃花居日柱': None, '桃花+财': None},
                            'merchant': {'财/印在时柱门户': None,
                                         '官杀当财被制': None, '内食神格': 1},
                            'lawyer': {'伤官制官': 1, '食神制官': None,
                                       '申酉金/辛金': 1}})
# S8: S7+corro×0.5
run_sim('S8 S7+corro×0.5', {'performer': {'桃花居日柱': None, '桃花+财': None},
                            'merchant': {'财/印在时柱门户': None,
                                         '官杀当财被制': None, '内食神格': 1},
                            'lawyer': {'伤官制官': 1, '食神制官': None,
                                       '申酉金/辛金': 1},
                            '__corro_scale__': 0.5})
