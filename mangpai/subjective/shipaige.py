"""
shipaige — 郑民生十排歌扩展：断语集锦 + 方法论

理论来源：郑民生《十排歌》公开碎片（mangpai/docs/zhengminsheng-shipaige-fragments.md，
          下称「碎片:行号」）。段氏五书 grep「一财是财/十排歌」零命中，对照源仅此。

与 shenshu.py 分工：shenshu = 数量歌诀（词典），shipaige = 断语+方法论（语法书）

⚠️ F1 批（2026-08-17）补注（批8 审计定）：断语层不可作书证；唯数量诀层
  （shenshu）与碎片逐字吻合可用。

F18 批（2026-08-17）断语层重写（批8 审计 P0×3 + P1：旧六域断语多为泛子平
常识冠名「郑氏」，与碎片 39 条几乎零对应）——逐域按碎片原文重写，仅收录
可机械检测者，未实现条目列入 todos：
  - P0-1「官杀为子」冠名错误 → 碎片:81「身旺财为子，身弱印作儿」
  - P0-2「劫财抗杀入牢狱」冠名冲突 → 碎片:90「劫财七杀两相连，要到边疆
    去从军」（归事业域）
  - P0-3「食神生旺子女聪慧」与自身数量诀「二食贪吃/三食愚钝」矛盾 → 废，
    子女域按碎片重建

置信度：低（公开碎片拼凑，未校订原文）—— 断语层不可作书证
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, DI_ZHI, WX_KE_ME,
)
from mangpai.objective.canggan import CANG_GAN_MANGPAI
from mangpai.objective.shenshu import (
    _compute_shishen,
    analyze_shenshu,
)

# ══════════════════════════════════════════════════════════════
# 关系/神煞基础表（检测辅助）
# ══════════════════════════════════════════════════════════════

_CHONG = {frozenset(p) for p in ('子午', '丑未', '寅申', '卯酉', '辰戌', '巳亥')}
_CHUAN = {frozenset(p) for p in ('子未', '丑午', '寅巳', '卯辰', '申亥', '酉戌')}
_XING = {frozenset(p) for p in
         ('丑戌', '戌未', '丑未', '寅巳', '巳申', '寅申', '子卯')}
_LU = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
       '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
_TOMB = {'木': '未', '火': '戌', '金': '丑', '水': '辰', '土': '辰'}
# 沐浴位（阴阳同生同死 + 火土同宫，盲派口径）
_MUYU = {'木': '子', '火': '卯', '土': '卯', '金': '午', '水': '酉'}

# ══════════════════════════════════════════════════════════════
# 第一层：断语集锦（六大人生领域）—— 逐条=碎片原文
# ══════════════════════════════════════════════════════════════

# ── 1. 父母 ──
PARENT_APHORISMS: Dict[str, str] = {
    '印在年月被财坏': '印在年月被财坏，命与父无缘（必须过继）［碎片:62］',
    '伏吟不见祖': '年日、年时伏吟不见祖，5岁前祖上少一人［碎片:64］',
    '母明父暗是偷生': '母明父暗是偷生（私生子）［碎片:66］',
}

# ── 2. 婚姻 ──
MARRIAGE_APHORISMS: Dict[str, str] = {
    '日坐墓库喜刑冲': '日坐墓库喜刑冲，冲开墓库得贤妻［碎片:72］',
    '劫财穿配偶宫必离': '劫财穿配偶宫，一定离婚［碎片:74］',
    '婚姻宫入墓难成家': '婚姻宫入墓，难成家［碎片:77］',
    '一字重现数为双': '一字重现数为双，双婚双姓双上详［碎片:78/133］',
}

# ── 3. 子女 ──
CHILDREN_APHORISMS: Dict[str, str] = {
    '身旺财为子身弱印作儿': '身旺财为子，身弱印作儿［碎片:81］',
    '命旺无财生女': '命旺无财，光生女孩没有男孩［碎片:82］',
    '双女双鱼占日支': '双女双鱼占日支，命中定有四个女（巳为双女，亥为双鱼）［碎片:84］',
    '三辰假子女': '辰月辰日与辰时，假子假女送进坟［碎片:85］',
}

# ── 4. 事业（含从军/武职、职业）──
CAREER_APHORISMS: Dict[str, str] = {
    '禄神入杀库': '禄神入杀库，人定进兵营［碎片:88］',
    '劫财七杀两相连': '劫财七杀两相连，要到边疆去从军［碎片:90］',
    '阳火克阴金': '阳火克阴金，定然去充军［碎片:91］',
    '戊坐戌见酉做老师': '戊坐戌见酉做老师（戊戌日柱见酉）［碎片:94］',
    '己临巳酉是郎中': '己临巳酉是郎中（医生）［碎片:95］',
    '辛丙合做酒店': '辛遇丙合做酒店，官星化食发大财［碎片:96］',
    '伤官生财格': '伤官生财格，伤官旺财有根才主富［碎片:97］',
    '无财禄当财': '原局无财，禄可当财［碎片:99］',
}

# ── 5. 牢狱/凶灾 ──
PRISON_APHORISMS: Dict[str, str] = {
    '日时两连见四角': '命中见四角（日时两支连着），十人八人易有牢狱［碎片:102］',
    '劫财伤官遇穿官': '劫财伤官拉帮结派，遇到穿官有死刑［碎片:103］',
    '用印见财有官灾': '用印若见财，必定有官灾［碎片:106］',
    '五鬼凶神': '五鬼最凶神：戌巳、辰亥、寅未［碎片:108］',
}

# ── 6. 寿元 ──
LONGEVITY_APHORISMS: Dict[str, str] = {
    '三枭夺财短命': '三枭无比，夺财制财短命［碎片:112］',
    '食伤被制短命': '食伤被制短命［碎片:112］',
    '邀合入墓皆凶': '乙见庚戌入鬼门，辛遇丙辰祸缠身（邀合入墓皆凶）［碎片:113］',
    '丁见丙寅命早没': '丁见丙寅命早没（阳生阴死）［碎片:114］',
    '沐浴水灾': '沐浴为水灾，沐浴加干杀，死于水中［碎片:115］',
}

# 六域→断语表映射。修批C 注：唯一消费者 format_shipaige_report 系死函数
# （全库零调用，R2 死数据清单）已删；本表与六域断语表现存为碎片原文档案
# （F18 逐条=碎片原文+行号），analyze_shipaige 触发键为内联检测不读本表。
SHIPAI_DOMAINS = {
    '父母': PARENT_APHORISMS,
    '婚姻': MARRIAGE_APHORISMS,
    '子女': CHILDREN_APHORISMS,
    '事业': CAREER_APHORISMS,
    '牢狱': PRISON_APHORISMS,
    '寿元': LONGEVITY_APHORISMS,
}

# ══════════════════════════════════════════════════════════════
# 第二层：方法论 — 郑公方法论要点（碎片§四）
# ══════════════════════════════════════════════════════════════

METHODOLOGY = {
    'step1': {
        'name': '阴阳组合',
        'description': '先看阴阳组合，再看单柱结构，再看十神含义［碎片:141］。',
        'rules': [
            '主抓象意结构，先懂刑冲克合害墓暗合破绝［碎片:142］',
            '天干为外形地支为实质；天干为外因地支为内因［碎片:147］',
        ],
    },
    'step2': {
        'name': '单柱',
        'description': '逐柱分析四柱独立结构——每柱天干+地支的组合含义。',
        'rules': [
            '墓也是一种方法，冲制也是［碎片:146］',
            '虚干怕合，合去合走应期［碎片:148］',
        ],
    },
    'step3': {
        'name': '十神三层入手',
        'description': '先分十神 → 再按数量歌诀断吉凶 → 后按六域断语定位人生领域。',
        'rules': [
            '四吉（正官/正印/食神/正财）宜扶不宜制［碎片:143］',
            '四凶（七杀/伤官/劫财/偏印）宜制不宜扶［碎片:143］',
            '比肩与偏财看成中性［碎片:144］',
            '禄合/日干合/日支合/食伤合/比肩合 → 自己去做什么去得到什么［碎片:145］',
            '数量1清纯、2-6混杂为病、≥7成势从格反吉（见 shenshu 数量诀）',
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
    郑氏十排歌扩展分析：断语集锦（碎片原文） + 方法论输出。

    先跑 shenshu 获取十神数量统计（如果未预计算），
    再按碎片断语做机械检测（可检测者），未实现条目列入 todos。

    Returns:
        {
            'domains': {六域: [触发的碎片断语键, ...]},
            'methodology_note': '方法论概要',
            'confidence': 'low',
            'todos': ['未实现碎片条目...'],
            'shenshu_summary': str,
        }
    """
    if shenshu_result is None:
        shenshu_result = analyze_shenshu(
            day_gan, day_zhi,
            year_gan, year_zhi,
            month_gan, month_zhi,
            hour_gan, hour_zhi,
        )

    counts = shenshu_result.get('counts', {})

    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    day_wx = GAN_WX.get(day_gan, '')

    def count_ss(name: str) -> int:
        return counts.get(name, {}).get('count', 0)

    def gan_ss(g: str) -> str:
        return _compute_shishen(day_gan, g) if g else ''

    def zhi_ss(z: str) -> str:
        """地支本气相对日主的十神。"""
        cg = CANG_GAN_MANGPAI.get(z, [])
        return gan_ss(cg[0][0]) if cg else ''

    def pillar_has(i: int, names) -> bool:
        return gan_ss(gans[i]) in names or zhi_ss(zhis[i]) in names

    def pair_in(a: str, b: str, rels) -> bool:
        return bool(a and b) and frozenset((a, b)) in rels

    other_zhis = [z for z in (year_zhi, month_zhi, hour_zhi) if z]
    zhi_set = set(z for z in zhis if z)
    gan_cai = any(gan_ss(g) in ('正财', '偏财') for g in gans if g)
    gan_yin = any(gan_ss(g) in ('正印', '偏印') for g in gans if g)
    cai_cnt = count_ss('正财') + count_ss('偏财')
    yin_cnt = count_ss('正印') + count_ss('偏印')
    # 身强弱简化代理（本模块不接 yongshen）：比劫印 vs 财官食伤 数量比
    self_side = count_ss('比肩') + count_ss('劫财') + yin_cnt
    other_side = (cai_cnt + count_ss('正官') + count_ss('七杀')
                  + count_ss('食神') + count_ss('伤官'))
    shen_qiang = self_side >= other_side

    triggered: Dict[str, List[str]] = {
        d: [] for d in ('父母', '婚姻', '子女', '事业', '牢狱', '寿元')}

    # ── 父母 ──
    # 碎片:62（天干共存即计「坏」——简化，无克夺动作检测）
    if (any(gan_ss(gans[i]) in ('正印', '偏印') for i in (0, 1))
            and gan_cai):
        triggered['父母'].append('印在年月被财坏')
    # 碎片:64
    if ((year_gan and year_gan == day_gan and year_zhi == day_zhi)
            or (year_gan and year_gan == hour_gan and year_zhi == hour_zhi)):
        triggered['父母'].append('伏吟不见祖')
    # 碎片:66（印透干 + 财不透干而地支本气有财）
    if (gan_yin and not gan_cai
            and any(zhi_ss(z) in ('正财', '偏财') for z in zhis if z)):
        triggered['父母'].append('母明父暗是偷生')

    # ── 婚姻 ──
    # 碎片:72
    if (day_zhi in '辰戌丑未'
            and any(pair_in(day_zhi, z, _CHONG | _XING) for z in other_zhis)):
        triggered['婚姻'].append('日坐墓库喜刑冲')
    # 碎片:74
    for i in (0, 1, 3):
        if pair_in(day_zhi, zhis[i], _CHUAN) and pillar_has(i, ('劫财',)):
            triggered['婚姻'].append('劫财穿配偶宫必离')
            break
    # 碎片:77（日支五行之墓在局）
    tomb = _TOMB.get(ZHI_WX.get(day_zhi, ''), '')
    if tomb and tomb in other_zhis:
        triggered['婚姻'].append('婚姻宫入墓难成家')
    # 碎片:78/133
    zlist = [z for z in zhis if z]
    if len(zlist) != len(set(zlist)):
        triggered['婚姻'].append('一字重现数为双')

    # ── 子女 ──
    # 碎片:81（身强弱为简化代理）
    if (shen_qiang and cai_cnt >= 1) or (not shen_qiang and yin_cnt >= 1):
        triggered['子女'].append('身旺财为子身弱印作儿')
    # 碎片:82
    if shen_qiang and cai_cnt == 0:
        triggered['子女'].append('命旺无财生女')
    # 碎片:84
    if day_zhi in ('巳', '亥'):
        triggered['子女'].append('双女双鱼占日支')
    # 碎片:85
    if month_zhi == day_zhi == hour_zhi == '辰':
        triggered['子女'].append('三辰假子女')

    # ── 事业 ──
    lu = _LU.get(day_gan, '')
    sha_wx = WX_KE_ME.get(day_wx, '')
    # 碎片:88（日主禄在局，且禄支所入之墓=七杀五行之库）
    if lu and lu in zhis:
        lu_tomb = _TOMB.get(ZHI_WX.get(lu, ''), '')
        if lu_tomb and lu_tomb == _TOMB.get(sha_wx) and lu_tomb in zhis:
            triggered['事业'].append('禄神入杀库')
    # 碎片:90（相邻柱一柱劫财、一柱七杀）
    for i in range(3):
        if ((pillar_has(i, ('劫财',)) and pillar_has(i + 1, ('七杀',)))
                or (pillar_has(i, ('七杀',)) and pillar_has(i + 1, ('劫财',)))):
            triggered['事业'].append('劫财七杀两相连')
            break
    # 碎片:91（共存即计——简化无动作检测）
    if (('丙' in gans or {'巳', '午'} & zhi_set)
            and ('辛' in gans or '酉' in zhi_set)):
        triggered['事业'].append('阳火克阴金')
    # 碎片:94
    if day_gan == '戊' and day_zhi == '戌' and '酉' in zhi_set:
        triggered['事业'].append('戊坐戌见酉做老师')
    # 碎片:95
    if day_gan == '己' and {'巳', '酉'} & zhi_set:
        triggered['事业'].append('己临巳酉是郎中')
    # 碎片:96
    if '辛' in gans and '丙' in gans:
        triggered['事业'].append('辛丙合做酒店')
    # 碎片:97（伤官明现 + 财有根=支本气财）
    if (count_ss('伤官') >= 1
            and any(zhi_ss(z) in ('正财', '偏财') for z in zhis if z)):
        triggered['事业'].append('伤官生财格')
    # 碎片:99
    if cai_cnt == 0 and lu and lu in zhis:
        triggered['事业'].append('无财禄当财')

    # ── 牢狱 ──
    # 碎片:102（日时两支相同或相邻=「连着」）
    if day_zhi and hour_zhi:
        d_i, h_i = DI_ZHI.index(day_zhi), DI_ZHI.index(hour_zhi)
        if (d_i - h_i) % 12 in (0, 1, 11):
            triggered['牢狱'].append('日时两连见四角')
    # 碎片:103
    has_chuan = any(pair_in(zhis[i], zhis[j], _CHUAN)
                    for i in range(4) for j in range(i + 1, 4))
    if (count_ss('劫财') >= 1 and count_ss('伤官') >= 1
            and count_ss('正官') >= 1 and has_chuan):
        triggered['牢狱'].append('劫财伤官遇穿官')
    # 碎片:106（「用印」=印透干之简化代理）
    if gan_yin and gan_cai:
        triggered['牢狱'].append('用印见财有官灾')
    # 碎片:108
    if any(pair <= zhi_set for pair in
           ({'戌', '巳'}, {'辰', '亥'}, {'寅', '未'})):
        triggered['牢狱'].append('五鬼凶神')

    # ── 寿元 ──
    # 碎片:112a
    if count_ss('偏印') >= 3 and count_ss('比肩') == 0:
        triggered['寿元'].append('三枭夺财短命')
    # 碎片:112b（食伤柱本气支逢冲/穿/刑）
    for i in range(4):
        if pillar_has(i, ('食神', '伤官')) and any(
                pair_in(zhis[i], zhis[j], _CHONG | _CHUAN | _XING)
                for j in range(4) if j != i):
            triggered['寿元'].append('食伤被制短命')
            break
    # 碎片:113
    if (('乙' in gans and '庚' in gans and '戌' in zhi_set)
            or ('辛' in gans and '丙' in gans and '辰' in zhi_set)):
        triggered['寿元'].append('邀合入墓皆凶')
    # 碎片:114
    if '丁' in gans and '寅' in zhi_set:
        triggered['寿元'].append('丁见丙寅命早没')
    # 碎片:115
    muyu = _MUYU.get(day_wx, '')
    if muyu and muyu in zhi_set:
        triggered['寿元'].append('沐浴水灾')

    # 方法论指引（碎片§四.1）
    methodology_note = (
        f"郑氏三步骤［碎片:141］：①阴阳组合→{day_gan}{day_zhi}日主"
        f"（{'阳' if day_gan in '甲丙戊庚壬' else '阴'}干）；"
        f"②单柱结构；③十神含义→数量歌诀(见shenshu)→六域断语(见本模块)"
    )

    # 未实现碎片条目（性别/空亡/神煞/运岁/年龄段未接入本模块）
    todos = [
        '父母：印星不能临寡/父星不能临孤（孤辰寡宿未接入）；比劫旺相印空亡父死母再嫁（空亡未接入）；月财合年支犯穿两姓占［碎片:61/63/65］',
        '婚姻：男命婚姻宫见杀为妻/女命比肩太多主风流/女命月令杀印同一根/日干临养地（性别/长生未接入）；年运来闭库不破大财就婚灾（运岁未接入）［碎片:69-76］',
        '子女：女命财星穿破难生儿/伤官空亡只生女（性别/空亡未接入）［碎片:83］',
        '事业：阳火旺盛要水济走到水地去从军（运岁未接入）；劫财为用神可做风险生意（用神未接入）［碎片:89/98］',
        '牢狱：食伤走墓运/酉金走子运沉体（运岁未接入）；亡神劫煞在时上合克年命（神煞未接入）［碎片:104/107/105］',
        '寿元：年纪大看财/小看印枭/中看食伤（年龄段未接入）［碎片:111］',
        '全局：断语层置信度低、不可作书证，待郑氏原文全文校订',
    ]

    triggered_any = any(v for v in triggered.values())

    return {
        'domains': {k: v for k, v in triggered.items() if v} if triggered_any else {'无触发': []},
        'methodology_note': methodology_note,
        'confidence': 'low',
        'todos': todos,
        'shenshu_summary': shenshu_result.get('summary', ''),
    }
