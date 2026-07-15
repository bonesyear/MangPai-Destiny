"""第一层基础层全量验证

验证项：
1. 纳音60组（NAYIN_TABLE 60甲子 + NAYIN_WUXING 五行归类）
2. 节气抽样（sxtwl 24节气 + jiaoyun 命五行->交运节气规则）
3. 藏干12（CANG_GAN_MANGPAI 12地支藏干表）
4. 长生10干（CHANGSHENG_START_MANGPAI 阴阳同生同死 + 5关键位）
5. 干支性情65条（ganqing 条件->行为规则 + match_ganqing/match_zhiqing）
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from foundation.objective.nayin import NAYIN_TABLE, NAYIN_WUXING, get_nayin, get_nayin_wuxing
from mangpai.objective.constants import (
    CANG_GAN_MANGPAI, CHANGSHENG_START_MANGPAI, KEY_STAGES, _STAGE_ALIASES,
    DI_ZHI, GAN_WX, ZHI_WX,
)
from mangpai.objective.jiaoyun import JIAOYUN_RULES, JIEQI_INDEX, _jieqi_jd, _jd_to_datetime
TIAN_GAN = list('甲乙丙丁戊己庚辛壬癸')
from mangpai.objective.changsheng import get_changsheng_mangpai, get_changsheng_all, is_key_stage
from foundation.objective.ganqing import (
    GAN_QING_RULES, ZHI_QING_RULES, match_ganqing, match_zhiqing, GanQingRule,
)

passed = 0
failed = 0
def check(name, cond, detail=''):
    global passed, failed
    if cond: passed += 1; print(f'  [PASS] {name}')
    else: failed += 1; print(f'  [FAIL] {name} - {detail}')

# ══════════════════════════════════════════════════════════════
print('── 1. 纳音60组 ──')
# 1a. 表长度=60 且键为完整60甲子
import itertools
GAN = list('甲乙丙丁戊己庚辛壬癸')
ZHI = list('子丑寅卯辰巳午未申酉戌亥')
jiazi60 = [g+z for g,z in zip(itertools.cycle(GAN), ZHI*6)]  # 阳阳/阴阴配对
# 标准排法：甲子乙丑丙寅...壬戌癸亥
std60 = []
gi, zi = 0, 0
for _ in range(60):
    std60.append(GAN[gi]+ZHI[zi]); gi=(gi+1)%10; zi=(zi+1)%12
check('NAYIN_TABLE 键数=60', len(NAYIN_TABLE)==60, f'实际{len(NAYIN_TABLE)}')
check('NAYIN_TABLE 键=标准60甲子', set(NAYIN_TABLE.keys())==set(std60), '键集不符')
# 1b. 抽样核对纳音名（每对同纳音）
expect_pairs = [('甲子','海中金'),('乙丑','海中金'),('丙寅','炉中火'),('丁卯','炉中火'),
                ('戊辰','大林木'),('壬戌','大海水'),('癸亥','大海水'),('甲午','砂中金'),
                ('丙午','天河水'),('戊午','天上火'),('庚子','壁上土'),('壬子','桑柘木'),
                ('戊申','大驿土'),('庚戌','钗钏金'),('丙辰','沙中土'),('甲寅','大溪水')]
for gz, ny in expect_pairs:
    check(f'纳音名 {gz}->{ny}', NAYIN_TABLE.get(gz)==ny, f'实际{NAYIN_TABLE.get(gz)}')
# 1c. 纳音五行归类：纳音名末字含五行线索，且30对各自两干支纳音相同
wx_of_name = {'金':['海中金','剑锋金','白蜡金','砂中金','金箔金','钗钏金'],
              '火':['炉中火','山头火','霹雳火','山下火','覆灯火','天上火'],
              '木':['大林木','杨柳木','松柏木','平地木','桑柘木','石榴木'],
              '水':['涧下水','泉中水','长流水','天河水','大溪水','大海水'],
              '土':['路旁土','城头土','壁上土','大驿土','沙中土','屋上土']}
name2wx = {n:w for w,names in wx_of_name.items() for n in names}
check('NAYIN_WUXING 覆盖30纳音名', set(NAYIN_WUXING.keys())==set(name2wx.keys()), '纳音名集合不符')
ok = all(NAYIN_WUXING.get(n)==w for n,w in name2wx.items())
check('NAYIN_WUXING 五行归类全对', ok, '归类有误')
# 1d. 30对各自两干支同纳音
pair_ok = True
for i in range(0,60,2):
    a,b = std60[i], std60[i+1]
    if NAYIN_TABLE[a]!=NAYIN_TABLE[b]: pair_ok=False; break
check('30对各自同纳音', pair_ok, f'{a}!={b}')
# 1e. get_nayin/get_nayin_wuxing 接口
check('get_nayin 接口', get_nayin('甲子')=='海中金', '接口异常')
check('get_nayin_wuxing 接口', get_nayin_wuxing('甲子')=='金', '接口异常')

# ══════════════════════════════════════════════════════════════
print('── 2. 节气抽样 ──')
import sxtwl
# sxtwl 24节气全名索引（与 jiaoyun.JIEQI_INDEX 注释一致）
_JQ24 = ['冬至','小寒','大寒','立春','雨水','惊蛰','春分','清明','谷雨',
         '立夏','小满','芒种','夏至','小暑','大暑','立秋','处暑',
         '白露','秋分','寒露','霜降','立冬','小雪','大雪']
_NAME2IDX = {n:i for i,n in enumerate(_JQ24)}
def _jq_jd(year, name):
    idx = _NAME2IDX[name]
    cands = [j for j in sxtwl.getJieQiByYear(year) if j.jqIndex==idx]
    return min(cands, key=lambda j:j.jd).jd if cands else None
# 2a. JIEQI_INDEX 含5交运节气且索引正确（与24节气全表一致）
jq5_ok = all(JIEQI_INDEX.get(n)==_NAME2IDX[n] for n in ['冬至','大寒','清明','芒种','处暑'])
check('JIEQI_INDEX 5交运节气索引正确', jq5_ok and len(JIEQI_INDEX)==5, f'实际{JIEQI_INDEX}')
# 2b. sxtwl 每年返回24节气(jqIndex 0-23齐全)
sample_years = [1949, 1976, 2000, 2024, 1887]
jq24_ok = all(len(set(j.jqIndex for j in sxtwl.getJieQiByYear(y)))==24 for y in sample_years)
check('sxtwl 每年24节气齐全(0-23)', jq24_ok, '24节气不全')
# 2c. 抽样5年×7节气 儒略日+datetime（覆盖交运5节气+立春夏至）
sample_jq = ['立春','冬至','夏至','清明','大寒','芒种','处暑']
jq_ok = True
for y in sample_years:
    for jq in sample_jq:
        jd = _jq_jd(y, jq)
        if jd is None: jq_ok=False; print(f'    缺 {y}年{jq}'); continue
        dt = _jd_to_datetime(jd)
        if dt is None: jq_ok=False; print(f'    转换失败 {y}年{jq}')
        elif dt.year not in (y, y-1, y+1): jq_ok=False; print(f'    年份越界 {y}年{jq}->{dt.year}')
check('抽样5年×7节气 儒略日+datetime', jq_ok, '见上方明细')
# 2d. 立春在2月（北半球），冬至在12月
lichun_ok = all(_jd_to_datetime(_jq_jd(y,'立春')).month==2 for y in sample_years)
check('立春恒在2月', lichun_ok, '立春月份异常')
dongzhi_ok = all(_jd_to_datetime(_jq_jd(y,'冬至')).month==12 for y in sample_years)
check('冬至恒在12月', dongzhi_ok, '冬至月份异常')
# 2e. 命五行->交运节气规则完整（5行）
check('JIAOYUN_RULES 覆盖5五行', set(JIAOYUN_RULES.keys())=={'木','火','土','金','水'}, '命五行规则不全')
for wx,(jq,off,zhi) in JIAOYUN_RULES.items():
    check(f'交运节气 {wx}->{jq}{off:+d}天{zhi}时', jq in _NAME2IDX, f'{jq}不在24节气')

# ══════════════════════════════════════════════════════════════
print('── 3. 藏干12 ──')
# 3a. 12地支全有藏干
check('12地支藏干全', set(CANG_GAN_MANGPAI.keys())==set(DI_ZHI), '地支不全')
# 3b. 抽样核对经典藏干
expect_cang = {
    '子':[('癸','本气')], '丑':[('己','本气'),('辛','中气'),('癸','余气')],
    '寅':[('甲','本气'),('丙','中气'),('戊','余气')], '卯':[('乙','本气')],
    '辰':[('戊','本气'),('癸','中气'),('乙','余气')], '巳':[('丙','本气'),('戊','中气'),('庚','余气')],
    '午':[('丁','本气'),('己','中气')], '未':[('己','本气'),('乙','中气'),('丁','余气')],
    '申':[('庚','本气'),('壬','中气'),('戊','余气')], '酉':[('辛','本气')],
    '戌':[('戊','本气'),('丁','中气'),('辛','余气')], '亥':[('壬','本气'),('甲','中气')],
}
for z, exp in expect_cang.items():
    got = CANG_GAN_MANGPAI.get(z,[])
    check(f'藏干 {z}', got==exp, f'实际{got}')
# 3c. 本气五行=地支五行（阳干对阳支/阴干对阴支的旺气）
from mangpai.objective.constants import ZHI_WX
benqi_ok = True
for z, cang in CANG_GAN_MANGPAI.items():
    if not cang: benqi_ok=False; break
    bg = cang[0][0]
    if GAN_WX[bg] != ZHI_WX[z]:
        # 午本气丁(火)=午火 OK; 例外仅个别，本气五行应与支五行同
        benqi_ok=False; print(f'    {z}本气{bg}五行{GAN_WX[bg]}!=支{ZHI_WX[z]}'); break
check('本气五行=地支五行', benqi_ok, '本气五行不一致')

# ══════════════════════════════════════════════════════════════
print('── 4. 长生10干 ──')
# 4a. 10干全有长生起点
check('CHANGSHENG_START 覆盖10干', set(CHANGSHENG_START_MANGPAI.keys())==set(TIAN_GAN), '干不全')
# 4b. 阴阳同生同死：阴干与同五行阳干同起点（乙=甲=亥,丁=丙=寅,己=戊=寅,辛=庚=巳,癸=壬=申）
same_birth = (CHANGSHENG_START_MANGPAI['甲']==CHANGSHENG_START_MANGPAI['乙']=='亥' and
              CHANGSHENG_START_MANGPAI['丙']==CHANGSHENG_START_MANGPAI['丁']==CHANGSHENG_START_MANGPAI['戊']==CHANGSHENG_START_MANGPAI['己']=='寅' and
              CHANGSHENG_START_MANGPAI['庚']==CHANGSHENG_START_MANGPAI['辛']=='巳' and
              CHANGSHENG_START_MANGPAI['壬']==CHANGSHENG_START_MANGPAI['癸']=='申')
check('阴阳同生同死(阴干同阳干起点)', same_birth, f'实际{CHANGSHENG_START_MANGPAI}')
# 4c. 每干起点位恰为'长生'
cs_ok = all(get_changsheng_mangpai(g, CHANGSHENG_START_MANGPAI[g])=='长生' for g in TIAN_GAN)
check('起点位=长生', cs_ok, '起点非长生')
# 4d. 5关键位 KEY_STAGES 齐全
check('KEY_STAGES 含5位', KEY_STAGES=={'长生','禄旺','死','墓','绝'}, f'实际{KEY_STAGES}')
check('临官/帝旺->禄旺别名', _STAGE_ALIASES.get('临官')=='禄旺' and _STAGE_ALIASES.get('帝旺')=='禄旺', '别名缺失')
# 4e. 抽样核对关键位：甲长生亥、临官寅(禄)、帝旺卯、墓未、绝申
ks_甲 = {'亥':'长生','寅':'临官','卯':'帝旺','未':'墓','申':'绝'}
ks_ok = all(get_changsheng_mangpai('甲',z)==s for z,s in ks_甲.items())
check('甲 5关键位(亥长/寅临/卯旺/未墓/申绝)', ks_ok, '甲关键位有误')
# 4f. is_key_stage 识别5位（含临官/帝旺经别名）
iks_ok = is_key_stage('长生') and is_key_stage('临官') and is_key_stage('帝旺') and is_key_stage('墓') and is_key_stage('绝') and not is_key_stage('沐浴')
check('is_key_stage 识别5位', iks_ok, '关键位识别异常')
# 4g. 10干各12地支完整返回
all_ok = all(len(get_changsheng_all(g))==12 for g in TIAN_GAN)
check('10干×12支全覆盖', all_ok, '覆盖不全')

# ══════════════════════════════════════════════════════════════
print('── 5. 干支性情65条 ──')
gan_total = sum(len(v) for v in GAN_QING_RULES.values())
zhi_total = sum(len(v) for v in ZHI_QING_RULES.values())
check('10干规则全覆盖', set(GAN_QING_RULES.keys())==set(TIAN_GAN), '干不全')
check(f'天干性情规则数(规格65)', gan_total>=65, f'实际{gan_total}')
# 5a. 每条规则结构完整（gan/fu_clause/condition/behavior/behavior_type 非空）
struct_ok = True
for g, rules in GAN_QING_RULES.items():
    for r in rules:
        if not (r.gan and r.fu_clause and r.behavior and r.behavior_type):
            struct_ok=False; print(f'    {g} 规则结构不全: {r.fu_clause}'); break
        if r.condition is None:
            struct_ok=False; print(f'    {g} condition缺失: {r.fu_clause}'); break
    if not struct_ok: break
check('天干规则结构完整', struct_ok, '见上方明细')
# 5b. behavior_type 全在合法集合
from foundation.objective.ganqing import BEHAVIOR_TYPES
bt_ok = all(r.behavior_type in BEHAVIOR_TYPES for rules in GAN_QING_RULES.values() for r in rules)
check('behavior_type 合法', bt_ok, '存在非法behavior_type')
# 5c. match_ganqing 可调用且返回 List[GanQingRule]
m = match_ganqing('甲', month_zhi='寅', stems=['甲','丙','戊'], day_gz='甲子')
check('match_ganqing 可调用', isinstance(m, list) and all(isinstance(x, GanQingRule) for x in m), '返回类型异常')
# 5d. match_zhiqing 可调用
mz = match_zhiqing('寅')
check('match_zhiqing 可调用', isinstance(mz, list) and all(isinstance(x, GanQingRule) for x in mz), '返回类型异常')
# 5e. 地支5条规则
check('地支性情规则数(规格5)', zhi_total>=5, f'实际{zhi_total}')
# 5f. 抽样：甲春不容金——春月甲木规则中应含排斥金类行为
jia_chun = [r for r in match_ganqing('甲', month_zhi='寅') if '金' in (r.behavior or '') or r.behavior_type in ('排斥','克')]
check('甲春月匹配到涉金规则', len(jia_chun)>0, '甲春不容金规则未命中')

print('='*60)
print(f'验证结果: {passed} passed, {failed} failed, total {passed+failed}')
print('='*60)
sys.exit(0 if failed==0 else 1)
