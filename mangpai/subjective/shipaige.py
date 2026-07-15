"""
shipaige — 郑民生十排歌扩展：断语集锦 + 方法论

理论来源：郑民生《十排歌》体系
内容分两层：
  1. 断语集锦：按人生六域（父母/婚姻/子女/事业/牢狱/寿元）
     基于已知郑氏十排歌公开内容的常见断语整理
  2. 方法论：阴阳组合→单柱→十神三层入手推演框架

与 shenshu.py 分工：shenshu = 数量歌诀（词典），shipaige = 断语+方法论（语法书）

置信度：低（公开碎片拼凑，未校订原文）—— 留多处 TODO 待原文确认
"""
from typing import Dict, List, Optional, Tuple

from mangpai.objective.constants import (
    GAN_WX, DI_ZHI,
    WX_KE, WX_SHENG,
    PILLAR_KEYS, PILLAR_NAMES_CN,
)
from mangpai.objective.shenshu import (
    _compute_shishen, _grade, SHENSHU_GE,
    analyze_shenshu,
    JI_SHISHEN, XIONG_SHISHEN, ZHONGXING_SHISHEN,
)

# ══════════════════════════════════════════════════════════════
# 第一层：断语集锦（六大人生领域）
# ⚠️ 置信度：低 — 基于公开碎片整理，待郑氏原文校订
# ══════════════════════════════════════════════════════════════

# ── 1. 父母 ──
# 郑氏理念：印为母，偏印为继母/长辈；财为父，偏财为父缘薄
PARENT_APHORISMS: Dict[str, str] = {
    '印多母众': '正印≥3则母缘多而杂，偏印≥3则继母/养母之象',
    '财多父杂': '偏财≥3主父缘薄或父亲多波折',
    '印被财克': '财星克印，父母关系紧张或有损',
    '年月印星': '年月柱见印星，祖荫深厚',
    '枭神夺食': '偏印克食神，母缘有损或幼年体弱',
    '财印两停': '财印平衡则父母双全且和睦',
    # TODO: 确认「年月官杀混杂」对父母的具体断语
}

# ── 2. 婚姻 ──
# 郑氏理念：男命以财为妻，女命以官为夫
MARRIAGE_APHORISMS: Dict[str, str] = {
    '一财清纯': '男命一财得位，婚姻美满',
    '多财混杂': '男命正偏财混杂≥3，感情不专或多次婚姻',
    '财被合': '财星被合，妻缘被夺或被他人介入',
    '一官清贵': '女命一官清纯，夫贵而专',
    '官杀混杂': '女命官杀≥3，感情纠葛、多次婚姻之象',
    '日坐比劫': '日支为比劫，夫妻关系多竞争摩擦',
    '伤官见官': '女命伤官见正官，婚姻波折、克夫之嫌',
    '日时相冲': '日时柱相冲，晚婚或婚姻不稳定',
    # TODO: 确认「官入墓」「财入墓」对婚姻的具体断语
}

# ── 3. 子女 ──
# 郑氏理念：食伤为子女，男命以官杀为子女（子平传统有别）
CHILDREN_APHORISMS: Dict[str, str] = {
    '食神生旺': '食神生旺有气，子女聪慧有成',
    '伤官过旺': '伤官≥3，子女叛逆或难养',
    '枭神夺食': '偏印克食神，不利子女或流产之象',
    '子女运入墓': '食伤入墓，求子艰难或与子女缘薄',
    '时柱逢空': '时柱落空亡，子女缘浅或远走他乡',
    '官杀为子': '郑氏：男命以官杀为子女，官清则子贵',
    # TODO: 确认「食多伤少」「伤多食少」的子女断语差异
}

# ── 4. 事业 ──
# 郑氏理念：官杀为事业压力，财为事业成果，印为事业支持
CAREER_APHORISMS: Dict[str, str] = {
    '官印相生': '官生印→印护身，仕途顺畅有靠山',
    '食伤生财': '食伤生财→才艺变现，技艺致富之路',
    '财官相生': '财生官→以财求贵，商人从政之象',
    '杀印相生': '七杀有印制，化压力为权威，掌权之命',
    '伤官配印': '伤官有印制，才华有约而不狂，贵格',
    '食神制杀': '食神制七杀，以智胜力，将才之象',
    '财破印': '财星克印，为财损名或因利失节',
    '官杀无制': '官杀混杂无制，事业多变压力大',
    # TODO: 确认「禄神」「羊刃」对事业的具体断语
}

