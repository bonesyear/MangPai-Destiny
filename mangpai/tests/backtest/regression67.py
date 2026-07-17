# -*- coding: utf-8 -*-
"""第二层审查·67例全量回归。principled judge，跟踪 ✅/⚠️/❌ deltas。
用法:
  python3 mangpai/tests/backtest/regression67.py            # 与内置 baseline67.json 对比
  python3 mangpai/tests/backtest/regression67.py --write-baseline  # 当前判定写回 baseline67.json
  python3 mangpai/tests/backtest/regression67.py <other_baseline.json>
退出码: 有回归(✅/⚠️ -> 更差)则 1，否则 0。
"""
import sys, json, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from harness import zuogong, gongliang, run

DEFAULT_BASELINE = os.path.join(_HERE, 'baseline67.json')
CURRENT_OUT = os.path.join(_HERE, 'current67.json')

VALID = set('甲乙丙丁戊己庚辛壬癸')
def fg(g): return ['己' if x == '已' else x for x in g]

# ── 类目1: zuogong (18) ──
# (name, gans, zhis, book_primary_set, level_cap_or_None)
# judge: primary in book_set -> ✅ (若 level>cap 则 ⚠️); book_set∩types 且非primary -> ⚠️; 不在types -> ❌
CAT1 = [
    ('制例一奥纳西斯', ['乙','己','已','庚'], ['巳','丑','未','午'], {'制用'}, 4),
    ('制例二',         ['丙','辛','戊','壬'], ['午','丑','寅','戌'], {'制用'}, 4),
    ('制例三',         ['癸','戊','己','甲'], ['卯','午','酉','戌'], {'制用'}, None),
    ('化例一',         ['壬','丙','戊','乙'], ['寅','午','寅','卯'], {'化用'}, None),
    ('化例二',         ['戊','壬','丙','壬'], ['申','戌','寅','辰'], {'化用'}, None),
    ('化例三中堂',     ['甲','丙','已','甲'], ['子','寅','丑','子'], {'化用'}, None),
    ('生例一富婆',     ['辛','庚','庚','已'], ['亥','子','寅','卯'], {'生用'}, None),
    ('生例二经理',     ['癸','甲','癸','癸'], ['巳','子','卯','亥'], {'生用'}, None),
    ('生例四企业家',   ['壬','癸','壬','壬'], ['寅','卯','子','寅'], {'生用'}, None),
    ('合例一富命',     ['庚','丙','壬','丁'], ['子','戌','申','未'], {'合用'}, None),
    ('合例六两妻',     ['已','丁','庚','己'], ['酉','卯','戌','卯'], {'合用'}, None),
    ('合例八暗合',     ['丙','甲','乙','甲'], ['申','午','卯','申'], {'合用'}, None),
    ('墓例一经理',     ['已','癸','壬','庚'], ['未','酉','寅','子'], {'墓用'}, None),
    ('墓例三电厂官',   ['壬','已','丁','已'], ['寅','酉','丑','酉'], {'墓用'}, None),
    ('墓例四曾国藩',   ['乙','己','丙','己'], ['未','亥','辰','亥'], {'墓用'}, None),
    ('复例一数学家',   ['壬','辛','庚','丁'], ['午','亥','辰','亥'], {'制用','墓用'}, None),
    ('复例二副总',     ['甲','癸','丁','庚'], ['寅','酉','丑','子'], {'合用'}, 2),  # 书一层, level>2 即 ❌
    ('复例四老师经商', ['戊','丙','丁','癸'], ['申','辰','巳','卯'], {'合用','制用'}, None),
]

def judge_cat1(r, book_set, cap):
    pt = r['primary_work']['type']
    types = set(r['work_types'])
    if pt in book_set:
        if cap is not None and r['work_level'] > cap:
            return '⚠️'
        return '✅'
    if types & book_set:
        if cap is not None and r['work_level'] > cap:
            return '❌'
        return '⚠️'
    return '❌'

