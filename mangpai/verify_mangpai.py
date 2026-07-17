"""
盲派客观层全量验证脚本

验证项：
1. 桃花（咸池）查表正确性 + 年支兼看
2. 驿马查表正确性 + 年支兼看
3. 墓用 from/to 方向（墓库=from/做功方，入墓方=to/被做功方）
4. 主动/被动做功分类（被动制 vs 被动合/生）
5. 穿提示（仅被动穿触发警告）
6. 合化条件（相邻+月令+无克破）
7. 藏干表（午含己、亥含甲）
8. 食伤归体
9. 暗合做功
10. 克破方向（WX_KE_ME）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.constants import (
    CANG_GAN_MANGPAI, HUA_YONG_MAP, WX_KE, WX_KE_ME, WX_SHENG,
    ZHI_WX, GAN_WX, TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI, AN_HE,
    TOMB_MAP, DI_ZHI, LU,
)
from mangpai.objective.shensha import (
    compute_shensha_ext, _TAO_HUA, _YI_MA,
    _TIAN_YI, _WEN_CHANG, _HUA_GAI,
)
from mangpai.subjective.zuogong_confirm import analyze_zuogong, assess_work_level
from mangpai.objective.tiyong import _TI_SHISHEN, _YONG_SHISHEN
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.muku import is_entomb
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


print('=' * 60)
print('盲派客观层全量验证')
print('=' * 60)

# ── 1. 桃花查表 ──
print('\n── 1. 桃花（咸池）查表 ──')

tao_expected = {
    '申': '酉', '子': '酉', '辰': '酉',
    '寅': '卯', '午': '卯', '戌': '卯',
    '亥': '子', '卯': '子', '未': '子',
    '巳': '午', '酉': '午', '丑': '午',
}
check('桃花表覆盖12支', len(_TAO_HUA) == 12)
for zhi, expected in tao_expected.items():
    check(f'桃花 {zhi}→{expected}', _TAO_HUA.get(zhi) == expected,
          f'got {_TAO_HUA.get(zhi)}')

# 验证三合局沐浴位
sanhe_groups = [
    (['申', '子', '辰'], '酉', '水局沐浴'),
    (['寅', '午', '戌'], '卯', '火局沐浴'),
    (['亥', '卯', '未'], '子', '木局沐浴'),
    (['巳', '酉', '丑'], '午', '金局沐浴'),
]
for members, expected_th, label in sanhe_groups:
    for m in members:
        check(f'{label}: {m}→{expected_th}', _TAO_HUA.get(m) == expected_th)

# 年支兼看测试（盲派以日支起，reference='day'）
ss = compute_shensha_ext('甲', ['寅', '午', '子', '戌'], reference='day')
check('桃花日支起(子→酉)', ss.get('桃花', {}).get('zhi') == '酉',
      f"got {ss.get('桃花', {}).get('zhi')}")
check('桃花年支兼看(寅→卯)', ss.get('桃花', {}).get('year_ref', {}).get('zhi') == '卯',
      f"got {ss.get('桃花', {}).get('year_ref', {}).get('zhi')}")

# 年支=日支时不重复
ss2 = compute_shensha_ext('甲', ['子', '午', '子', '戌'], reference='day')
check('年支=日支时无year_ref', ss2.get('桃花', {}).get('year_ref') is None)

# ── 2. 驿马查表 ──
print('\n── 2. 驿马查表 ──')

# 段氏「三支皆马」：每支映射其所属三合局之对冲三支；列表首位=长生之冲(传统单点)
ym_expected = {
    '申': ['寅', '午', '戌'], '子': ['寅', '午', '戌'], '辰': ['寅', '午', '戌'],
    '寅': ['申', '子', '辰'], '午': ['申', '子', '辰'], '戌': ['申', '子', '辰'],
    '亥': ['巳', '酉', '丑'], '卯': ['巳', '酉', '丑'], '未': ['巳', '酉', '丑'],
    '巳': ['亥', '卯', '未'], '酉': ['亥', '卯', '未'], '丑': ['亥', '卯', '未'],
}
check('驿马表覆盖12支', len(_YI_MA) == 12)
for zhi, expected in ym_expected.items():
    check(f'驿马 {zhi}→{expected}', _YI_MA.get(zhi) == expected,
          f'got {_YI_MA.get(zhi)}')

# 验证三合局对冲三支皆马：同局三支映射相同，且首位=长生之冲
chong_map = dict(LIU_CHONG) | {v: k for k, v in LIU_CHONG}
for members, _, label in sanhe_groups:
    changsheng = members[0]  # 长生位是三合局第一位
    expected_ym = chong_map.get(changsheng, '')
    for m in members:
        mapped = _YI_MA.get(m, [])
        check(f'{label}驿马首位: {m}→{expected_ym}(冲{changsheng})',
              mapped and mapped[0] == expected_ym,
              f'got {mapped}')
        check(f'{label}驿马三支: {m}→{mapped}(对冲三支)',
              len(mapped) == 3, f'got {mapped}')

# 年支兼看（reference='day'）；'zhi' 保留首位=传统单点，向后兼容
ss3 = compute_shensha_ext('甲', ['寅', '午', '子', '戌'], reference='day')
check('驿马日支起(子→寅首位)', ss3.get('驿马', {}).get('zhi') == '寅')
check('驿马日支起三支(子→寅午戌)', ss3.get('驿马', {}).get('zhis') == ['寅', '午', '戌'],
      f"got {ss3.get('驿马', {}).get('zhis')}")
check('驿马年支兼看(寅→申首位)', ss3.get('驿马', {}).get('year_ref', {}).get('zhi') == '申')

# ── 3. 墓用 from/to 方向 ──
print('\n── 3. 墓用 from/to 方向 ──')

# 日支为墓库(辰=水/土墓)，时支为亥(水，四生)→亥入辰墓
# 四生（寅申巳亥）见墓库入墓；四正（子午卯酉）见墓库不入墓（见 P0-3 规则）
# 日柱=辰(墓库)应为from(做功方)，时柱=亥(入墓方)应为to(被做功方)
zg = analyze_zuogong('戊', '辰', '甲', '寅', '丙', '午', '庚', '亥')
tomb_works = zg.get('tomb_works', [])
check('墓用检测到', len(tomb_works) > 0, '未检测到墓用')
if tomb_works:
    tw = tomb_works[0]
    check('墓用 from=墓库(日辰)', '辰' in tw.get('from', ''),
          f"got from={tw.get('from')}")
    check('墓用 to=入墓方(时亥)', '亥' in tw.get('to', ''),
          f"got to={tw.get('to')}")
    check('墓用 from_pos=day_zhi', tw.get('from_pos') == 'day_zhi',
          f"got from_pos={tw.get('from_pos')}")
    check('墓用 to_pos=hour_zhi', tw.get('to_pos') == 'hour_zhi',
          f"got to_pos={tw.get('to_pos')}")
    check('墓用 desc正确', '亥' in tw.get('desc', '') and '辰' in tw.get('desc', ''),
          f"got desc={tw.get('desc')}")

# 日支被入墓：日支=亥(水，四生)，时支=辰(水墓)→亥入辰墓
# 辰(墓库)=from(做功方)，亥(入墓方)=to(被做功方)
zg2 = analyze_zuogong('壬', '亥', '甲', '寅', '丙', '午', '庚', '辰')
tomb_works2 = zg2.get('tomb_works', [])
check('日支被入墓检测到', len(tomb_works2) > 0)
if tomb_works2:
    tw2 = tomb_works2[0]
    check('被入墓 from=墓库(时辰)', '辰' in tw2.get('from', ''),
          f"got from={tw2.get('from')}")
    check('被入墓 to=入墓方(日亥)', '亥' in tw2.get('to', ''),
          f"got to={tw2.get('to')}")
    check('被入墓 to_pos=day_zhi(被动)', tw2.get('to_pos') == 'day_zhi',
          f"got to_pos={tw2.get('to_pos')}")
    # 被入墓应出现在passive_control中
    pc = zg2.get('passive_control', [])
    check('被入墓计入passive_control',
          any(wa.get('type') == '墓用' for wa in pc),
          f"passive_control={pc}")

# 闭库抑制：墓库逢合而闭且无冲开时，不应产生墓用
# 辰(年支,水/土墓)+酉(月支,辰酉合→闭库)+亥(日支,水,应入辰墓但辰闭)
# 无戌冲辰→闭库，亥不应入辰墓
zg_closed = analyze_zuogong('壬', '亥', '辛', '酉', '甲', '辰', '丙', '午')
check('闭库抑制: 辰酉合闭→亥不入辰墓',
      len(zg_closed.get('tomb_works', [])) == 0,
      f"tomb_works={zg_closed.get('tomb_works')}")

# ── 4. 主动/被动做功分类 ──
print('\n── 4. 主动/被动做功分类 ──')

# 被动合不应计入passive_control
# 日支=丑，时支=子→子丑合，to_pos=day_zhi(被动合)
zg3 = analyze_zuogong('己', '丑', '甲', '寅', '丙', '午', '庚', '子')
pc3 = zg3.get('passive_control', [])
has_passive_he = any(
    wa.get('to_pos', '').startswith('day_') and wa.get('type') in ('地支合', '暗合', '天干合')
    for wa in zg3.get('work_actions', [])
)
check('被动合存在', has_passive_he, '未检测到被动合')
check('被动合不计入passive_control',
      not any(wa.get('type') in ('地支合', '暗合', '天干合') for wa in pc3),
      f"passive_control含合: {pc3}")

# 被动生不应计入passive_control
# 日支=卯(木)，年支=子(水)→子水生卯木，to_pos=day_zhi(被动生)
zg4 = analyze_zuogong('乙', '卯', '壬', '子', '丙', '午', '庚', '辰')
pc4 = zg4.get('passive_control', [])
has_passive_sheng = any(
    wa.get('to_pos', '').startswith('day_') and wa.get('type') == '生'
    for wa in zg4.get('work_actions', [])
)
check('被动生存在', has_passive_sheng, '未检测到被动生')
check('被动生不计入passive_control',
      not any(wa.get('type') == '生' for wa in pc4),
      f"passive_control含生: {pc4}")

# 被动克应计入passive_control
# 日支=卯(木)，时支=申(金)→申金克卯木，to_pos=day_zhi(被动克)
# 用申卯（纯克，无冲/刑/穿/破/合）而非酉卯（酉卯既冲又克，
# P0-1 去重后冲优先级高于克会把克去重掉，无法独立验证被动克）
zg5 = analyze_zuogong('乙', '卯', '甲', '寅', '丙', '午', '庚', '申')
pc5 = zg5.get('passive_control', [])
check('被动克计入passive_control',
      any(wa.get('type') == '克' for wa in pc5),
      f"passive_control={pc5}")

# 被动冲应计入passive_control
# 日支=午，年支=子→子午冲，to_pos=day_zhi(被动冲)
zg6 = analyze_zuogong('丙', '午', '壬', '子', '甲', '寅', '庚', '辰')
pc6 = zg6.get('passive_control', [])
check('被动冲计入passive_control',
      any(wa.get('type') == '冲' for wa in pc6),
      f"passive_control={pc6}")

# ── 5. 穿提示 ──
print('\n── 5. 穿提示（仅被动穿触发）──')

# 主动穿：日支穿时支，from_pos=day_zhi → 不应触发has_severe_harm
# 寅巳穿：日支=寅，时支=巳
zg7 = analyze_zuogong('甲', '寅', '壬', '子', '丙', '辰', '庚', '巳')
chuan_actions = [wa for wa in zg7.get('work_actions', []) if wa.get('type') == '穿']
check('穿检测到', len(chuan_actions) > 0, '未检测到穿')
if chuan_actions:
    has_active = any(wa.get('from_pos', '').startswith('day_') for wa in chuan_actions)
    has_passive = any(wa.get('to_pos', '').startswith('day_') for wa in chuan_actions)
    check('主动穿存在(from=day)', has_active, f'穿actions: {chuan_actions}')
    if has_active and not has_passive:
        check('主动穿不触发has_severe_harm', not zg7.get('has_severe_harm'),
              f"has_severe_harm={zg7.get('has_severe_harm')}")

# 被动穿：年支穿日支，to_pos=day_zhi → 应触发has_severe_harm
# 寅巳穿：日支=巳，年支=寅
zg8 = analyze_zuogong('丙', '巳', '庚', '寅', '甲', '辰', '壬', '子')
chuan_actions8 = [wa for wa in zg8.get('work_actions', []) if wa.get('type') == '穿']
if chuan_actions8:
    has_passive8 = any(wa.get('to_pos', '').startswith('day_') for wa in chuan_actions8)
    check('被动穿存在(to=day)', has_passive8, f'穿actions: {chuan_actions8}')
    if has_passive8:
        check('被动穿触发has_severe_harm', zg8.get('has_severe_harm'),
              f"has_severe_harm={zg8.get('has_severe_harm')}")

# ── 6. 合化条件 ──
print('\n── 6. 合化条件 ──')
# 注：化用已重定义为杀印相生（type='杀印相生'），天干合化为独立 action（type='合化'）。
# 本节验证合化条件，按 type=='合化' 过滤，不与杀印相生化用混淆。

# 甲己合化土：月令为土(辰)，日支非木(戌)，无木克破
# 日干=甲，月干=己，月支=辰(土)，日支=戌(土)→化土成功
zg_hua = analyze_zuogong('甲', '戌', '丙', '午', '己', '辰', '庚', '申')
hua_actions = [wa for wa in zg_hua.get('work_actions', []) if wa.get('type') == '合化']
check('甲己合化土(月辰无克破)', len(hua_actions) > 0,
      f'化用actions: {hua_actions}')

# 甲己合化土：月令为土但有木克破
# 日干=甲，月干=己，月支=辰(土)，日支=寅(木)→木克土，有克破
zg_hua2 = analyze_zuogong('甲', '寅', '丙', '午', '己', '辰', '庚', '申')
hua_actions2 = [wa for wa in zg_hua2.get('work_actions', []) if wa.get('type') == '合化']
check('甲己合化土(日寅木克破)', len(hua_actions2) == 0,
      f'不应化化但检测到: {hua_actions2}')

# 年干与日干不相邻，不能合化
# 日干=甲，年干=己，月干=丙，月支=辰(土)
zg_hua3 = analyze_zuogong('甲', '寅', '己', '酉', '丙', '辰', '庚', '申')
hua_actions3 = [wa for wa in zg_hua3.get('work_actions', []) if wa.get('type') == '合化']
check('年干日干不相邻不合化', len(hua_actions3) == 0,
      f'不应化化但检测到: {hua_actions3}')

# 月令非化气五行，不合化
# 日干=甲，月干=己，月支=寅(木)→月令非土
zg_hua4 = analyze_zuogong('甲', '子', '丙', '午', '己', '寅', '庚', '申')
hua_actions4 = [wa for wa in zg_hua4.get('work_actions', []) if wa.get('type') == '合化']
check('月令非化气不合化', len(hua_actions4) == 0,
      f'不应化化但检测到: {hua_actions4}')

# ── 7. 藏干表 ──
print('\n── 7. 藏干表 ──')

wu_canggan = get_canggan_mangpai('午')
check('午含丁(本气)', any(g == '丁' for g, _ in wu_canggan), f'got {wu_canggan}')
check('午含己(中气)', any(g == '己' for g, _ in wu_canggan), f'got {wu_canggan}')
check('午藏干数量=2', len(wu_canggan) == 2, f'got {len(wu_canggan)}')

hai_canggan = get_canggan_mangpai('亥')
check('亥含壬(本气)', any(g == '壬' for g, _ in hai_canggan), f'got {hai_canggan}')
check('亥含甲(中气)', any(g == '甲' for g, _ in hai_canggan), f'got {hai_canggan}')
check('亥不含戊', not any(g == '戊' for g, _ in hai_canggan), f'got {hai_canggan}')

# 全表验证
expected_canggan = {
    '子': [('癸', '本气')],
    '丑': [('己', '本气'), ('辛', '中气'), ('癸', '余气')],
    '寅': [('甲', '本气'), ('丙', '中气'), ('戊', '余气')],
    '卯': [('乙', '本气')],
    '辰': [('戊', '本气'), ('癸', '中气'), ('乙', '余气')],
    '巳': [('丙', '本气'), ('戊', '中气'), ('庚', '余气')],
    '午': [('丁', '本气'), ('己', '中气')],
    '未': [('己', '本气'), ('乙', '中气'), ('丁', '余气')],
    '申': [('庚', '本气'), ('壬', '中气'), ('戊', '余气')],
    '酉': [('辛', '本气')],
    '戌': [('戊', '本气'), ('丁', '中气'), ('辛', '余气')],
    '亥': [('壬', '本气'), ('甲', '中气')],
}
for zhi, expected in expected_canggan.items():
    actual = get_canggan_mangpai(zhi)
    check(f'藏干 {zhi}', actual == expected, f'got {actual}')

# ── 8. 食伤归体 ──
print('\n── 8. 食伤归体 ──')

check('食神∈体', '食神' in _TI_SHISHEN)
check('伤官∈体', '伤官' in _TI_SHISHEN)
check('正财∈用', '正财' in _YONG_SHISHEN)
check('偏财∈用', '偏财' in _YONG_SHISHEN)
check('正官∈用', '正官' in _YONG_SHISHEN)
check('七杀∈用', '七杀' in _YONG_SHISHEN)
check('正印∈体', '正印' in _TI_SHISHEN)
check('偏印∈体', '偏印' in _TI_SHISHEN)
check('比肩∈体', '比肩' in _TI_SHISHEN)
check('劫财∈体', '劫财' in _TI_SHISHEN)

# ── 9. 暗合做功 ──
print('\n── 9. 暗合做功 ──')

# 寅丑暗合：日支=寅，时支=丑→暗合做功
zg_anhe = analyze_zuogong('甲', '寅', '丙', '午', '己', '辰', '庚', '丑')
anhe_actions = [wa for wa in zg_anhe.get('work_actions', []) if wa.get('type') == '暗合']
check('寅丑暗合检测到', len(anhe_actions) > 0, '未检测到暗合')
if anhe_actions:
    check('暗合计入合用', '合用' in zg_anhe.get('work_types', []))
    check('暗合日支参与', any(
        'day' in wa.get('from_pos', '') or 'day' in wa.get('to_pos', '')
        for wa in anhe_actions
    ))

# 非日支参与的暗合不计入做功
# 年支=寅，月支=丑→暗合但不涉及日支
zg_anhe2 = analyze_zuogong('甲', '子', '丙', '寅', '己', '丑', '庚', '申')
anhe_actions2 = [wa for wa in zg_anhe2.get('work_actions', []) if wa.get('type') == '暗合']
check('非日支暗合不计入做功', len(anhe_actions2) == 0,
      f'检测到非日支暗合: {anhe_actions2}')

# AN_HE表双向验证
for a, b in [('寅', '丑'), ('午', '亥'), ('卯', '申'), ('子', '巳')]:
    check(f'暗合 {a}→{b}', AN_HE.get(a) == b)
    check(f'暗合 {b}→{a}', AN_HE.get(b) == a)

# ── 10. 克破方向 ──
print('\n── 10. 克破方向（WX_KE_ME）──')

# 验证WX_KE_ME正确性
check('WX_KE_ME 木→金(金克木)', WX_KE_ME.get('木') == '金')
check('WX_KE_ME 金→火(火克金)', WX_KE_ME.get('金') == '火')
check('WX_KE_ME 火→水(水克火)', WX_KE_ME.get('火') == '水')
check('WX_KE_ME 水→土(土克水)', WX_KE_ME.get('水') == '土')
check('WX_KE_ME 土→木(木克土)', WX_KE_ME.get('土') == '木')

# 验证合化克破方向：甲己合化土，克破元素=木(WX_KE_ME['土']='木')
check('化土克破=木', WX_KE_ME.get('土') == '木')
check('化金克破=火', WX_KE_ME.get('金') == '火')
check('化水克破=土', WX_KE_ME.get('水') == '土')
check('化木克破=金', WX_KE_ME.get('木') == '金')
check('化火克破=水', WX_KE_ME.get('火') == '水')

# HUA_YONG_MAP双向验证
for a, b, wx in [('甲', '己', '土'), ('乙', '庚', '金'),
                   ('丙', '辛', '水'), ('丁', '壬', '木'), ('戊', '癸', '火')]:
    check(f'合化 {a}{b}→{wx}', HUA_YONG_MAP.get((a, b)) == wx)
    check(f'合化 {b}{a}→{wx}', HUA_YONG_MAP.get((b, a)) == wx)

# ── 11. 做功层次评估 ──
print('\n── 11. 做功层次评估 ──')

# 无做功→Level 0
result0 = assess_work_level([], [], 0, None)
check('无做功→Level 0', result0['level'] == 0, f"got level={result0['level']}")

# 单类型→Level 1
result1 = assess_work_level(['制用'], [{'type': '冲'}], 0, None)
check('单类型→Level 1', result1['level'] == 1, f"got level={result1['level']}")

# 双类型→Level 2
result2 = assess_work_level(['制用', '合用'], [{'type': '冲'}, {'type': '地支合'}], 0, None)
check('双类型→Level 2', result2['level'] == 2, f"got level={result2['level']}")

# 三类型→Level 3
result3 = assess_work_level(['制用', '合用', '墓用'],
                            [{'type': '冲'}, {'type': '地支合'}, {'type': '墓用'}], 1, None)
check('三类型→Level 3', result3['level'] == 3, f"got level={result3['level']}")

# 主动做功加成
result_active = assess_work_level(['制用'],
    [{'type': '冲', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'},
     {'type': '克', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'}],
    0, None, active_work_count=2, passive_work_count=0, passive_control_count=0)
check('主动做功≥2→+1', result_active['level'] == 2,
      f"got level={result_active['level']}")

# 被动受制减分（只有被动制才减分）
result_pc = assess_work_level(['制用'],
    [{'type': '克', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi'},
     {'type': '冲', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi'}],
    0, None, active_work_count=0, passive_work_count=2, passive_control_count=2)
check('被动受制≥2→-1', result_pc['level'] == 0,
      f"got level={result_pc['level']}")

# 被动合不减分
result_ph = assess_work_level(['合用'],
    [{'type': '地支合', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi'},
     {'type': '暗合', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi'}],
    0, None, active_work_count=0, passive_work_count=2, passive_control_count=0)
check('被动合≥2不减分', result_ph['level'] == 1,
      f"got level={result_ph['level']}")

# 被动穿触发has_severe_harm
result_harm = assess_work_level(['制用'],
    [{'type': '穿', 'severity': 'high', 'to_pos': 'day_zhi', 'from_pos': 'hour_zhi'}],
    0, None)
check('被动穿→has_severe_harm=True', result_harm['has_severe_harm'])

# 主动穿不触发has_severe_harm
result_no_harm = assess_work_level(['制用'],
    [{'type': '穿', 'severity': 'high', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'}],
    0, None)
check('主动穿→has_severe_harm=False', not result_no_harm['has_severe_harm'])

# ── 12. 墓库表验证 ──
print('\n── 12. 墓库表 ──')

check('木墓在未', '木' in TOMB_MAP.get('未', []))
check('火墓在戌', '火' in TOMB_MAP.get('戌', []))
check('金墓在丑', '金' in TOMB_MAP.get('丑', []))
check('水墓在辰', '水' in TOMB_MAP.get('辰', []))
check('土墓在辰', '土' in TOMB_MAP.get('辰', []))

# ── 13. 六冲/六合/六害表验证 ──
print('\n── 13. 六冲/六合/六害表 ──')

check('六冲6组', len(LIU_CHONG) == 6)
check('六合6组', len(LIU_HE) == 6)
check('六害6组', len(LIU_HAI) == 6)

# 六冲验证
chong_expected = [('子', '午'), ('丑', '未'), ('寅', '申'),
                  ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
for a, b in chong_expected:
    found = (a, b) in LIU_CHONG or (b, a) in LIU_CHONG
    check(f'冲 {a}{b}', found)

# 六害验证
hai_expected = [('子', '未'), ('丑', '午'), ('寅', '巳'),
                ('卯', '辰'), ('申', '亥'), ('酉', '戌')]
for a, b in hai_expected:
    found = (a, b) in LIU_HAI or (b, a) in LIU_HAI
    check(f'穿 {a}{b}', found)

# ── 14. 反向做功 / 长生折扣 / 天干入墓 / 效率降级 ──
print('\n── 14. 反向做功 / 长生折扣 / 天干入墓 / 效率降级 ──')

# 14a. 反向做功（M1 direction）：from=主位用、to=宾位体 → direction=反向
# 日干甲（木）：酉=金=官杀(用)、寅=木=比劫(体)。
# 日支酉(主位)克月支寅(宾位)：from=day_zhi(用) → to=month_zhi(体) → 反向做功。
# 酉寅仅克（非冲刑穿破合），故该克动作不被去重、不降辅助。
zg_rev = analyze_zuogong('甲', '酉', '丙', '未', '戊', '寅', '庚', '未')
rev_actions = [wa for wa in zg_rev.get('work_actions', [])
               if wa.get('direction') == '反向']
check('反向做功检测到', len(rev_actions) >= 1,
      f"reverse_work_count={zg_rev.get('reverse_work_count')}")
check('反向做功 reverse_work_count>=1',
      zg_rev.get('reverse_work_count', 0) >= 1)
if rev_actions:
    wa = rev_actions[0]
    check('反向 from=主位(day)', wa.get('from_pos', '').startswith('day_'),
          f"from_pos={wa.get('from_pos')}")
    check('反向 to=宾位(month/year)',
          wa.get('to_pos', '').split('_')[0] in ('month', 'year'),
          f"to_pos={wa.get('to_pos')}")

# 14b. 长生折扣：日干在 action 所在柱处死/墓/绝 → efficiency_discount=True
# 日干甲在午=死。月支子冲日支午（被动冲），to_pos=day_zhi(午) → efficiency_discount。
zg_cs = analyze_zuogong('甲', '午', '壬', '巳', '戊', '子', '庚', '巳')
check('日干甲在午=死', zg_cs.get('day_changsheng', {}).get('午') == '死',
      f"day_changsheng={zg_cs.get('day_changsheng')}")
chong_actions = [wa for wa in zg_cs.get('work_actions', [])
                 if wa.get('type') == '冲']
check('子午冲检测到', len(chong_actions) > 0, '未检测到冲')
if chong_actions:
    check('长生折扣触发 efficiency_discount',
          chong_actions[0].get('efficiency_discount') is True,
          f"冲action={chong_actions[0]}")

# 14c. 天干入墓（M4）：天干坐墓 → 相关 actions 标记 gan_entombed + efficiency_discount
# 时干甲坐未（甲在未=墓）→ 时柱天干入墓。日支丑冲时支未（to_pos=hour）→ gan_entombed。
# 日干丙在丑=养、在未=衰，均非死/墓/绝，故 efficiency_discount 仅来自 M4（非长生折扣）。
zg_en = analyze_zuogong('丙', '丑', '戊', '巳', '庚', '巳', '甲', '未')
entombed_actions = [wa for wa in zg_en.get('work_actions', [])
                    if wa.get('gan_entombed')]
check('天干入墓动作检测到', len(entombed_actions) >= 1, '未检测到 gan_entombed')
if entombed_actions:
    wa = entombed_actions[0]
    check('天干入墓 gan_entombed=True', wa.get('gan_entombed') is True)
    check('天干入墓同时 efficiency_discount=True',
          wa.get('efficiency_discount') is True, f"action={wa}")
    check('天干入墓涉及时柱(甲坐未)',
          'hour' in wa.get('from_pos', '') or 'hour' in wa.get('to_pos', ''),
          f"from_pos={wa.get('from_pos')}, to_pos={wa.get('to_pos')}")

# 14d. 效率降级：折扣动作过半 → efficiency 降一级
# 日干甲在午=死。子午冲 + 午未合 均涉日支午(死) → 两动作皆折扣。
# 非辅助动作=2（type=制用+合用，基线效率=中），折扣过半 → 效率降为低。
# 干取壬癸乙（与甲唯生/比，无天干克），避免 P2-3 天干克干扰本效率用例。
zg_disc = analyze_zuogong('甲', '午', '壬', '巳', '癸', '子', '乙', '未')
non_aux_disc = [wa for wa in zg_disc.get('work_actions', [])
                if not wa.get('auxiliary')]
disc_count = sum(1 for wa in non_aux_disc if wa.get('efficiency_discount'))
check('效率降级: 非辅助动作=2', len(non_aux_disc) == 2,
      f"non_aux={len(non_aux_disc)}: {[wa.get('type') for wa in non_aux_disc]}")
check('效率降级: 折扣动作过半',
      disc_count > 0 and disc_count * 2 >= len(non_aux_disc),
      f"disc_count={disc_count}, non_aux={len(non_aux_disc)}")
check('效率降级: 效率=低(由中降一级)', zg_disc.get('work_efficiency') == '低',
      f"work_efficiency={zg_disc.get('work_efficiency')}")

# 14d-2. work_level 折扣直接验证：传 efficiency_discount_count → level 降一级
wl_base = assess_work_level(
    ['制用', '合用'], [{'type': '冲'}, {'type': '地支合'}], 0, None)
wl_disc = assess_work_level(
    ['制用', '合用'], [{'type': '冲'}, {'type': '地支合'}], 0, None,
    efficiency_discount_count=2)
check('work_level 基线(双类型无折扣)=Level 2', wl_base['level'] == 2,
      f"got level={wl_base['level']}")
check('work_level 折扣过半→Level 降一级',
      wl_disc['level'] == wl_base['level'] - 1,
      f"got level={wl_disc['level']}, base={wl_base['level']}")

# ── 15. S1 去重修复（P0-1）──
print('\n── 15. S1 去重修复（地支合入去重 + 无序键）──')

# 巳申对同时命中 地支合(巳申合)/克(巳火克申金)/刑(巳申刑)/破(巳申破)，
# 且 申 在年、巳 在日（申先巳后）→ 克 的 from/to 方向与冲/刑相反。
# 段氏优先级 冲>刑>穿>破>克>合>生，应只保留 刑 一条非辅助。
# 旧实现：'合'∉去重类型集合（实为'地支合'）+ 有序键 → 地支合/克/破/刑 全留存（4条）。
_P15_KEYS = ['year', 'month', 'day', 'hour']
_P15_ZHIS = ['申', '卯', '巳', '丑']


def _p15_zhi_of(pos):
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    return _P15_ZHIS[_P15_KEYS.index(p)] if t == 'zhi' else ''


zg_p1 = analyze_zuogong('丙', '巳', '庚', '申', '戊', '卯', '癸', '丑')
p1_pair = [wa for wa in zg_p1.get('work_actions', [])
           if {_p15_zhi_of(wa.get('from_pos', '')),
               _p15_zhi_of(wa.get('to_pos', ''))} == {'巳', '申'}]
p1_types = sorted({wa.get('type') for wa in p1_pair})
check('巳申对四类关系全命中', set(p1_types) == {'刑', '克', '地支合', '破'},
      f'got {p1_types}')
p1_non_aux = [wa for wa in p1_pair if not wa.get('auxiliary')]
check('巳申对去重后仅剩1条非辅助', len(p1_non_aux) == 1,
      f'non_aux={[w.get("type") for w in p1_non_aux]}')
check('巳申对保留最高优先级=刑',
      len(p1_non_aux) == 1 and p1_non_aux[0].get('type') == '刑',
      f'got {[w.get("type") for w in p1_non_aux]}')
# 子问题 a：地支合参与去重（被刑降为辅助）
check('地支合被刑去重为辅助',
      any(wa.get('type') == '地支合' and wa.get('auxiliary') for wa in p1_pair),
      f'地支合未降级: {[w for w in p1_pair if w.get("type")=="地支合"]}')
# 子问题 b：克方向相反但被无序键合并去重（被刑降为辅助）
check('反向克被无序键合并去重为辅助',
      any(wa.get('type') == '克' and wa.get('auxiliary') for wa in p1_pair),
      f'克未降级: {[w for w in p1_pair if w.get("type")=="克"]}')

# ── 16. 四库入墓误判修复（P0-2）──
print('\n── 16. 四库入墓误判修复（四库走多而入墓）──')

# is_entomb 单元验证
# 四库(戌)入辰墓：辰戌同土，盘上仅一戌（非多）→ 不入墓
check('is_entomb 四库非多不入墓(戌入辰)',
      is_entomb('戌', '辰', ['子', '寅', '辰', '戌']) is False)
# 四库多而入墓：未+戌两土（除墓库辰）→ 入墓
check('is_entomb 四库多而入墓(戌入辰)',
      is_entomb('戌', '辰', ['未', '寅', '辰', '戌']) is True)
# 四生入墓不变：亥(水,四生)见辰(水墓) → 入墓
check('is_entomb 四生入墓不变(亥入辰)',
      is_entomb('亥', '辰', ['寅', '午', '辰', '亥']) is True)
# 四正非多不入墓：子(水,四正)见辰(水墓)，仅一水 → 不入墓
check('is_entomb 四正非多不入墓(子入辰)',
      is_entomb('子', '辰', ['子', '午', '辰', '戌']) is False)
# 四正多而入墓：两酉见丑(金墓) → 入墓（排除墓库丑不影响计数）
check('is_entomb 四正多而入墓(两酉见丑)',
      is_entomb('酉', '丑', ['酉', '酉', '丑', '午']) is True)

# 端到端：辰戌冲的盘不应产生戌入辰墓
# zhis=[子,寅,辰,戌]，日辰时戌辰戌冲；辰戌同土但仅一戌（非多）→ 无墓用
zg_cv = analyze_zuogong('戊', '辰', '甲', '子', '丙', '寅', '庚', '戌')
cv_tombs = zg_cv.get('tomb_works', [])
check('辰戌冲不产生戌入辰墓',
      not any(wa.get('type') == '墓用' and '戌' in wa.get('to', '')
              and '辰' in wa.get('from', '') for wa in cv_tombs),
      f'tomb_works={cv_tombs}')
# 多而入墓端到端：未+戌两土 → 戌入辰墓应产生
zg_duo = analyze_zuogong('戊', '辰', '己', '未', '丙', '寅', '庚', '戌')
duo_tombs = zg_duo.get('tomb_works', [])
check('四库多而入墓端到端(戌入辰)',
      any(wa.get('type') == '墓用' and '戌' in wa.get('to', '')
          and '辰' in wa.get('from', '') for wa in duo_tombs),
      f'tomb_works={duo_tombs}')

# ── 17. 空亡接入做功（P1-1）──
print('\n── 17. 空亡接入做功 ──')

# 午子冲涉空亡地支(子) → efficiency_discount=True。丙在午=帝旺、在子=胎，
# 均非死/墓/绝，故无空亡时该冲不打折——可判别折扣确由空亡引起。


def _kw_chong(zg):
    for wa in zg.get('work_actions', []):
        if (wa.get('type') == '冲' and not wa.get('auxiliary')
                and '午' in wa.get('desc', '') and '子' in wa.get('desc', '')):
            return wa
    return None


zg_kw_no = analyze_zuogong('丙', '午', '己', '巳', '戊', '辰', '壬', '子')
zg_kw_list = analyze_zuogong('丙', '午', '己', '巳', '戊', '辰', '壬', '子',
                             kong_wang=['子'])
zg_kw_dict = analyze_zuogong('丙', '午', '己', '巳', '戊', '辰', '壬', '子',
                             kong_wang={'zhi': ['子']})
# 无空亡：午子冲不打折（判别器）
check('无空亡午子冲不打折',
      not _kw_chong(zg_kw_no).get('efficiency_discount'),
      f"action={_kw_chong(zg_kw_no)}")
# list 形态空亡：午子冲(涉子)打折
wa_kw_list = _kw_chong(zg_kw_list)
check('空亡(list)地支参与做功打折',
      wa_kw_list.get('efficiency_discount') is True, f"action={wa_kw_list}")
check('空亡动作标 kong_wang=True', wa_kw_list.get('kong_wang') is True)
# dict 形态空亡：同样打折
wa_kw_dict = _kw_chong(zg_kw_dict)
check('空亡(dict)地支参与做功打折',
      wa_kw_dict.get('efficiency_discount') is True, f"action={wa_kw_dict}")
# 结果透传空亡地支集合
check('kong_wang_zhis 透传',
      zg_kw_list.get('kong_wang_zhis') == ['子'],
      f"got {zg_kw_list.get('kong_wang_zhis')}")
# 空亡仅作用于地支动作：天干层面(食伤)不标 kong_wang
shishang_kw = [wa for wa in zg_kw_list.get('work_actions', [])
               if wa.get('type') == '食伤']
check('空亡不影响天干层面动作',
      bool(shishang_kw) and all(not wa.get('kong_wang') for wa in shishang_kw),
      f"食伤被标空亡: {shishang_kw}")

# __init__.py 透传 kong_wang 至 analyze_zuogong
bazi_data_kw = {
    'bazi': {'year': '己巳', 'month': '戊辰', 'day': '丙午', 'hour': '壬子'},
    'shishen': {}, 'kong_wang': {'zhi': ['子']},
    'di_zhi_relations': {}, 'input': {},
}
res_kw = MangpaiEngine(bazi_data_kw).compute_all()
check('MangpaiEngine 透传 kong_wang',
      res_kw.get('zuogong', {}).get('kong_wang_zhis') == ['子'],
      f"got {res_kw.get('zuogong', {}).get('kong_wang_zhis')}")
check('MangpaiEngine 空亡做功打折',
      _kw_chong(res_kw.get('zuogong', {})).get('efficiency_discount') is True,
      f"action={_kw_chong(res_kw.get('zuogong', {}))}")

# ── 18. 反向做功降级（P1-2）──
print('\n── 18. 反向做功降级（不+1，仅参考信号）──')

# 反向做功≥2 不再 +1 level，仅在 desc 加注"含反向做功"参考信号
# 单类型 base=Level 1，reverse=2 → 旧逻辑 +1=2，新逻辑保持 1
wl_rev1 = assess_work_level(['制用'], [{'type': '冲'}], 0, None, reverse_work_count=2)
check('反向做功不+1(单类型保持Level 1)', wl_rev1['level'] == 1,
      f"got level={wl_rev1['level']}")
check('反向做功 desc含参考信号', '含反向做功' in wl_rev1['desc'],
      f"desc={wl_rev1['desc']}")
# 双类型 base=Level 2，reverse=2 → 旧逻辑 +1=3，新逻辑保持 2
wl_rev2 = assess_work_level(['制用', '合用'],
                            [{'type': '冲'}, {'type': '地支合'}], 0, None,
                            reverse_work_count=2)
check('反向做功不+1(双类型保持Level 2)', wl_rev2['level'] == 2,
      f"got level={wl_rev2['level']}")
# 无反向做功 → desc 不含参考信号
wl_rev0 = assess_work_level(['制用'], [{'type': '冲'}], 0, None, reverse_work_count=0)
check('无反向做功 desc不含参考信号', '含反向做功' not in wl_rev0['desc'],
      f"desc={wl_rev0['desc']}")
# 端到端：14a 反向做功盘 → work_level_desc 含参考信号
zg_rev_desc = analyze_zuogong('甲', '酉', '丙', '未', '戊', '寅', '庚', '未')
check('反向做功盘 desc含参考信号',
      '含反向做功' in zg_rev_desc.get('work_level_desc', ''),
      f"desc={zg_rev_desc.get('work_level_desc')}")

# ── 19. 伏吟/反吟检测（P2-1）──
print('\n── 19. 伏吟/反吟检测 ──')

# 伏吟：日支寅、时支寅（寅寅，非自刑）→ type=伏吟
zg_fu = analyze_zuogong('甲', '寅', '乙', '卯', '丙', '子', '丁', '寅')
fu = [wa for wa in zg_fu.get('work_actions', []) if wa.get('type') == '伏吟']
check('伏吟检测到(寅寅)', len(fu) >= 1, '未检测到伏吟')
if fu:
    check('伏吟日柱参与',
          'day' in fu[0].get('from_pos', '') or 'day' in fu[0].get('to_pos', ''),
          f"from_pos={fu[0].get('from_pos')}")
    check('伏吟 desc含寅寅', '寅' in fu[0].get('desc', ''))

# 自刑(辰辰)不加伏吟——自刑已有 type=刑，不重复
zg_zx = analyze_zuogong('戊', '辰', '乙', '寅', '丙', '巳', '甲', '辰')
fu_zx = [wa for wa in zg_zx.get('work_actions', []) if wa.get('type') == '伏吟']
xing_zx = [wa for wa in zg_zx.get('work_actions', []) if wa.get('type') == '刑']
check('自刑(辰辰)不加伏吟', len(fu_zx) == 0,
      f'检测到伏吟: {fu_zx}')
check('自刑(辰辰)仍计刑',
      any('自刑' in wa.get('desc', '') for wa in xing_zx),
      f'刑actions: {xing_zx}')

# 反吟：日甲子、时庚午（甲庚相克 + 子午冲 = 天克地冲）→ type=反吟 severity=high
zg_fan = analyze_zuogong('甲', '子', '戊', '巳', '壬', '亥', '庚', '午')
fan = [wa for wa in zg_fan.get('work_actions', []) if wa.get('type') == '反吟']
check('反吟检测到(甲子庚午天克地冲)', len(fan) >= 1, '未检测到反吟')
if fan:
    check('反吟 severity=high', fan[0].get('severity') == 'high',
          f"severity={fan[0].get('severity')}")
    check('反吟日柱参与',
          'day' in fan[0].get('from_pos', '') or 'day' in fan[0].get('to_pos', ''),
          f"from_pos={fan[0].get('from_pos')}")
    check('反吟 desc含天克地冲', '天克地冲' in fan[0].get('desc', ''))

# 负例：日甲子、时丙午（甲生丙，天干相生非克）→ 不应反吟
zg_fan_neg = analyze_zuogong('甲', '子', '戊', '巳', '壬', '亥', '丙', '午')
fan_neg = [wa for wa in zg_fan_neg.get('work_actions', [])
           if wa.get('type') == '反吟']
check('天干相生非克不反吟', len(fan_neg) == 0,
      f'误检测反吟: {fan_neg}')

# ── 20. 禄做功（P2-2）──
print('\n── 20. 禄做功 ──')

# 禄位表（段氏）
lu_expected = {
    '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
    '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子',
}
check('禄表覆盖10干', len(LU) == 10)
for g, z in lu_expected.items():
    check(f'禄 {g}→{z}', LU.get(g) == z, f'got {LU.get(g)}')

# 自坐禄：日庚申（庚禄申在日支），无其他做功 → 禄做功
zg_lu = analyze_zuogong('庚', '申', '癸', '未', '丁', '戌', '丙', '酉')
check('自坐禄 primary_work 升级',
      zg_lu['primary_work'].get('lu_in_zhu') is True,
      f"primary_work={zg_lu['primary_work']}")
check('自坐禄 禄action 检测到',
      any(wa.get('type') == '禄' for wa in zg_lu['work_actions']),
      '未检测到禄action')
lu_act = [wa for wa in zg_lu['work_actions'] if wa.get('type') == '禄']
if lu_act:
    check('自坐禄 禄action primary=True', lu_act[0].get('primary') is True)
    check('自坐禄 禄在日支', lu_act[0].get('to_pos') == 'day_zhi',
          f"to_pos={lu_act[0].get('to_pos')}")

# 时禄：日丙午、时壬巳（丙禄巳在时支），无其他做功 → 禄做功
zg_hlu = analyze_zuogong('丙', '午', '甲', '辰', '丁', '辰', '乙', '巳')
check('时禄 primary_work 升级',
      zg_hlu['primary_work'].get('lu_in_zhu') is True,
      f"primary_work={zg_hlu['primary_work']}")
hlu_act = [wa for wa in zg_hlu['work_actions'] if wa.get('type') == '禄']
check('时禄 禄action 检测到', len(hlu_act) >= 1)
if hlu_act:
    check('时禄 禄在时支', hlu_act[0].get('to_pos') == 'hour_zhi',
          f"to_pos={hlu_act[0].get('to_pos')}")

# 禄不在主位（在宾位月柱）且日柱确无做功：primary_work 保持通用禄比 label，无禄action
# 注：此柱组刻意避开日柱六合/暗合/天干克，以纯化"俱不做功"fallback 的覆盖
# （日柱有做功的情形由下方 禄分支触发守卫 三例覆盖）。
zg_nolu = analyze_zuogong('丙', '辰', '甲', '未', '乙', '巳', '丁', '午')
check('禄在宾位 不升级(通用label)',
      zg_nolu['primary_work'].get('lu_in_zhu') is None
      and '俱不做功' in zg_nolu['primary_work'].get('path', ''),
      f"primary_work={zg_nolu['primary_work']}")
check('禄在宾位 无禄action',
      not any(wa.get('type') == '禄' for wa in zg_nolu['work_actions']))

# ── 禄分支触发守卫（P2-2 修复回归）──
# zhi_actions 过滤器（弃干看支）不认日支六合/暗合、也不认日干主动克(天干克)，
# 旧逻辑以 primary_action is None 触发禄分支，导致这些日柱做功场景误追加伪禄 action
# 或误标 primary_work。修复后禄分支以"日柱确无做功"为前置，下列三例回归：

# a) 天干克 + 禄在主位：日庚申（庚禄申自坐主位），庚金克甲木（日干主动克）→
#    日柱已有制用做功，不应触发禄分支（无伪禄action，primary_work 非禄）
zg_a = analyze_zuogong('庚', '申', '甲', '酉', '戊', '戌', '己', '未')
check('天干克+禄在主位 不触禄(无禄action)',
      not any(wa.get('type') == '禄' for wa in zg_a['work_actions']),
      f"work_actions含禄: {[wa.get('type') for wa in zg_a['work_actions']]}")
check('天干克+禄在主位 primary_work 非禄',
      '禄做功' not in zg_a['primary_work'].get('path', '')
      and zg_a['primary_work'].get('lu_in_zhu') is None,
      f"primary_work={zg_a['primary_work']}")
check('天干克+禄在主位 primary_work 为制用',
      zg_a['primary_work'].get('type') == '制用'
      and '克做功' in zg_a['primary_work'].get('path', ''),
      f"primary_work={zg_a['primary_work']}")

# b) 日支六合 + 禄在主位：日丁午（丁禄午自坐主位），午未六合（日支参与）→
#    日柱已有合用做功，不应触发禄分支（无伪禄action，primary_work 为合用非禄）
zg_b = analyze_zuogong('丁', '午', '甲', '辰', '乙', '巳', '丙', '未')
check('日支六合+禄在主位 不触禄(无禄action)',
      not any(wa.get('type') == '禄' for wa in zg_b['work_actions']),
      f"work_actions含禄: {[wa.get('type') for wa in zg_b['work_actions']]}")
check('日支六合+禄在主位 primary_work 非禄',
      '禄做功' not in zg_b['primary_work'].get('path', '')
      and zg_b['primary_work'].get('lu_in_zhu') is None,
      f"primary_work={zg_b['primary_work']}")
check('日支六合+禄在主位 primary_work 为合用',
      zg_b['primary_work'].get('type') == '合用'
      and '合用做功' in zg_b['primary_work'].get('path', ''),
      f"primary_work={zg_b['primary_work']}")

# c) 天干克 + 禄不在主位：日庚酉，庚禄申在宾位年柱，庚金克甲木（日干主动克）→
#    日柱已有制用做功，primary_work.path 应反映实际做功而非"俱不做功"
zg_c = analyze_zuogong('庚', '酉', '甲', '申', '丙', '亥', '戊', '未')
check('天干克+禄不在主位 path 不含俱不做功',
      '俱不做功' not in zg_c['primary_work'].get('path', ''),
      f"primary_work={zg_c['primary_work']}")
check('天干克+禄不在主位 primary_work 为制用',
      zg_c['primary_work'].get('type') == '制用'
      and '克做功' in zg_c['primary_work'].get('path', ''),
      f"primary_work={zg_c['primary_work']}")
check('天干克+禄不在主位 无禄action',
      not any(wa.get('type') == '禄' for wa in zg_c['work_actions']))

# ── 21. 天干克（P2-3）──
print('\n── 21. 天干克 ──')

# 天干克(被动)：日甲、时庚（庚金克甲木，非合对）→ type=克，from/to 为干
zg_gk = analyze_zuogong('甲', '子', '壬', '巳', '癸', '亥', '庚', '午')
gk = [wa for wa in zg_gk.get('work_actions', [])
      if wa.get('type') == '克' and wa.get('from_pos', '').endswith('_gan')]
check('天干克检测到(庚克甲)', len(gk) >= 1, '未检测到天干克')
if gk:
    check('天干克 from/to 为干位',
          gk[0].get('from_pos', '').endswith('_gan')
          and gk[0].get('to_pos', '').endswith('_gan'))
    check('天干克 日干参与',
          'day' in gk[0].get('from_pos', '') or 'day' in gk[0].get('to_pos', ''))
    check('天干克 desc含庚克甲', '庚' in gk[0].get('desc', '') and '甲' in gk[0].get('desc', ''))
check('天干克计入制用', '制用' in zg_gk.get('work_types', []))
# 庚克甲(to=day_gan) → 被动受制，计入 passive_control
check('天干克(庚克甲)计入passive_control',
      any(wa.get('type') == '克' and wa.get('to_pos') == 'day_gan'
          for wa in zg_gk.get('passive_control', [])))

# 天干克(主动)：日甲、时戊（甲木克戊土，非合对）→ from=day_gan 主动做功
# （M4 后列表或含宾位干克扩展检出，断言用 any 不按列表首位）
zg_gk2 = analyze_zuogong('甲', '子', '壬', '巳', '癸', '亥', '戊', '午')
gk2 = [wa for wa in zg_gk2.get('work_actions', [])
       if wa.get('type') == '克' and wa.get('from_pos', '').endswith('_gan')]
check('天干克主动(甲克戊)', any(wa.get('from_pos') == 'day_gan' for wa in gk2),
      f"gk2={gk2}")
check('天干克主动计入active_work',
      any(wa.get('type') == '克' and wa.get('from_pos') == 'day_gan'
          for wa in zg_gk2.get('active_work', [])))

# 天干克与支克共用 type=克：干克(_gan)与支冲(_zhi)可并存不冲突
gk_gan_pos = [wa for wa in zg_gk.get('work_actions', [])
              if wa.get('type') == '克' and wa.get('from_pos', '').endswith('_gan')]
chong_zhi = [wa for wa in zg_gk.get('work_actions', [])
             if wa.get('type') == '冲' and wa.get('from_pos', '').endswith('_zhi')
             and ('day' in wa.get('from_pos', '') or 'day' in wa.get('to_pos', ''))]
check('干克(_gan)与支冲(_zhi)并存不冲突',
      len(gk_gan_pos) >= 1 and len(chong_zhi) >= 1,
      f'gan克={len(gk_gan_pos)}, 支冲={len(chong_zhi)}')

# 合对(甲己)不计天干克——合为主动关系，不以克论
zg_he = analyze_zuogong('甲', '丑', '癸', '巳', '己', '亥', '壬', '卯')
check('甲己天干合检测到',
      any(wa.get('type') == '天干合' for wa in zg_he.get('work_actions', [])))
jiaji_gk = [wa for wa in zg_he.get('work_actions', [])
            if wa.get('type') == '克' and wa.get('from_pos', '').endswith('_gan')
            and {wa.get('from_pos'), wa.get('to_pos')} == {'day_gan', 'month_gan'}]
check('合对(甲己)不计天干克', len(jiaji_gk) == 0,
      f'误计天干克: {jiaji_gk}')

# ── 22. 天乙贵人（按日干起）──
print('\n── 22. 天乙贵人（按日干起）──')

ty_expected = {
    '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
    '乙': ['子', '申'], '己': ['子', '申'],
    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
    '壬': ['卯', '巳'], '癸': ['卯', '巳'],
    '辛': ['寅', '午'],
}
check('天乙表覆盖10干', len(_TIAN_YI) == 10)
for gan, expected in ty_expected.items():
    check(f'天乙 {gan}→{expected}', _TIAN_YI.get(gan) == expected,
          f'got {_TIAN_YI.get(gan)}')
    check(f'天乙 {gan} 两位贵人', len(_TIAN_YI.get(gan, [])) == 2)

# 口诀分组验证：甲戊庚牛羊、乙己鼠猴乡、丙丁猪鸡位、壬癸兔蛇藏、六辛逢虎马
check('天乙 甲戊庚同组(丑未)',
      _TIAN_YI['甲'] == _TIAN_YI['戊'] == _TIAN_YI['庚'] == ['丑', '未'])
check('天乙 乙己同组(子申)',
      _TIAN_YI['乙'] == _TIAN_YI['己'] == ['子', '申'])
check('天乙 丙丁同组(亥酉)',
      _TIAN_YI['丙'] == _TIAN_YI['丁'] == ['亥', '酉'])
check('天乙 壬癸同组(卯巳)',
      _TIAN_YI['壬'] == _TIAN_YI['癸'] == ['卯', '巳'])
check('天乙 辛独组(寅午)', _TIAN_YI['辛'] == ['寅', '午'])

# 端到端：日干甲（贵人丑未），月支丑→检测到
ss_ty = compute_shensha_ext('甲', ['寅', '丑', '子', '戌'], reference='day')
check('天乙 甲贵人=[丑,未]', ss_ty.get('天乙贵人', {}).get('zhis') == ['丑', '未'],
      f"got {ss_ty.get('天乙贵人', {}).get('zhis')}")
check('天乙 丑在月支检测到',
      ss_ty.get('天乙贵人', {}).get('in_pillars') == ['month'],
      f"got {ss_ty.get('天乙贵人', {}).get('in_pillars')}")

# 两位贵人同时出现（年未月丑）
ss_ty2 = compute_shensha_ext('甲', ['未', '丑', '子', '戌'], reference='day')
check('天乙 丑未同现(年月)',
      set(ss_ty2.get('天乙贵人', {}).get('in_pillars', [])) == {'year', 'month'},
      f"got {ss_ty2.get('天乙贵人', {}).get('in_pillars')}")

# 无贵人地支
ss_ty3 = compute_shensha_ext('甲', ['寅', '卯', '子', '戌'], reference='day')
check('天乙 无贵人地支',
      ss_ty3.get('天乙贵人', {}).get('in_pillars') == [],
      f"got {ss_ty3.get('天乙贵人', {}).get('in_pillars')}")

# 日干丙（贵人亥酉），年支亥→检测到
ss_ty4 = compute_shensha_ext('丙', ['亥', '卯', '午', '戌'], reference='day')
check('天乙 丙贵人亥在年支',
      ss_ty4.get('天乙贵人', {}).get('in_pillars') == ['year'],
      f"got {ss_ty4.get('天乙贵人', {}).get('in_pillars')}")

# ── 23. 文昌（按日干起）──
print('\n── 23. 文昌（按日干起）──')

wc_expected = {
    '甲': '巳', '乙': '午', '丙': '申', '戊': '申',
    '丁': '酉', '己': '酉', '庚': '亥', '辛': '子',
    '壬': '寅', '癸': '卯',
}
check('文昌表覆盖10干', len(_WEN_CHANG) == 10)
for gan, expected in wc_expected.items():
    check(f'文昌 {gan}→{expected}', _WEN_CHANG.get(gan) == expected,
          f'got {_WEN_CHANG.get(gan)}')

# 口诀验证：丙戊同位(申)、丁己同位(酉)
check('文昌 丙戊同位(申)', _WEN_CHANG['丙'] == _WEN_CHANG['戊'] == '申')
check('文昌 丁己同位(酉)', _WEN_CHANG['丁'] == _WEN_CHANG['己'] == '酉')

# 端到端：日干甲（文昌巳），时支巳→检测到
ss_wc = compute_shensha_ext('甲', ['寅', '午', '子', '巳'], reference='day')
check('文昌 甲→巳', ss_wc.get('文昌', {}).get('zhi') == '巳',
      f"got {ss_wc.get('文昌', {}).get('zhi')}")
check('文昌 巳在时支检测到',
      ss_wc.get('文昌', {}).get('in_pillars') == ['hour'],
      f"got {ss_wc.get('文昌', {}).get('in_pillars')}")

# 文昌不在柱中
ss_wc2 = compute_shensha_ext('甲', ['寅', '午', '子', '戌'], reference='day')
check('文昌 不在柱中',
      ss_wc2.get('文昌', {}).get('in_pillars') == [],
      f"got {ss_wc2.get('文昌', {}).get('in_pillars')}")

# 日干庚（文昌亥），月支亥→检测到
ss_wc3 = compute_shensha_ext('庚', ['辰', '亥', '申', '子'], reference='day')
check('文昌 庚→亥', ss_wc3.get('文昌', {}).get('zhi') == '亥',
      f"got {ss_wc3.get('文昌', {}).get('zhi')}")
check('文昌 亥在月支检测到',
      ss_wc3.get('文昌', {}).get('in_pillars') == ['month'],
      f"got {ss_wc3.get('文昌', {}).get('in_pillars')}")

# ── 24. 华盖（按日柱起，日柱优先，兼看年柱）──
print('\n── 24. 华盖（按日柱起，日柱优先）──')

hg_expected = {
    '寅': '戌', '午': '戌', '戌': '戌',
    '申': '辰', '子': '辰', '辰': '辰',
    '巳': '丑', '酉': '丑', '丑': '丑',
    '亥': '未', '卯': '未', '未': '未',
}
check('华盖表覆盖12支', len(_HUA_GAI) == 12)
for zhi, expected in hg_expected.items():
    check(f'华盖 {zhi}→{expected}', _HUA_GAI.get(zhi) == expected,
          f'got {_HUA_GAI.get(zhi)}')

# 华盖=三合局墓库位验证
# 寅午戌火局→火墓戌；申子辰水局→水墓辰；巳酉丑金局→金墓丑；亥卯未木局→木墓未
sanhe_huagai = [
    (['寅', '午', '戌'], '戌', '火'),
    (['申', '子', '辰'], '辰', '水'),
    (['巳', '酉', '丑'], '丑', '金'),
    (['亥', '卯', '未'], '未', '木'),
]
for members, expected_hg, wx in sanhe_huagai:
    # 华盖位应是该五行墓库（TOMB_MAP 键值反向验证）
    check(f'华盖 {wx}局墓库={expected_hg}',
          wx in TOMB_MAP.get(expected_hg, []),
          f'TOMB_MAP[{expected_hg}]={TOMB_MAP.get(expected_hg)}')
    for m in members:
        check(f'华盖 {wx}局: {m}→{expected_hg}', _HUA_GAI.get(m) == expected_hg)

# 端到端：日支寅（华盖戌），时支戌→检测到，reference=day_zhi
ss_hg = compute_shensha_ext('甲', ['申', '午', '寅', '戌'], reference='day')
check('华盖 日支寅→戌', ss_hg.get('华盖', {}).get('zhi') == '戌',
      f"got {ss_hg.get('华盖', {}).get('zhi')}")
check('华盖 reference=day_zhi', ss_hg.get('华盖', {}).get('reference') == 'day_zhi')
check('华盖 戌在时支检测到',
      ss_hg.get('华盖', {}).get('in_pillars') == ['hour'],
      f"got {ss_hg.get('华盖', {}).get('in_pillars')}")

# 日柱优先：日支寅(华盖戌)，年支申(华盖辰)→主取日柱戌，年柱辰入year_ref
ss_hg2 = compute_shensha_ext('甲', ['申', '午', '寅', '戌'], reference='day')
check('华盖 日柱优先(戌)', ss_hg2.get('华盖', {}).get('zhi') == '戌')
check('华盖 年支兼看(申→辰)',
      ss_hg2.get('华盖', {}).get('year_ref', {}).get('zhi') == '辰',
      f"got {ss_hg2.get('华盖', {}).get('year_ref')}")
check('华盖 年支兼看 reference=year_zhi',
      ss_hg2.get('华盖', {}).get('year_ref', {}).get('reference') == 'year_zhi')

# 年支=日支同三合局（华盖相同）→无year_ref
ss_hg3 = compute_shensha_ext('甲', ['午', '辰', '寅', '戌'], reference='day')
check('华盖 年日同局无year_ref',
      ss_hg3.get('华盖', {}).get('year_ref') is None,
      f"got {ss_hg3.get('华盖', {}).get('year_ref')}")

# 华盖不在柱中（日支寅→戌，柱中无戌）
ss_hg4 = compute_shensha_ext('甲', ['申', '子', '寅', '辰'], reference='day')
check('华盖 戌不在柱中',
      ss_hg4.get('华盖', {}).get('in_pillars') == [],
      f"got {ss_hg4.get('华盖', {}).get('in_pillars')}")

# ── 结果汇总 ──
print('\n' + '=' * 60)
print(f'验证结果: {passed} passed, {failed} failed, total {passed + failed}')
print('=' * 60)

sys.exit(1 if failed > 0 else 0)
