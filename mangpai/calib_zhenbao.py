"""
命理珍宝50期 — 郝金阳断语案例引擎校准（只读诊断，不修改引擎）
"""
import sys, json
sys.path.insert(0, '/root/metaphysics')
from mangpai import MangpaiEngine
from mangpai.subjective.caiming import analyze_caiming
from mangpai.subjective.guanming import analyze_guanming
from mangpai.subjective.hunyin import analyze_hunyin
from mangpai.subjective.zhiye import analyze_zhiye
from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi
from mangpai.subjective.gongliang import analyze_gongliang

def run_case(name, gans, zhis, gender, year, dayun=None, liunian=None):
    """dayun: (gan,zhi) of the relevant大运柱; liunian: (gan,zhi,year) of流年柱."""
    bazi = {
        'year': gans[0]+zhis[0], 'month': gans[1]+zhis[1],
        'day': gans[2]+zhis[2], 'hour': gans[3]+zhis[3],
    }
    bazi_data = {
        'bazi': bazi, 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': gender, 'year': year},
    }
    # 喂入大运/流年给 engine 的 dayun_analysis/liunian_analysis
    if dayun:
        bazi_data['dayun'] = {'direction':'顺','start_age':5,
            'dayun':[{'gz':dayun[0]+dayun[1],'start_age':5}]}
    if liunian:
        bazi_data['liunian'] = [{'gz':liunian[0]+liunian[1],'year':liunian[2]}]

    res = MangpaiEngine(bazi_data).compute_all()
    dg = gans[2]
    cm = analyze_caiming(dg, gans, zhis)
    gm = analyze_guanming(dg, gans, zhis)
    hy = analyze_hunyin(dg, gans, zhis, gender=gender)
    zy = analyze_zhiye(dg, gans, zhis)
    yq = None
    if dayun or liunian:
        yq = infer_comprehensive_yingqi(dg, gans, zhis,
            dayun_gan=(dayun[0] if dayun else ''),
            dayun_zhi=(dayun[1] if dayun else ''),
            liunian_gan=(liunian[0] if liunian else ''),
            liunian_zhi=(liunian[1] if liunian else ''))
    return res, cm, gm, hy, zy, yq

def show(name, res, cm, gm, hy, zy, yq):
    print(f"\n{'='*70}\n【{name}】  {res['bazi']['year']} {res['bazi']['month']} {res['bazi']['day']} {res['bazi']['hour']}")
    print("摘要:", res['summary'])
    zg = res['zuogong']; gl = res['gongliang']
    print(f"[做功] types={zg.get('work_types')} level={zg.get('work_level')}/{zg.get('work_tier')} eff={zg.get('work_efficiency')}")
    print(f"[层功] L{gl.get('level')} {gl.get('tier_name')} score={gl.get('score')} 富贵={gl.get('fugui_pinjian')} 净={gl.get('zhi_jing')}")
    zf = res.get('zhengfan',{})
    print(f"[正反] {zf.get('configuration')} ({zf.get('type')})")
    mk = res.get('muku',{})
    print(f"[墓库] {mk}")
    ss = res.get('shensha',{})
    ss_names = [k for k,v in ss.items() if isinstance(v,dict) and v.get('in_pillars')]
    print(f"[神煞] {ss_names}")
    print(f"[财命] tier={cm.get('tier')} | {cm.get('summary')}")
    print(f"[官命] is={gm.get('is_guanming')} level={gm.get('level')} | {gm.get('summary')}")
    q = hy.get('quality')
    qtxt = q.get('quality') if isinstance(q,dict) else q
    print(f"[婚姻] quality={qtxt} duohun={hy.get('duohun')} | {hy.get('summary')}")
    print(f"[职业] primary={zy.get('primary')} label={zy.get('primary_label')}")
    if yq:
        print(f"[应期] {yq.get('conclusion')} | trigger={yq.get('liunian_trigger')}")
    da = res.get('dayun_analysis',{})
    if da.get('summary'): print(f"[大运分析] {da.get('summary')}")
    la = res.get('liunian_analysis',{})
    if la.get('summary'): print(f"[流年分析] {la.get('summary')}")

# ============ 10个郝金阳断语案例 ============
CASES = [
    # 1. 第1期·生孩子  戊戌(1958)男  大运壬戌 流年戊辰(1988)
    ("第1期·生孩子/官司/职业", ['戊','己','乙','丁'], ['戌','未','巳','亥'], '男', 1958,
        ('壬','戌'), ('戊','辰',1988)),
    # 2. 第4期·赔媳妇  丁未(1967)男  癸卯运 戊寅(1998)
    ("第4期·赔媳妇赔娶媳妇钱", ['丁','丙','庚','丁'], ['未','午','申','丑'], '男', 1967,
        ('癸','卯'), ('戊','寅',1998)),
    # 3. 第5期·厅级  乙巳(1965)男  丙子运 壬午年升/丁亥年到顶
    ("第5期·厅级官壬午升丁亥到顶", ['乙','庚','辛','壬'], ['巳','辰','卯','辰'], '男', 1965,
        ('丙','子'), ('壬','午',2002)),
    # 4. 第9期·乞丐  壬子(1972)男  丙午运
    ("第9期·乞丐(丙午运讨乞)", ['壬','癸','壬','丙'], ['子','卯','子','午'], '男', 1972,
        ('丙','午'), None),
    # 5. 第10期·李凡丁  壬子(1972)男  戊寅(98)调动 庚辰(2000)媳妇上身
    ("第10期·李凡丁公检法/两次婚/庚辰", ['壬','壬','庚','辛'], ['子','寅','辰','巳'], '男', 1972,
        ('戊','寅'), ('庚','辰',2000)),
    # 6. 第12期·阎锡山  癸未(1883)男
    ("第12期·阎锡山半壁天下/勿冒头", ['癸','辛','乙','丁'], ['未','酉','酉','丑'], '男', 1883,
        None, None),
    # 7. 第14期·刘XX演员  乙未(1955)坤
    ("第14期·刘XX名演员卖身/三婚/无子", ['乙','丙','甲','乙'], ['未','戌','子','亥'], '女', 1955,
        None, None),
    # 8. 第14期·贪财坐牢  戊戌(1958)男
    ("第14期·贪财坐牢", ['戊','戊','戊','甲'], ['戌','午','午','寅'], '男', 1958,
        None, None),
    # 9. 第23期·官司破财  庚戌(1970)男  辛卯运 己卯(1999)官司破财
    ("第23期·官司输破财/明年转机后年赢", ['庚','戊','壬','庚'], ['戌','子','午','子'], '男', 1970,
        ('辛','卯'), ('己','卯',1999)),
    # 10. 第23期·找二婚  壬子(1972)男
    ("第23期·找二婚妻(大姑娘找不成)", ['壬','癸','壬','甲'], ['子','卯','子','辰'], '男', 1972,
        None, None),
]

for c in CASES:
    name = c[0]
    try:
        res,cm,gm,hy,zy,yq = run_case(name, c[1], c[2], c[3], c[4], c[5], c[6])
        show(name, res, cm, gm, hy, zy, yq)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"!! {name} 失败: {e}")