# ── 类目2: gongliang (15) ──
# (name, gans, zhis, book_level)
CAT2 = [
    ('李嘉诚', ['戊','己','庚','丁'], ['辰','未','午','亥'], 4),
    ('乾隆',   ['辛','丁','庚','丙'], ['卯','酉','午','子'], 4),
    ('克林顿', ['丙','丙','乙','戊'], ['戌','申','丑','寅'], 4),
    ('蒋介石', ['丁','庚','己','庚'], ['亥','戌','巳','午'], 3),
    ('岳飞',   ['癸','乙','甲','己'], ['未','卯','子','巳'], 3),
    ('例6',    ['乙','丙','甲','甲'], ['未','戌','子','戌'], 2),
    ('例7',    ['丙','戊','戊','甲'], ['申','戌','寅','寅'], 2),
    ('例8',    ['壬','戊','丙','壬'], ['寅','申','申','辰'], 3),
    ('例9',    ['壬','戊','癸','庚'], ['寅','申','巳','申'], 3),
    ('普例1',  ['丙','戊','辛','癸'], ['戌','戌','巳','巳'], 1),
    ('普例2',  ['壬','己','乙','丁'], ['子','酉','丑','丑'], 1),
    ('普例3',  ['庚','庚','癸','丁'], ['戌','辰','未','巳'], 1),
    ('普例4',  ['壬','甲','庚','辛'], ['子','辰','午','巳'], 2),
    ('普例5',  ['壬','甲','庚','己'], ['子','辰','寅','卯'], 2),
    ('阎锡山', ['癸','辛','乙','丁'], ['未','酉','酉','丑'], 3),
]
def judge_cat2(r, book_lv):
    d = r['level'] - book_lv
    if d == 0: return '✅'
    if abs(d) == 1: return '⚠️'
    return '❌'

# ── 类目3: xiangfa (18) ── (principle, name, gstr, zstr, book_verdict)
# xiangfa 稳定，用审计 修复后 verdict 作基准；改动由 key-signal 监控
CAT3 = [
    ('共象','丁目','丁辛乙丁','酉亥酉亥','⚠️'),
    ('共象','申机器','辛丙辛丙','卯申巳申','⚠️'),
    ('合象','建筑设计','壬癸丙戊','子丑寅戌','⚠️'),
    ('合象','银行行长','庚乙癸庚','辰酉卯申','⚠️'),
    ('化象','纺织','辛辛丙甲','卯丑辰午','✅'),
    ('化象','服装','癸丁癸癸','卯巳丑亥','✅'),
    ('墓象','军官','己辛戊甲','卯未辰寅','✅'),
    ('墓象','建筑','丁癸辛丁','未卯卯酉','✅'),
    ('制象','岳飞','癸乙甲己','未卯子巳','⚠️'),
    ('制象','资本运营','丁癸丙壬','未丑子辰','⚠️'),
    ('带象','甲子','癸甲戊癸','巳子午亥','✅'),
    ('带象','癸巳','辛辛丙癸','丑卯寅巳','✅'),
    ('借象','寅卯','庚己丁癸','寅丑卯卯','✅'),
    ('借象','戊巳','癸庚癸戊','巳申丑午','✅'),
    ('换象','银行行长','乙戊癸庚','巳子卯申','✅'),
    ('换象','外贸商','壬丙己辛','子午巳未','✅'),
    ('局象','公安','戊丙乙戊','申辰丑寅','⚠️'),
    ('局象','比劫包局','庚乙庚乙','戌酉申酉','✅'),
]
_P2K = {'共象':'gongxiang','合象':'hexiang','化象':'huaxiang','墓象':'muxiang',
        '制象':'zhixiang','带象':'daixiang','借象':'jiexiang','换象':'huanxiang','局象':'juxiang'}

# ── V4 verdict 解冻（cat3-5）──
# 原冻结口径：verdict 直接取审计时 book_v，引擎现状变化不影响判定（仅 detail 记录）。
# 解冻后按书结论重算，分两类：
#   cat4/cat5（书结论已编码为明确期望值 expect_primary/expect_gm/expect_val）：
#     ok=True  -> ✅（引擎当前命中书结论，如实计入；审计档留痕于 detail「审计档=」）
#     ok=False -> 维持审计档（⚠️/❌）；审计档=✅ 则 ❌ + 报警
#   cat3（书结论未完全编码，仅有象法原则键）：审计档为上限，
#     findings 非空 -> 审计档；空 -> ❌（原则检出丢失），审计档=✅ 另加报警。
# 报警（ALARM）=「ok=False 且 verdict=✅」组合：审计通过而当前引擎未命中书结论，
#   引擎回归或审计误判，须人工复核。
def recompute_verdict(book_v, ok):
    """cat4/cat5：返回 (verdict, alarm)。"""
    if ok:
        return '✅', False
    if book_v == '✅':
        return '❌', True
    return book_v, False