# ── 5. 牢狱 ──
# 郑氏理念：官杀过旺无制、伤官见官、枭神夺食为牢狱信号
PRISON_APHORISMS: Dict[str, str] = {
    '三官是鬼': '正官≥3变为鬼，官非牢狱之象',
    '三杀牢狱': '七杀≥3无制，暴力和牢狱风险',
    '伤官见官': '伤官克官，对抗规则制度，官非口舌',
    '枭神夺食': '偏印克食神+官杀混杂，思维混乱招祸',
    '财杀相生': '财生七杀无制，为财犯法',
    '劫财抗杀': '劫财多而七杀少，以暴制暴反招祸',
    # TODO: 确认「三刑」「自刑」配合十神的牢狱断语
}

# ── 6. 寿元 ──
# 郑氏理念：印为寿，食为福，伤官七杀为损寿信号
LONGEVITY_APHORISMS: Dict[str, str] = {
    '印星为寿': '印星有力不被克，根基稳固寿元长',
    '食神为福': '食神旺而不被夺，福寿绵长',
    '五杀伤残': '七杀≥5，伤残短寿之象',
    '六伤短命': '伤官≥6，短寿之兆',
    '枭神夺食': '偏印夺食，损福折寿',
    '日主无根': '日主无根又无印比生扶，根基浅薄不利寿',
    '墓库重重': '日主入墓或多柱入墓，寿元有碍',
    # TODO: 确认「死绝之地」「胎养之地」的寿元断语
}

SHIPAI_DOMAINS = {
    '父母': PARENT_APHORISMS,
    '婚姻': MARRIAGE_APHORISMS,
    '子女': CHILDREN_APHORISMS,
    '事业': CAREER_APHORISMS,
    '牢狱': PRISON_APHORISMS,
    '寿元': LONGEVITY_APHORISMS,
}

# ══════════════════════════════════════════════════════════════
# 第二层：方法论 — 郑氏三步骤推演框架
# ══════════════════════════════════════════════════════════════

METHODOLOGY = {
    'step1': {
        'name': '阴阳组合',
        'description': '先看天干阴阳搭配，后看地支藏干互动。阳干主动在外，阴干主静在内。',
        'rules': [
            '甲庚冲→改革突破；乙辛冲→细节纠纷',
            '丙壬冲→水火激荡；丁癸冲→暗流涌动',
            '戊己土混杂→厚土埋金或浊水之象',
            '阳干多→外向主动型人格；阴干多→内敛深思型人格',
        ],
    },
    'step2': {
        'name': '单柱',
        'description': '逐柱分析四柱独立结构——每柱天干+地支的组合含义。',
        'rules': [
            '年柱：祖上根基，看天干十神+地支藏干主气',
            '月柱：父母宫+事业提纲，月令五行定全局旺衰基调',
            '日柱：自身+配偶宫，日干为命主，日支为内心+配偶',
            '时柱：子女宫+晚年归宿，时支为最终去向',
            '单柱天干坐绝/死/墓/胎地则该柱对应人事有损',
        ],
    },
    'step3': {
        'name': '十神三层入手',
        'description': '核心推演路径：先分十神 → 再按数量歌诀断吉凶 → 后按六域断语定位人生具体领域。',
        'rules': [
            '四吉（正官/正印/食神/正财）宜扶不宜制',
            '四凶（七杀/伤官/劫财/偏印）宜制不宜扶',
            '中性（比肩/偏财）看数量与位置定吉凶',
            '数量1为「清纯」→ 该十神正面特质凸显',
            '数量2-6为「混杂」→ 该十神负面特质暴露',
            '数量≥7为「成势」→ 顺势而为反而吉利',
            '十神组合优先于单十神判断（如「食神制杀」> 单独看食神或七杀）',
        ],
    },
}

# ══════════════════════════════════════════════════════════════
# 分析函数
# ══════════════════════════════════════════════════════════════


