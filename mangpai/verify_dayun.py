"""
盲派大运/流年分析模块验证脚本

验证项：
1. 大运天干十神定位
2. 大运地支冲合穿刑破关系
3. 大运墓库开闭效应
4. 大运废神激活
5. 大运禄刃应期
6. 大运长生位
7. 大运气势变化
8. 大运综合吉凶评价
9. 流年与大运互动
10. 空亡折扣
11. MangpaiEngine 集成
12. 主观层 payload 集成
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.dayun import _analyze_pillar_interaction
from mangpai.subjective.dayun import analyze_dayun_mangpai
from mangpai.subjective.liunian import analyze_liunian_mangpai
from mangpai.objective.constants import LU, GAN_WX, ZHI_WX
from mangpai import MangpaiEngine

passed = 0
failed = 0


def check(name, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f'  [PASS] {name}')
    else:
        failed += 1
        print(f'  [FAIL] {name} — {detail}')


# ── 测试数据 ──
# 本命：甲寅(年) 丙子(月) 庚午(日) 壬辰(时)
# 日干庚金，做功在日支午（午克庚？不对，庚金克午火... 实际是庚坐午，午中丁火官星）
# 为简化测试，用标准四柱
NATAL_GANS = ['甲', '丙', '庚', '壬']  # 年月日时
NATAL_ZHIS = ['寅', '子', '午', '辰']  # 年月日时
DAY_GAN = '庚'

print('=' * 60)
print('盲派大运/流年分析模块验证')
print('=' * 60)

# ── 1. 大运天干十神定位 ──
print('\n── 1. 大运天干十神定位 ──')

# 庚日干见丁=正官，见甲=偏财，见乙=正财
dy_list_1 = [{'gz': '丁亥', 'start_age': 5}]
result_1 = analyze_dayun_mangpai(dy_list_1, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
check('大运分析返回结果', result_1 is not None and 'dayun' in result_1)
check('大运列表长度正确', len(result_1['dayun']) == 1)
dy_1 = result_1['dayun'][0]
check('大运天干=丁', dy_1['gan'] == '丁')
check('大运地支=亥', dy_1['zhi'] == '亥')
check('大运gz=丁亥', dy_1['gz'] == '丁亥')
# 庚(阳金)见丁(阴火)→火克金→正官
check('丁对庚=正官', dy_1['gan_shishen'] == '正官',
      f"got {dy_1['gan_shishen']}")
check('正官属用', dy_1['tiyong_import']['category'] == '用')
check('正官运描述', '正官' in dy_1['tiyong_import']['desc'])

# 庚见甲=偏财
dy_list_1b = [{'gz': '甲申', 'start_age': 5}]
result_1b = analyze_dayun_mangpai(dy_list_1b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_1b = result_1b['dayun'][0]
# 庚(阳金)见甲(阳木)→金克木→偏财
check('甲对庚=偏财', dy_1b['gan_shishen'] == '偏财',
      f"got {dy_1b['gan_shishen']}")

# 庚见壬=食神
dy_list_1c = [{'gz': '壬午', 'start_age': 5}]
result_1c = analyze_dayun_mangpai(dy_list_1c, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_1c = result_1c['dayun'][0]
# 庚(阳金)见壬(阳水)→金生水→食神
check('壬对庚=食神', dy_1c['gan_shishen'] == '食神',
      f"got {dy_1c['gan_shishen']}")
check('食神属体', dy_1c['tiyong_import']['category'] == '体')

# ── 2. 大运地支关系 ──
print('\n── 2. 大运地支关系 ──')

# 大运子→冲午(日支)
dy_list_2 = [{'gz': '丁子', 'start_age': 5}]
result_2 = analyze_dayun_mangpai(dy_list_2, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_2 = result_2['dayun'][0]
chong = [r for r in dy_2['zhi_relations'] if r['type'] == '冲']
check('子冲午检测到', len(chong) >= 1, f"zhi_relations={dy_2['zhi_relations']}")
if chong:
    check('冲目标=午(日柱)', chong[0]['target'] == '午' and '日柱' in chong[0]['target_pillar'],
          f"target={chong[0]['target']}, pillar={chong[0]['target_pillar']}")

# 大运未→合午(日支)
dy_list_2b = [{'gz': '丁未', 'start_age': 5}]
result_2b = analyze_dayun_mangpai(dy_list_2b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_2b = result_2b['dayun'][0]
he = [r for r in dy_2b['zhi_relations'] if r['type'] == '六合']
check('未合午检测到', len(he) >= 1, f"zhi_relations={dy_2b['zhi_relations']}")
if he:
    check('合目标=午(日柱)', he[0]['target'] == '午')

# 大运丑→穿午(日支)
dy_list_2c = [{'gz': '丁丑', 'start_age': 5}]
result_2c = analyze_dayun_mangpai(dy_list_2c, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_2c = result_2c['dayun'][0]
chuan = [r for r in dy_2c['zhi_relations'] if r['type'] == '穿']
check('丑穿午检测到', len(chuan) >= 1, f"zhi_relations={dy_2c['zhi_relations']}")

# ── 3. 大运墓库开闭 ──
print('\n── 3. 大运墓库开闭 ──')

# 本命时支辰=水库/土库。大运戌→冲辰→开库（如果有透干）
# 本命天干有壬(水)，辰为水库→壬透干→开库成功
dy_list_3 = [{'gz': '戊戌', 'start_age': 5}]
result_3 = analyze_dayun_mangpai(dy_list_3, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_3 = result_3['dayun'][0]
tomb = dy_3.get('tomb_effect')
check('墓库效应检测到', tomb is not None, f"tomb_effect={tomb}")
if tomb:
    check('冲开辰墓库', len(tomb.get('opens', [])) >= 1,
          f"opens={tomb.get('opens')}")
    if tomb.get('opens'):
        check('开库透干=水', '水' in tomb['opens'][0].get('tou_gan', []),
              f"tou_gan={tomb['opens'][0].get('tou_gan')}")

# 大运酉→合辰→闭库
dy_list_3b = [{'gz': '丁酉', 'start_age': 5}]
result_3b = analyze_dayun_mangpai(dy_list_3b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_3b = result_3b['dayun'][0]
tomb_b = dy_3b.get('tomb_effect')
check('合闭辰墓库', tomb_b is not None and len(tomb_b.get('closes', [])) >= 1,
      f"tomb_effect={tomb_b}")

# ── 4. 大运废神激活 ──
print('\n── 4. 大运废神激活 ──')

# 假设年柱天干甲为废神（未参与做功）
# 大运己→合甲→激活废神
fei_shen = ['year_gan']
dy_list_4 = [{'gz': '己巳', 'start_age': 5}]
result_4 = analyze_dayun_mangpai(dy_list_4, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
                                  natal_fei_shen=fei_shen)
dy_4 = result_4['dayun'][0]
activated = dy_4.get('fei_shen_activated', [])
check('废神激活检测到', len(activated) >= 1, f"fei_shen_activated={activated}")
if activated:
    check('激活年柱甲', activated[0]['pillar'] == '年柱' and activated[0]['target'] == '甲',
          f"pillar={activated[0]['pillar']}, target={activated[0]['target']}")
    check('激活原因含天干合', any('合' in r for r in activated[0]['reasons']),
          f"reasons={activated[0]['reasons']}")

# 无废神时返回空列表
result_4b = analyze_dayun_mangpai(dy_list_4, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
                                   natal_fei_shen=[])
check('无废神时激活列表为空', len(result_4b['dayun'][0].get('fei_shen_activated', [])) == 0)

# ── 5. 大运禄刃应期 ──
print('\n── 5. 大运禄刃应期 ──')

# 庚禄在申→大运申=禄运
dy_list_5 = [{'gz': '甲申', 'start_age': 5}]
result_5 = analyze_dayun_mangpai(dy_list_5, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_5 = result_5['dayun'][0]
lu_blade = dy_5.get('lu_blade')
check('禄位检测到', lu_blade is not None and lu_blade['type'] == '禄',
      f"lu_blade={lu_blade}")
if lu_blade:
    check('庚禄在申', '申' in lu_blade['desc'] and '禄' in lu_blade['desc'])

# 庚刃在酉→大运酉=刃运
dy_list_5b = [{'gz': '丁酉', 'start_age': 5}]
result_5b = analyze_dayun_mangpai(dy_list_5b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_5b = result_5b['dayun'][0]
lu_blade_b = dy_5b.get('lu_blade')
check('刃位检测到', lu_blade_b is not None and lu_blade_b['type'] == '羊刃',
      f"lu_blade={lu_blade_b}")

# 非禄非刃
dy_list_5c = [{'gz': '丁亥', 'start_age': 5}]
result_5c = analyze_dayun_mangpai(dy_list_5c, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_5c = result_5c['dayun'][0]
check('非禄非刃返回None', dy_5c.get('lu_blade') is None)

# ── 6. 大运长生位 ──
print('\n── 6. 大运长生位 ──')

# 庚长生在巳→大运巳=长生位
dy_list_6 = [{'gz': '己巳', 'start_age': 5}]
result_6 = analyze_dayun_mangpai(dy_list_6, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_6 = result_6['dayun'][0]
cs = dy_6.get('changsheng', {})
check('庚在巳=长生', cs.get('stage') == '长生',
      f"changsheng={cs}")

# 庚在午=沐浴（非关键位）
dy_list_6b = [{'gz': '丁午', 'start_age': 5}]
result_6b = analyze_dayun_mangpai(dy_list_6b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_6b = result_6b['dayun'][0]
cs_b = dy_6b.get('changsheng', {})
check('庚在午=沐浴', cs_b.get('stage') == '沐浴',
      f"changsheng={cs_b}")

# 庚在子=死（盲派阴阳同生同死，庚长生巳→顺数到子）
# 巳→午(沐浴)→未(冠带)→申(临官)→酉(帝旺)→戌(衰)→亥(病)→子(死)
dy_list_6c = [{'gz': '丁子', 'start_age': 5}]
result_6c = analyze_dayun_mangpai(dy_list_6c, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_6c = result_6c['dayun'][0]
cs_c = dy_6c.get('changsheng', {})
check('庚在子=死', cs_c.get('stage') == '死',
      f"changsheng={cs_c}")

# ── 7. 大运气势变化 ──
print('\n── 7. 大运气势变化 ──')

# 本命五行分布：甲(木)+丙(火)+庚(金)+壬(水) + 寅(木)+子(水)+午(火)+辰(土)
# = 木2 火2 金1 水2 土1 → 无单行≥4
# 加大运丁(火)亥(水) → 火3 水3 → 仍无≥4
dy_list_7 = [{'gz': '丁亥', 'start_age': 5}]
result_7 = analyze_dayun_mangpai(dy_list_7, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_7 = result_7['dayun'][0]
check('无气势变化返回None', dy_7.get('qishi_change') is None,
      f"qishi_change={dy_7.get('qishi_change')}")

# 用一个五行密集的命局测试气势变化
# 全木命局：甲乙寅卯 + 大运甲→木≥4
dense_gans = ['甲', '乙', '庚', '甲']
dense_zhis = ['寅', '卯', '申', '辰']
# 木：甲+乙+甲=3天干 + 寅+卯=2地支 = 5 → 已≥4
dy_list_7b = [{'gz': '丙午', 'start_age': 5}]
result_7b = analyze_dayun_mangpai(dy_list_7b, dense_gans, dense_zhis, DAY_GAN)
dy_7b = result_7b['dayun'][0]
# 木5 + 丙(火)+午(火) → 木仍5≥4，火增加但未改变主导
# 如果木已≥4且火未达≥4，无变化
check('已有气势且未变化返回None', dy_7b.get('qishi_change') is None,
      f"qishi_change={dy_7b.get('qishi_change')}")

# ── 8. 大运综合吉凶评价 ──
print('\n── 8. 大运综合吉凶评价 ──')

# 禄运+长生→应该偏吉
dy_list_8 = [{'gz': '甲申', 'start_age': 5}]
result_8 = analyze_dayun_mangpai(dy_list_8, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_8 = result_8['dayun'][0]
check('禄运overall含吉信号', dy_8['overall'] in ('吉', '吉凶参半'),
      f"overall={dy_8['overall']}")
check('有正面信号', len(dy_8['positive_signals']) > 0,
      f"positive_signals={dy_8['positive_signals']}")

# 冲日支+穿→应该偏凶
dy_list_8b = [{'gz': '丁子', 'start_age': 5}]
result_8b = analyze_dayun_mangpai(dy_list_8b, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
dy_8b = result_8b['dayun'][0]
check('冲日支有负面信号', len(dy_8b['negative_signals']) > 0,
      f"negative_signals={dy_8b['negative_signals']}")
check('冲日支overall含凶信号', dy_8b['overall'] in ('凶', '吉凶参半'),
      f"overall={dy_8b['overall']}")

# ── 9. 流年与大运互动 ──
print('\n── 9. 流年与大运互动 ──')

# 流年子冲大运午
ln_list_9 = [{'gz': '丙子', 'year': 2024}]
current_dy = {'gan': '丁', 'zhi': '午'}
result_9 = analyze_liunian_mangpai(
    ln_list_9, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
    current_dayun=current_dy,
)
check('流年分析返回结果', result_9 is not None and 'liunian' in result_9)
ln_9 = result_9['liunian'][0]
dy_inter = ln_9.get('dayun_interaction', [])
check('流年大运互动检测到', len(dy_inter) > 0,
      f"dayun_interaction={dy_inter}")
chong_inter = [i for i in dy_inter if i['type'] == '冲']
check('子冲午(大运)检测到', len(chong_inter) >= 1,
      f"interactions={dy_inter}")

# 流年合大运
ln_list_9b = [{'gz': '丙未', 'year': 2024}]
result_9b = analyze_liunian_mangpai(
    ln_list_9b, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
    current_dayun=current_dy,
)
ln_9b = result_9b['liunian'][0]
he_inter = [i for i in ln_9b.get('dayun_interaction', []) if i['type'] == '六合']
check('未合午(大运)检测到', len(he_inter) >= 1,
      f"interactions={ln_9b.get('dayun_interaction')}")

# 无大运时也能工作
result_9c = analyze_liunian_mangpai(
    ln_list_9, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
)
check('无大运时流年分析正常', 'liunian' in result_9c and len(result_9c['liunian']) == 1)
check('无大运时无dayun_interaction', 'dayun_interaction' not in result_9c['liunian'][0])

# ── 10. 空亡折扣 ──
print('\n── 10. 空亡折扣 ──')

# 大运地支亥在空亡中
dy_list_10 = [{'gz': '丁亥', 'start_age': 5}]
result_10 = analyze_dayun_mangpai(
    dy_list_10, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
    kong_wang=['亥'],
)
dy_10 = result_10['dayun'][0]
check('大运亥空亡检测到', dy_10['is_kong_wang'] is True,
      f"is_kong_wang={dy_10['is_kong_wang']}")
check('空亡有负面信号', any('空亡' in s for s in dy_10['negative_signals']),
      f"negative_signals={dy_10['negative_signals']}")

# 非空亡
result_10b = analyze_dayun_mangpai(
    dy_list_10, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
    kong_wang=['子'],
)
dy_10b = result_10b['dayun'][0]
check('大运亥非空亡', dy_10b['is_kong_wang'] is False)

# dict格式空亡
result_10c = analyze_dayun_mangpai(
    dy_list_10, NATAL_GANS, NATAL_ZHIS, DAY_GAN,
    kong_wang={'zhi': ['亥']},
)
dy_10c = result_10c['dayun'][0]
check('dict格式空亡检测', dy_10c['is_kong_wang'] is True)

# ── 11. MangpaiEngine 集成 ──
print('\n── 11. MangpaiEngine 集成 ──')

# 无大运数据时不报错
bazi_data_no_dy = {
    'bazi': {'year': '甲寅', 'month': '丙子', 'day': '庚午', 'hour': '壬辰'},
    'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {}, 'input': {},
}
res_no_dy = MangpaiEngine(bazi_data_no_dy).compute_all()
check('无大运数据不报错', 'dayun_analysis' not in res_no_dy)
check('无大运数据其他模块正常', 'zuogong' in res_no_dy and 'bazi' in res_no_dy)

# 有大运数据时分析正确
bazi_data_with_dy = {
    'bazi': {'year': '甲寅', 'month': '丙子', 'day': '庚午', 'hour': '壬辰'},
    'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {}, 'input': {},
    'dayun': {
        'direction': '顺',
        'start_age': 5,
        'dayun': [
            {'gz': '丁丑', 'start_age': 5},
            {'gz': '戊寅', 'start_age': 15},
            {'gz': '己卯', 'start_age': 25},
        ],
    },
}
res_with_dy = MangpaiEngine(bazi_data_with_dy).compute_all()
check('有大运数据时dayun_analysis存在', 'dayun_analysis' in res_with_dy)
dy_analysis = res_with_dy.get('dayun_analysis', {})
check('大运分析3步', len(dy_analysis.get('dayun', [])) == 3,
      f"dayun count={len(dy_analysis.get('dayun', []))}")
check('大运分析含summary', 'summary' in dy_analysis and dy_analysis['summary'])
# summary中包含大运信息
check('总summary含大运', '大运' in res_with_dy.get('summary', ''),
      f"summary={res_with_dy.get('summary', '')}")

# 有流年数据时
bazi_data_with_ln = {
    'bazi': {'year': '甲寅', 'month': '丙子', 'day': '庚午', 'hour': '壬辰'},
    'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {}, 'input': {},
    'dayun': {
        'direction': '顺',
        'start_age': 5,
        'dayun': [{'gz': '丁丑', 'start_age': 5}],
    },
    'liunian': [
        {'gz': '甲辰', 'year': 2024},
        {'gz': '乙巳', 'year': 2025},
    ],
}
res_with_ln = MangpaiEngine(bazi_data_with_ln).compute_all()
check('有流年数据时liunian_analysis存在', 'liunian_analysis' in res_with_ln)
ln_analysis = res_with_ln.get('liunian_analysis', {})
check('流年分析2年', len(ln_analysis.get('liunian', [])) == 2,
      f"liunian count={len(ln_analysis.get('liunian', []))}")
ln_0 = ln_analysis.get('liunian', [{}])[0]
check('流年含大运互动', 'dayun_interaction' in ln_0,
      f"ln_0 keys={list(ln_0.keys())}")

# ── 12. 主观层 payload 集成 ──
print('\n── 12. 主观层 payload 集成 ──')

from subjective import build_payload, MANGPAI_SCHOOL
from subjective.schools import MANGPAI_SCHOOL as SCHOOL

check('selectors含dayun_analysis', 'dayun_analysis' in SCHOOL.selectors)
check('selectors含liunian_analysis', 'liunian_analysis' in SCHOOL.selectors)
check('selectors含chang_sheng', 'chang_sheng' in SCHOOL.selectors)
check('selectors含gongliang', 'gongliang' in SCHOOL.selectors)
check('selectors总数=40', len(SCHOOL.selectors) == 40,
      f"got {len(SCHOOL.selectors)}")

payload = build_payload(res_with_dy)
check('payload含dayun_analysis', 'dayun_analysis' in payload,
      f"payload keys={list(payload.keys())}")
check('payload不含liunian_analysis(无数据)', 'liunian_analysis' not in payload)

payload_ln = build_payload(res_with_ln)
check('payload含liunian_analysis(有数据)', 'liunian_analysis' in payload_ln)

# ── 13. 多步大运分析 ──
print('\n── 13. 多步大运分析 ──')

dy_list_13 = [
    {'gz': '丁丑', 'start_age': 5},
    {'gz': '戊寅', 'start_age': 15},
    {'gz': '己卯', 'start_age': 25},
    {'gz': '庚辰', 'start_age': 35},
    {'gz': '辛巳', 'start_age': 45},
]
result_13 = analyze_dayun_mangpai(dy_list_13, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
check('5步大运分析完成', len(result_13['dayun']) == 5)
check('summary含吉运数', '吉运' in result_13['summary'] or '凶运' in result_13['summary'] or '共5步' in result_13['summary'])
check('ji_count+xiong_count+banfeng_count<=5',
      result_13['ji_count'] + result_13['xiong_count'] + result_13['banfeng_count'] <= 5)

# 每步大运都有desc
all_have_desc = all(d.get('desc') for d in result_13['dayun'])
check('每步大运有desc', all_have_desc)

# ── 14. gan/zhi格式输入 ──
print('\n── 14. gan/zhi格式输入 ──')

dy_list_14 = [{'gan': '丁', 'zhi': '亥', 'start_age': 5}]
result_14 = analyze_dayun_mangpai(dy_list_14, NATAL_GANS, NATAL_ZHIS, DAY_GAN)
check('gan/zhi格式输入正常', len(result_14['dayun']) == 1)
check('gan/zhi格式gz正确', result_14['dayun'][0]['gz'] == '丁亥')

# ── 结果汇总 ──
print('\n' + '=' * 60)
print(f'验证结果: {passed} passed, {failed} failed, total {passed + failed}')
print('=' * 60)

sys.exit(1 if failed > 0 else 0)