def recompute_verdict_xf(book_v, nonempty):
    """cat3：审计档为上限，检出丢失才降档。返回 (verdict, alarm)。"""
    if nonempty:
        return book_v, False
    if book_v == '✅':
        return '❌', True
    return '❌', False

def judge_cat3(princ, gstr, zstr, book_v):
    gans = list(gstr); zhis = list(zstr)
    r = run(gans, zhis)
    xo = r.get('xiangfa_ops', {})
    key = _P2K[princ]
    findings = xo.get(key, [])
    nonempty = bool(findings)
    return recompute_verdict_xf(book_v, nonempty) + (nonempty,)

# ── 类目4: caiming/guanming (10) ──
# 财命
CAI = [
    ('禄当财', ['丁','丙','庚','丁'], ['未','午','申','丑'], '禄当财', '⚠️'),
    ('伤食当财', ['己','戊','壬','癸'], ['酉','辰','申','卯'], '伤食当财', '⚠️'),
    ('官杀当财', ['辛','庚','丙','丁'], ['卯','子','申','酉'], '官统财（官杀当财）', '✅'),
    ('过河拆桥', ['辛','戊','己','癸'], ['卯','戌','亥','酉'], '过河拆桥', '✅'),
]
# 官命 (name, gans, zhis, expect_guanming_bool, book_v)
GUAN = [
    ('伤食制官杀', ['丙','甲','乙','甲'], ['申','午','卯','申'], True, '✅'),
    ('劫刃制官杀', ['甲','丁','甲','甲'], ['申','卯','申','子'], True, '✅'),
    ('财制印',     ['丁','己','癸','丁'], ['未','酉','巳','巳'], True, '✅'),
    ('印制伤食',   ['乙','丁','甲','丙'], ['未','亥','午','子'], False, '⚠️'),
    ('带帽',       ['壬','己','壬','甲'], ['寅','酉','申','辰'], True, '✅'),
    ('公门武职',   ['己','辛','戊','甲'], ['卯','未','辰','寅'], True, '✅'),
]

def judge_cat4():
    from mangpai.subjective.caiming import classify_caifu_view
    from mangpai.subjective.guanming import classify_guanming_combo, detect_guancai_daimao
    res = []
    for name, g, z, exp_primary, book_v in CAI:
        cv = classify_caifu_view(g[2], g, z)
        ok = (exp_primary in cv.get('primary', '')) or (exp_primary.split('（')[0] in cv.get('primary',''))
        res.append((f'cai:{name}', book_v, ok, cv.get('primary')))
    for name, g, z, exp_gm, book_v in GUAN:
        gm = classify_guanming_combo(g[2], g, z)
        ok = gm.get('is_guanming') == exp_gm
        res.append((f'guan:{name}', book_v, ok, gm.get('is_guanming')))
    return res

# ── 类目5: hunyin/xueli/laoyu (6) ──
CAT5 = [
    # (name, gans, zhis, gender, kind, expect_val, book_v)
    ('婚差', ['戊','己','乙','丁'], ['戌','未','巳','亥'], '男', 'hunyin', '差', '✅'),
    ('离婚', ['癸','辛','戊','丁'], ['丑','酉','午','巳'], '女', 'hunyin', '差', '✅'),
    ('初中', ['壬','丙','壬','丁'], ['子','午','辰','未'], '男', 'xueli', '低', '✅'),
    ('博士', ['甲','甲','辛','甲'], ['寅','戌','亥','午'], '男', 'xueli', '高', '✅'),
    ('抢劫', ['甲','丁','乙','庚'], ['寅','卯','丑','辰'], '男', 'laoyu', '高', '✅'),
    ('受贿', ['戊','丙','壬','戊'], ['戌','辰','申','申'], '男', 'laoyu', '高', '⚠️'),
]
def judge_cat5():
    res = []
    for name, g, z, gender, kind, exp, book_v in CAT5:
        r = run(g, z, gender=gender)
        if kind == 'hunyin':
            val = r.get('hunyin', {}).get('quality', {}).get('quality', '')
        elif kind == 'xueli':
            val = r.get('xueli', {}).get('level_str', '')
        else:
            val = r.get('laoyu', {}).get('risk', '')
        ok = (val == exp)
        res.append((f'{kind}:{name}', book_v, ok, val))
    return res