def analyze_shipaige(
    day_gan: str = '',
    day_zhi: str = '',
    year_gan: str = '',
    year_zhi: str = '',
    month_gan: str = '',
    month_zhi: str = '',
    hour_gan: str = '',
    hour_zhi: str = '',
    shenshu_result: Optional[Dict] = None,
) -> Dict:
    """
    郑氏十排歌扩展分析：断语集锦 + 方法论输出。

    先跑 shenshu 获取十神数量统计（如果未预计算），
    再基于十神分布 + 柱位特征匹配六域断语 + 方法论指引。

    Returns:
        {
            'domains': {  # 六域触发断语
                '父母': ['印多母众', ...],
                '婚姻': [...],
                ...
            },
            'methodology_note': '三步骤方法论概要',
            'confidence': 'low',
            'todos': ['待校订项...'],
        }
    """
    # 1. 先获取 shenshu 统计
    if shenshu_result is None:
        shenshu_result = analyze_shenshu(
            day_gan, day_zhi,
            year_gan, year_zhi,
            month_gan, month_zhi,
            hour_gan, hour_zhi,
        )

    counts = shenshu_result.get('counts', {})
    grades = shenshu_result.get('grades', {})

    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    day_wx = GAN_WX.get(day_gan, '')

    # 辅助函数
    def count_ss(name: str) -> int:
        return counts.get(name, {}).get('count', 0)

    def has_ss_pattern(*pairs: Tuple[str, int]) -> bool:
        """检查十神是否达到指定数量阈值。"""
        for ss, min_cnt in pairs:
            if count_ss(ss) < min_cnt:
                return False
        return True

    def zhi_has(gan: str) -> bool:
        """日支本气是否为指定天干。"""
        from mangpai.objective.canggan import CANG_GAN_MANGPAI as cang
        cg = cang.get(day_zhi, [])
        return bool(cg and cg[0][0] == gan)

    def get_ss_for_gan(gan: str) -> str:
        return _compute_shishen(day_gan, gan) if gan else ''

    def day_zhi_shishen() -> str:
        """日支本气天干相对日主的十神。"""
        from mangpai.objective.canggan import CANG_GAN_MANGPAI as cang
        cg = cang.get(day_zhi, [])
        return get_ss_for_gan(cg[0][0]) if cg else ''

    def gans_have(gan: str) -> bool:
        return gan in [year_gan, month_gan, hour_gan]

    # 2. 匹配各域断语
    triggered: Dict[str, List[str]] = {}
    for domain in ['父母', '婚姻', '子女', '事业', '牢狱', '寿元']:
        triggered[domain] = []

    # ── 父母 ──
    if count_ss('正印') >= 3:
        triggered['父母'].append('印多母众')
    if count_ss('偏印') >= 3:
        triggered['父母'].append('印多母众')
    if count_ss('偏财') >= 3:
        triggered['父母'].append('财多父杂')
    if count_ss('正财') >= 2 and count_ss('正印') >= 2:
        triggered['父母'].append('财印两停')
    # 年月柱印星
    for i in [0, 1]:  # 年、月
        ss = get_ss_for_gan(gans[i])
        if ss in ('正印', '偏印'):
            triggered['父母'].append('年月印星')
            break
    # 财克印
    if count_ss('正财') >= 2 and count_ss('正印') >= 1:
        triggered['父母'].append('印被财克')

    # ── 婚姻 ──
    if count_ss('正财') == 1 and count_ss('偏财') == 0:
        triggered['婚姻'].append('一财清纯')
    if count_ss('正财') + count_ss('偏财') >= 3:
        triggered['婚姻'].append('多财混杂')
    if count_ss('正官') == 1 and count_ss('七杀') == 0:
        triggered['婚姻'].append('一官清贵')
    if count_ss('正官') + count_ss('七杀') >= 3:
        triggered['婚姻'].append('官杀混杂')
    # 日坐比劫：日支本气天干对日主为比肩/劫财
    if day_zhi_shishen() in ('比肩', '劫财'):
        triggered['婚姻'].append('日坐比劫')
    # 伤官见官
    if count_ss('伤官') >= 1 and count_ss('正官') >= 1:
        triggered['婚姻'].append('伤官见官')
    # 日时冲
    day_z = zhis[2]
    hour_z = zhis[3]
    if day_z and hour_z:
        chong_pairs = {'子午', '丑未', '寅申', '卯酉', '辰戌', '巳亥'}
        pair = day_z + hour_z
        if pair in chong_pairs or pair[::-1] in chong_pairs:
            triggered['婚姻'].append('日时相冲')

    # ── 子女 ──
    if count_ss('食神') >= 2 or (count_ss('食神') == 1 and '食神' in grades.get('清纯', [])):
        triggered['子女'].append('食神生旺')
    if count_ss('伤官') >= 3:
        triggered['子女'].append('伤官过旺')
    if count_ss('偏印') >= 2 and count_ss('食神') >= 1:
        triggered['子女'].append('枭神夺食')
    # 时柱空亡检查简化
    if count_ss('正官') == 1:
        triggered['子女'].append('官杀为子')

    # ── 事业 ──
    if count_ss('正官') >= 1 and count_ss('正印') >= 1:
        triggered['事业'].append('官印相生')
    if count_ss('食神') >= 1 and count_ss('正财') >= 1:
        triggered['事业'].append('食伤生财')
    if count_ss('正财') >= 1 and count_ss('正官') >= 1:
        triggered['事业'].append('财官相生')
    if count_ss('七杀') >= 1 and count_ss('正印') >= 1:
        triggered['事业'].append('杀印相生')
    if count_ss('伤官') >= 1 and count_ss('正印') >= 1:
        triggered['事业'].append('伤官配印')
    if count_ss('食神') >= 1 and count_ss('七杀') >= 1:
        triggered['事业'].append('食神制杀')
    if count_ss('正财') >= 2 and count_ss('正印') <= 1:
        triggered['事业'].append('财破印')
    if (count_ss('正官') + count_ss('七杀') >= 3
            and count_ss('食神') == 0 and count_ss('伤官') == 0
            and count_ss('正印') == 0 and count_ss('偏印') == 0):
        triggered['事业'].append('官杀无制')

    # ── 牢狱 ──
    if count_ss('正官') >= 3:
        triggered['牢狱'].append('三官是鬼')
    if count_ss('七杀') >= 3:
        triggered['牢狱'].append('三杀牢狱')
    if count_ss('伤官') >= 1 and count_ss('正官') >= 1:
        triggered['牢狱'].append('伤官见官')
    if count_ss('偏印') >= 2 and count_ss('食神') >= 1:
        triggered['牢狱'].append('枭神夺食')
    if count_ss('正财') >= 2 and count_ss('七杀') >= 2:
        triggered['牢狱'].append('财杀相生')
    if count_ss('劫财') >= 2 and count_ss('七杀') >= 1:
        triggered['牢狱'].append('劫财抗杀')

    # ── 寿元 ──
    if count_ss('正印') >= 1:
        triggered['寿元'].append('印星为寿')
    if count_ss('食神') >= 2:
        triggered['寿元'].append('食神为福')
    if count_ss('七杀') >= 5:
        triggered['寿元'].append('五杀伤残')
    if count_ss('伤官') >= 6:
        triggered['寿元'].append('六伤短命')
    if count_ss('偏印') >= 2 and count_ss('食神') >= 1:
        triggered['寿元'].append('枭神夺食')
    # 日主无根
    if count_ss('比肩') == 0 and count_ss('劫财') == 0 and count_ss('正印') == 0 and count_ss('偏印') == 0:
        triggered['寿元'].append('日主无根')

    # 3. 方法论指引
    methodology_note = (
        f"郑氏三步骤：①阴阳组合→{day_gan}{day_zhi}日主（"
        f"{'阳' if day_gan in '甲丙戊庚壬' else '阴'}干），"
        f"四柱{'阳多主动' if sum(1 for g in gans if g in '甲丙戊庚壬') >= 2 else '阴多主静'}；"
        f"②单柱→年月日时逐柱分析；"
        f"③十神三层→数量歌诀(见shenshu)→六域断语(见本模块)"
    )

    # 4. TODO 列表
    todos = [
        '父母：确认「年月官杀混杂」的郑氏原文断语',
        '婚姻：确认「财入墓」「官入墓」的郑氏原文断语',
        '子女：确认「食多伤少」「伤多食少」的郑氏差异断语',
        '事业：确认「禄神」「羊刃」配合十神的郑氏原文断语',
        '牢狱：确认「三刑」「自刑」配合十神的郑氏原文断语',
        '寿元：确认「死绝之地」「胎养之地」的郑氏原文断语',
        '全局：六域断语表待郑氏原文全文校订后提升置信度',
    ]

    triggered_any = any(v for v in triggered.values())

    return {
        'domains': {k: v for k, v in triggered.items() if v} if triggered_any else {'无触发': []},
        'methodology_note': methodology_note,
        'confidence': 'low',
        'todos': todos,
        'shenshu_summary': shenshu_result.get('summary', ''),
    }


def format_shipaige_report(shipaige_result: Dict) -> str:
    """将 shipaige 分析结果格式化为可读文本。"""
    lines = []
    lines.append('【郑氏十排歌扩展分析】')
    lines.append(f'置信度：{shipaige_result.get("confidence", "low").upper()}')
    lines.append('')

    domains = shipaige_result.get('domains', {})
    domain_names = ['父母', '婚姻', '子女', '事业', '牢狱', '寿元']
    for dn in domain_names:
        triggered = domains.get(dn, [])
        if triggered:
            lines.append(f'── {dn} ──')
            for key in triggered:
                aph_map = SHIPAI_DOMAINS.get(dn, {})
                desc = aph_map.get(key, key)
                lines.append(f'  ● {key}：{desc}')
            lines.append('')

    lines.append('── 方法论指引 ──')
    lines.append(shipaige_result.get('methodology_note', ''))

    lines.append('')
    lines.append('── 待校订项 ──')
    for i, todo in enumerate(shipaige_result.get('todos', []), 1):
        lines.append(f'  {i}. {todo}')

    return '\n'.join(lines)
