"""第三层 calib_zhenbao 10例端到端 · 三关键检查点验证

检查点：
  A. 方向判断（assess_direction_signals）：10例全部产出方向/凶向信号
  B. 官命否决（guanming veto）：应否决例(乞丐/贪财坐牢)被否决；正当官命例(阎锡山/厅级)不被否决
  C. 阎锡山L3：第12期层功level=3 + 官命level=3
     （F6 修正：旧锁 L4 与书锚正面冲突——理象学 7182-7188 纯制局读法
     「旺杀入墓…杀库制比劫库…功量有三层强一点」、授课38期「旺忌神弱制」
     非从杀；旧 L4 系 gongliang 化用高层+1 校准自我撤销所致（批3 P0-2），
     以书为准改锁 L3）
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mangpai import MangpaiEngine
from mangpai.subjective.guanming import analyze_guanming
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.yongshen import assess_direction_signals
from mangpai.objective.bazi_calc import compute_shishen, get_kong_wang

# 10例（与 calib_zhenbao.CASES 一致）
CASES = [
    ("第1期·生孩子/官司/职业", ['戊','己','乙','丁'], ['戌','未','巳','亥'], '男', 1958),
    ("第4期·赔媳妇赔娶媳妇钱", ['丁','丙','庚','丁'], ['未','午','申','丑'], '男', 1967),
    ("第5期·厅级官壬午升丁亥到顶", ['乙','庚','辛','壬'], ['巳','辰','卯','辰'], '男', 1965),
    ("第9期·乞丐(丙午运讨乞)", ['壬','癸','壬','丙'], ['子','卯','子','午'], '男', 1972),
    ("第10期·李凡丁公检法/两次婚/庚辰", ['壬','壬','庚','辛'], ['子','寅','辰','巳'], '男', 1972),
    ("第12期·阎锡山半壁天下/勿冒头", ['癸','辛','乙','丁'], ['未','酉','酉','丑'], '男', 1883),
    ("第14期·刘XX名演员卖身/三婚/无子", ['乙','丙','甲','乙'], ['未','戌','子','亥'], '女', 1955),
    ("第14期·贪财坐牢", ['戊','戊','戊','甲'], ['戌','午','午','寅'], '男', 1958),
    ("第23期·官司输破财/明年转机后年赢", ['庚','戊','壬','庚'], ['戌','子','午','子'], '男', 1970),
    ("第23期·找二婚妻(大姑娘找不成)", ['壬','癸','壬','甲'], ['子','卯','子','辰'], '男', 1972),
]

passed = 0; failed = 0
def check(name, cond, detail=''):
    global passed, failed
    if cond: passed += 1; print(f'  [PASS] {name}')
    else: failed += 1; print(f'  [FAIL] {name} - {detail}')

def _bazi_data(gans, zhis, gender, year):
    bazi = {'year':gans[0]+zhis[0],'month':gans[1]+zhis[1],'day':gans[2]+zhis[2],'hour':gans[3]+zhis[3]}
    shishen = compute_shishen(gans[2], bazi['year'],bazi['month'],bazi['day'],bazi['hour'])
    kong_wang = get_kong_wang(gans[2], zhis[2])
    return {'bazi':bazi,'shishen':shishen,'kong_wang':kong_wang,'di_zhi_relations':{},
            'input':{'gender':gender,'year':year}}

print('='*60)
print('── A. 方向判断（10例 assess_direction_signals）──')
dir_results = {}
for name, gans, zhis, gender, year in CASES:
    try:
        res = MangpaiEngine(_bazi_data(gans,zhis,gender,year)).compute_all()
        gl = res.get('gongliang', {})
        d = assess_direction_signals(gans[2], gans, zhis, gongliang_result=gl)
        dir_results[name] = d
        has_dir = isinstance(d, dict) and 'direction' in d and 'reasons' in d
        check(f'{name} 方向产出', has_dir, f'返回{d}')
    except Exception as e:
        import traceback; traceback.print_exc()
        check(f'{name} 方向产出', False, f'异常{e}')
        dir_results[name] = {}

print('── B. 官命否决（guanming veto）──')
gm_results = {}
for name, gans, zhis, gender, year in CASES:
    try:
        res = MangpaiEngine(_bazi_data(gans,zhis,gender,year)).compute_all()
        gl = res.get('gongliang', {})
        gm = analyze_guanming(gans[2], gans, zhis, gongliang_result=gl)
        gm_results[name] = gm
    except Exception as e:
        import traceback; traceback.print_exc()
        gm_results[name] = {}

# B1. 应否决例：乞丐(比劫夺财破财)、贪财坐牢(反局/牢狱) -> is_guanming=False
#     注：贪财坐牢从强格官杀为忌神，反局否决当生效
yixing = gm_results.get('第9期·乞丐(丙午运讨乞)', {})
tancai = gm_results.get('第14期·贪财坐牢', {})
check('乞丐 官命被否决(is=False)', yixing.get('is_guanming')==False, f"is={yixing.get('is_guanming')}")
check('贪财坐牢 官命被否决(is=False)', tancai.get('is_guanming')==False, f"is={tancai.get('is_guanming')}")
# 否决依据应含凶向信号
yixing_desc = str(yixing.get('summary','')) + str(yixing.get('level',{}).get('desc',''))
check('乞丐 否决依据含破财/比劫', ('破财' in yixing_desc or '比劫' in yixing_desc or '劫刃' in yixing_desc), f'{yixing_desc}')
tancai_desc = str(tancai.get('summary','')) + str(tancai.get('level',{}).get('desc',''))
check('贪财坐牢 否决依据含反局/牢狱/否决', ('反局' in tancai_desc or '牢狱' in tancai_desc or '否决' in tancai_desc or '坐牢' in tancai_desc), f'{tancai_desc}')

# B2. 正当官命例：阎锡山、厅级 -> is_guanming=True（反局否决门槛保护）
yan = gm_results.get('第12期·阎锡山半壁天下/勿冒头', {})
tingji = gm_results.get('第5期·厅级官壬午升丁亥到顶', {})
check('阎锡山 官命成立(is=True,门槛保护)', yan.get('is_guanming')==True, f"is={yan.get('is_guanming')}")
check('厅级 官命成立(is=True)', tingji.get('is_guanming')==True, f"is={tingji.get('is_guanming')}")
# 阎锡山官阶未被否决降级（F6：层功 L3 合书「三层强一点」理象学7188；
# guanming grade_map L3->中高(处级) 与 gongliang _RANK_GRADE L3->厅级-省部级
# 的口径差为 F12 联动项，本批不动 grade_map，仅锁「未被否决」）
yan_grade = str(yan.get('level',{}).get('grade',''))
check('阎锡山 官阶未被否决(grade非否决/非官命)', '否决' not in yan_grade and '非官命' not in yan_grade, f'grade={yan_grade}')

print('── C. 阎锡山L3（书「三层强一点」理象学7188）──')
# 层功 level=3 + 官命 level=3
yan_gl = None
for name, gans, zhis, gender, year in CASES:
    if '阎锡山' in name:
        gl = analyze_gongliang(day_gan=gans[2], gans=gans, zhis=zhis)
        yan_gl = gl; break
check('阎锡山 层功level=3(三层强一点，大富大贵)', yan_gl and yan_gl.get('level')==3, f"level={yan_gl.get('level') if yan_gl else None}")
check('阎锡山 层功tier=大富大贵', yan_gl and '大富' in str(yan_gl.get('tier_name','')), f"tier={yan_gl.get('tier_name') if yan_gl else None}")
yan_gm_lv = yan.get('level',{}).get('level') if isinstance(yan.get('level'),dict) else None
check('阎锡山 官命level=3', yan_gm_lv==3, f'官命level={yan_gm_lv}')

print('='*60)
print(f'验证结果: {passed} passed, {failed} failed, total {passed+failed}')
print('='*60)
sys.exit(0 if failed==0 else 1)