def compute():
    out = {}  # key -> (verdict, detail)
    alarms = []  # V4: ok=False 且 审计verdict=✅ 组合报警
    # cat1
    for name, g, z, bset, cap in CAT1:
        r = zuogong(fg(g), z)
        v = judge_cat1(r, bset, cap)
        out[f'zg:{name}'] = (v, f"types={r['work_types']} primary={r['primary_work']['type']} lv={r['work_level']}")
    # cat2
    for name, g, z, blv in CAT2:
        r = gongliang(fg(g), z)
        v = judge_cat2(r, blv)
        out[f'gl:{name}'] = (v, f"level={r['level']}(书{blv}) score={r['score']}")
    # cat3
    for princ, name, gs, zs, bv in CAT3:
        v, alarm, nonempty = judge_cat3(princ, gs, zs, bv)
        out[f'xf:{princ}:{name}'] = (v, f"ok={nonempty} 审计档={bv}")
        if alarm:
            alarms.append(f'xf:{princ}:{name}')
    # cat4
    for name, bv, ok, detail in judge_cat4():
        v, alarm = recompute_verdict(bv, ok)
        out[name] = (v, f"ok={ok} 审计档={bv} detail={detail}")
        if alarm:
            alarms.append(name)
    # cat5
    for name, bv, ok, detail in judge_cat5():
        v, alarm = recompute_verdict(bv, ok)
        out[name] = (v, f"ok={ok} 审计档={bv} val={detail}")
        if alarm:
            alarms.append(name)
    return out, alarms

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write_baseline = '--write-baseline' in sys.argv
    cur, alarms = compute()
    base_path = args[0] if args else DEFAULT_BASELINE
    # 统计
    from collections import Counter
    cnt = Counter(v for v, _ in cur.values())
    # 分类目统计
    def cat_stats(prefix):
        c = Counter()
        for k, (v, _) in cur.items():
            if k.startswith(prefix):
                c[v] += 1
        return c
    print("=== 当前判定 ===")
    for pref, label in [('zg:','cat1 zuogong'), ('gl:','cat2 gongliang'),
                        ('xf:','cat3 xiangfa'), ('cai:','cat4 cai'), ('guan:','cat4 guan'),
                        ('hunyin:','cat5'), ('xueli:','cat5'), ('laoyu:','cat5')]:
        c = cat_stats(pref)
        if c:
            print(f"  {label}: ✅{c.get('✅',0)} ⚠️{c.get('⚠️',0)} ❌{c.get('❌',0)}")
    tot = cnt
    print(f"  TOTAL: ✅{tot.get('✅',0)} ⚠️{tot.get('⚠️',0)} ❌{tot.get('❌',0)}  (n={sum(tot.values())})")
    # V4：「ok=False 且 审计verdict=✅」组合报警——审计通过而当前引擎未命中书结论
    if alarms:
        print(f"\n  🚨 ALARM ({len(alarms)}): 审计档✅ 但当前引擎未命中书结论（引擎回归或审计误判，须人工复核）:")
        for k in alarms:
            print(f"    {k}: {cur[k][1]}")
    n_reg = 0
    if base_path and os.path.exists(base_path):
        base = json.load(open(base_path))
        print(f"\n=== vs baseline ({os.path.basename(base_path)}) ===")
        reg, imp = [], []
        for k, (v, d) in cur.items():
            bv = base.get(k, {}).get('verdict')
            if bv and bv != v:
                order = {'✅':0,'⚠️':1,'❌':2}
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
    # 存档
    arch = {k: {'verdict': v, 'detail': d} for k, (v, d) in cur.items()}
    out_path = DEFAULT_BASELINE if write_baseline else CURRENT_OUT
    json.dump(arch, open(out_path, 'w'), ensure_ascii=False, indent=1)
    print(f"\n(archived -> {out_path})")
    sys.exit(1 if n_reg else 0)

if __name__ == '__main__':
    main()
