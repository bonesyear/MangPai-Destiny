"""
body_parts - 盲派干支身体部位映射·客观层（objective）·纯数据查表

理论来源：
  段建业《盲派命理高级内容篇》ch11.2「疾病健康」干/支身体主表（OCR 15305-15391）
  与 ch4 十干/十二支类象「人体」条（OCR 3960-4940）、《盲派中级命理学》类象章。
核心分层（ch11 明义）：
  - 十天干主**外**表、显露之部位与功能（GAN_BODY）；
  - 十二地支主**内**在、深层之器官与系统（ZHI_BODY）；
  - 宫位身段主表取高级 4.5/中级共识（年腿足、时头面门户），
    ch11 宫位分野变体另存 PILLAR_BODY_CH11 备查。

与既有模块关系（F1 批 2026-08-17 更正，原「唯一事实源」名不副实）：
  - 本模块数据经逐项对书可信，但**未接线**：engine/subjective 零生产消费
    （仅 __init__ re-export + 测试引用）。实际服役旧表 = gongshen.py
    _PILLAR_BODY（年/时颠倒备案）与 zaihuo.py 自带四表。接线或收口决策
    留后续批次，本批仅去冠名。
  - xiangfa.py 的 'body' 字段为速记简版，保持不动、不回写、不互相 import
    （避免 objective 内部横向耦合）。
  - zaihuo.py 疾病表（_HAI_DISEASE/_XING_DISEASE/_WX_ORGAN）与本表同构，
    后续立项收口 import；本期不改 zaihuo。
  - 已知存疑：gongshen._PILLAR_BODY 年/时柱身段与书中三处主表颠倒
    （书：年=腿足、时=头面；码：年=头颈、时=腿足），另立 bug 单，不在本层迁就。
置信度：高（主表直录原书；扩展层并录 ch4+中级类象，分键不合并）。
"""
from typing import Dict, List

from mangpai.objective.constants import DI_ZHI, GAN_WX, PILLAR_KEYS

__all__ = [
    'GAN_BODY', 'ZHI_BODY', 'GAN_BODY_EXT', 'ZHI_BODY_EXT',
    'PILLAR_BODY', 'PILLAR_BODY_CH11', 'SHISHEN_BODY',
    'YINYANG_BINGJI', 'WX_BINGJI', 'HAI_DISEASE', 'PO_DISEASE', 'XING_DISEASE',
    'GAN_BODY_VERSE', 'ZHI_BODY_VERSE', 'PILLAR_BODY_VERSE', 'BINGJI_VERSE',
    'get_gan_body', 'get_zhi_body', 'get_pillar_body', 'get_shishen_body',
    'get_disease_by_hai', 'get_disease_by_po', 'get_disease_by_xing',
]

# ── 古传口诀原文（ch11 引「古传」，OCR 15305-15312）──
GAN_BODY_VERSE = (
    '甲头乙项丙肩求，丁心戊胃己脾乡。'
    '庚是脐轮辛属股，壬胫癸足一身由。'
    '三焦亦向壬中寄，包络同归入癸方。'
)
ZHI_BODY_VERSE = (
    '子属膀胱水道耳，丑为胞肚及脾乡。'
    '寅胆发脉并两手，卯本十指内肝方。'
    '辰土为皮肩胸类，巳面齿咽下脘肛。'
    '午火精神司眼目，未土胃脘膈脊梁。'
    '申金大肠经络肺，酉中精血小肠藏。'
    '戌土命门腿还足，亥水为头及肾要。'
)
# 宫位身段口诀五（高级 4.5，OCR 5906-5907）；
# 终南真诀再确认：「宫位年腿月胸腹，日腑时窍生殖专」（OCR 15751）
PILLAR_BODY_VERSE = '年柱腿足四肢伤，月令脊背肩腰扛。日支五脏六腑地，时上门户头面详。'
# 五行病机口诀三（OCR 15552-15556）
BINGJI_VERSE = (
    '阳亢阴弱高血压，阴盛阳衰寒湿痹。'
    '木不受水生肝郁，火旺克金血病危。'
    '土来浊水糖尿病，金寒水冷肺气萎。'
)

# ── 天干身体部位主表（ch11 主表：干主外，OCR 15320-15344）──
GAN_BODY: Dict[str, List[str]] = {
    '甲': ['头', '胆'],
    '乙': ['颈', '肝', '毛发', '眉'],
    '丙': ['肩', '小肠', '面'],
    '丁': ['心', '眼', '血液', '神经'],
    '戊': ['胃', '肋胁', '鼻'],
    '己': ['脾', '腹', '皮肤', '唇'],
    '庚': ['大肠', '脐'],
    '辛': ['肺', '股', '齿'],
    '壬': ['膀胱', '胫', '口'],
    '癸': ['肾', '足', '精', '眼', '耳'],
}

# ── 天干扩展层（高级 ch4 类象 + 中级类象并录，象法细节用）──
# 中级特注：丙配癸才算是眼睛（丙为眼框、癸为黑眼珠）[中级 1480-1483]；
#           己为身体（女性则曲线）[中级 1484]。
GAN_BODY_EXT: Dict[str, List[str]] = {
    '甲': ['头面', '肝胆', '神经', '头发', '眉', '臂', '肢体', '经脉'],
    '乙': ['脊柱', '手腕', '脚腕', '胆', '头发', '经脉'],
    '丙': ['眼睛', '神经', '大脑', '血压', '小肠', '肩'],
    '丁': ['心脏', '眼睛', '血管', '神经'],
    '戊': ['胃', '皮肤', '鼻', '肌肉'],
    '己': ['脾', '腹', '皮肤', '胰腺', '身体'],
    '庚': ['大肠', '骨骼', '骨钙', '肺', '牙齿', '嗓音', '脐'],
    '辛': ['肺', '呼吸道', '喉咙', '鼻腔', '耳朵', '筋骨', '小骨骼'],
    '壬': ['口', '膀胱', '血液', '循环系统'],
    '癸': ['肾脏', '眼睛', '精血', '骨髓', '脑', '精液', '经血', '津液'],
}

# ── 地支身体部位主表（ch11 主表：支主内，OCR 15346-15377）──
ZHI_BODY: Dict[str, List[str]] = {
    '子': ['膀胱', '肾', '耳', '腰', '血液', '泌尿'],
    '丑': ['肚腹', '脾', '肌肉', '生殖器', '妇科', '肛门'],
    '寅': ['胆', '脉', '手', '头', '毛发'],
    '卯': ['肝', '十指', '筋', '管道', '血管', '腰', '肠', '关节'],
    '辰': ['肩胸', '皮肤', '膀胱', '胰', '淋巴', '前列腺'],
    '巳': ['面', '齿', '咽喉', '神经'],
    '午': ['心', '眼', '精神', '小肠', '血压', '神经'],
    '未': ['胃', '腹', '脊梁', '脾', '饮食', '力'],
    '申': ['大肠', '经络', '肺', '筋骨', '声'],
    '酉': ['肺', '鼻', '皮毛', '精血', '耳'],
    '戌': ['命门', '腿足', '心包', '胃', '神经'],
    '亥': ['头', '肾', '阴茎', '髓', '精', '血', '寒湿'],
}

# ── 地支扩展层（高级 ch4「人体」+ 中级类象并录）──
ZHI_BODY_EXT: Dict[str, List[str]] = {
    '子': ['肾', '耳', '膀胱', '泌尿', '血液', '精', '腰', '喉咙'],
    '丑': ['腹', '脾胃', '肾', '子宫', '肌肉', '肿块'],
    '寅': ['头', '手', '肢体', '肝胆', '毛发', '指甲', '掌', '经络', '脉', '筋', '神经'],
    '卯': ['肝胆', '四肢', '手臂', '手指', '腰', '筋', '毛发'],
    '辰': ['膀胱', '内分泌', '肌肤', '肩', '胸', '腹', '胃', '肋'],
    '巳': ['心脏', '三焦', '咽喉', '面', '齿', '眼目', '神经', '小肠', '肛门'],
    '午': ['心', '小肠', '眼', '舌', '血液', '神经', '精力'],
    '未': ['脾胃', '腕', '腹', '口腔', '肌肤', '脊梁'],
    '申': ['肺', '大肠', '骨', '脊椎', '气管', '食道', '牙齿', '骨钙', '经络'],
    '酉': ['肺', '肋', '小肠', '耳朵', '牙齿', '骨骼', '臂膀', '精血'],
    '戌': ['心', '心包', '命门', '背', '胃', '鼻', '肌肉', '腿', '踝足'],
    '亥': ['头', '肾', '膀胱', '尿道', '血脉', '经血'],
}

# ── 宫位（柱位）身段主表（高级 4.5 [OCR 5889-5913] 与中级 [1668-1672] 共识）──
# 年柱离日主最远主腿足四肢；时柱为沟通门户主头面五官/生殖排泄。
PILLAR_BODY: Dict[str, List[str]] = {
    'year': ['腿', '足', '四肢'],
    'month': ['脊', '背', '肩', '腰', '躯干', '上肢'],
    'day': ['五脏', '六腑', '胸', '心', '脑', '髓'],
    'hour': ['头', '面', '眼', '耳', '鼻', '口', '手', '生殖器', '排泄器官'],
}

# ── 宫位身段 ch11 变体（ch11.2「宫位分野」[OCR 15379-15391]，唯一给年柱头面的版本）──
PILLAR_BODY_CH11: Dict[str, List[str]] = {
    'year': ['头面', '腿脚', '遗传系统'],
    'month': ['胸背', '脊柱', '上肢', '肢体'],
    'day': ['心腹', '五脏六腑', '里症', '骨髓神经'],
    'hour': ['门户', '耳鼻口五官', '手', '生殖泌尿系统'],
}

# ── 十神身体表（中级十神总表「身体」行 [中级 1985-2080] + 禄刃条）──
# 键为十神类别；get_shishen_body 负责 正印/偏印→印 等归并。
# 禄刃：高级 11.4 沿用「禄刃代表肉身，禄刃受伤=身体摧毁、死亡标志」[OCR 16218-16224]。
SHISHEN_BODY: Dict[str, List[str]] = {
    '印': ['毛发', '皮肤'],
    '财': ['精血', '呼吸'],
    '官杀': ['外伤', '疾病', '神经'],
    '比劫': ['手足', '四肢'],
    '食伤': ['口', '舌', '窍'],
    '禄': ['身体', '肢体', '寿命'],
    '羊刃': ['四肢', '身体'],
}

_SHISHEN_GROUP: Dict[str, str] = {
    '正印': '印', '偏印': '印',
    '正财': '财', '偏财': '财',
    '正官': '官杀', '七杀': '官杀',
    '比肩': '比劫', '劫财': '比劫',
    '食神': '食伤', '伤官': '食伤',
    '禄': '禄', '禄神': '禄', '羊刃': '羊刃',
}

# ── 阴阳三态病机（ch11.2，OCR 15549-15573）──
YINYANG_BINGJI: Dict[str, Dict] = {
    '阴阳离决': {
        'condition': '纯阴纯阳、干支隔绝',
        'diseases': ['大凶', '重病', '夭折'],
    },
    '阳亢阴弱': {
        'condition': '阳火过亢、阴水衰微（如丙日见甲寅、甲日丙火旺透）',
        'diseases': ['高血压', '头晕', '心脏病'],
    },
    '阴盛阳衰': {
        'condition': '金水湿土过旺、火土衰微',
        'diseases': ['寒湿症', '肾病', '抑郁症', '气血亏虚'],
    },
}

# ── 五行病机七具名组合（ch11.2，OCR 15613-15623）──
# condition 为文字条件，判定逻辑留 subjective（zaihuo 等）消费。
WX_BINGJI: Dict[str, Dict] = {
    '寅亥合': {
        'condition': '寅亥合，水湿伤肝、疏泄不力',
        'organs': ['肝', '心'],
        'diseases': ['风湿', '血脂高', '血压高', '心脏病'],
        'note': '水湿化痰重则怪病、精神病',
    },
    '丑辰合金': {
        'condition': '丑辰湿土壅金',
        'organs': ['肺'],
        'diseases': ['肺壅', '哮喘', '咳嗽'],
    },
    '火克金': {
        'condition': '丙丁火旺克辛酉金',
        'organs': ['血', '骨', '骨髓'],
        'diseases': ['血病', '白血病'],
        'note': '金水相连才主肺病；金水未连主骨/骨髓（OCR 15634）',
    },
    '木多火塞': {
        'condition': '乙多丁弱，木多火塞',
        'organs': ['肝', '心', '神经'],
        'diseases': ['肝郁化火', '心神经伤'],
    },
    '土多金埋': {
        'condition': '戊己厚土、庚辛弱金',
        'organs': ['肺', '呼吸道'],
        'diseases': ['肺疾', '呼吸道病'],
    },
    '水多木漂': {
        'condition': '壬癸旺水、甲乙虚木',
        'organs': ['肝胆', '肾'],
        'diseases': ['肝胆病', '风湿', '肾虚'],
    },
    '金多水浊': {
        'condition': '庚辛旺金、壬癸弱水',
        'organs': ['肾', '泌尿'],
        'diseases': ['肾亏', '泌尿病'],
    },
}

# ── 六穿（害）主病（ch11.2，OCR 15402-15413）──
HAI_DISEASE: Dict[frozenset, List[str]] = {
    frozenset({'子', '未'}): ['脾胃', '腹疾'],
    frozenset({'丑', '午'}): ['心脏', '心慌惊悸', '妇科', '肾疾'],
    frozenset({'寅', '巳'}): ['胆', '神经', '面齿'],
    frozenset({'卯', '辰'}): ['肝腹', '腰肠'],
    frozenset({'申', '亥'}): ['胫足', '肾阴'],
    frozenset({'酉', '戌'}): ['肺', '眼', '心包', '神经'],
}

# ── 破主病（书中明文仅子卯、卯午两组，OCR 15462-15470）──
# 注：子卯书亦言「子卯刑亦作破」（OCR 15523），故子卯同见 XING_DISEASE。
PO_DISEASE: Dict[frozenset, List[str]] = {
    frozenset({'子', '卯'}): ['肾气虚', '泌尿系统病', '肝气郁结'],
    frozenset({'卯', '午'}): ['血管破裂', '心脏出血', '心梗', '脑溢血'],
}

# ── 三刑主病（ch11.2，OCR 15514-15523）──
XING_DISEASE: Dict[frozenset, List[str]] = {
    frozenset({'寅', '巳', '申'}): ['神经', '肝胆', '筋骨之疾', '官非'],
    frozenset({'丑', '未', '戌'}): ['脾胃', '皮肤', '肌肉之疾', '顽疾难愈'],
    frozenset({'子', '卯'}): ['肝肾', '泌尿', '生殖之疾'],
}


# ── 查表函数（纯查表，无判断）──

def get_gan_body(gan: str, ext: bool = False) -> List[str]:
    """天干身体部位。ext=True 取 ch4+中级类象扩展层。"""
    table = GAN_BODY_EXT if ext else GAN_BODY
    return list(table.get(gan, []))


def get_zhi_body(zhi: str, ext: bool = False) -> List[str]:
    """地支身体部位。ext=True 取 ch4+中级类象扩展层。"""
    table = ZHI_BODY_EXT if ext else ZHI_BODY
    return list(table.get(zhi, []))


def get_pillar_body(pillar: str, variant: str = 'main') -> List[str]:
    """宫位身段。pillar ∈ year/month/day/hour；variant='ch11' 取 ch11 变体。"""
    table = PILLAR_BODY_CH11 if variant == 'ch11' else PILLAR_BODY
    return list(table.get(pillar, []))


def get_shishen_body(shishen: str) -> List[str]:
    """十神身体部位（正印/偏印→印 等类别归并；禄/羊刃直查）。"""
    group = _SHISHEN_GROUP.get(shishen, shishen)
    return list(SHISHEN_BODY.get(group, []))


def _lookup_pairs(table: Dict[frozenset, List[str]], zhis) -> List[str]:
    keys = set(zhis)
    for pair, diseases in table.items():
        if pair <= keys:
            return list(diseases)
    return []


def get_disease_by_hai(zhi_a: str, zhi_b: str) -> List[str]:
    """六穿主病查表（两支无序）。"""
    return _lookup_pairs(HAI_DISEASE, (zhi_a, zhi_b))


def get_disease_by_po(zhi_a: str, zhi_b: str) -> List[str]:
    """破主病查表（仅书明文两组）。"""
    return _lookup_pairs(PO_DISEASE, (zhi_a, zhi_b))


def get_disease_by_xing(zhis) -> List[str]:
    """三刑主病查表（2-3 支集合）。"""
    return _lookup_pairs(XING_DISEASE, zhis)


def _self_check() -> List[str]:
    """数据完整性自检：主表覆盖 10 干 12 支、键合法。返回问题列表（空=通过）。"""
    problems = []
    gans = set(GAN_WX)
    for table, name in ((GAN_BODY, 'GAN_BODY'), (GAN_BODY_EXT, 'GAN_BODY_EXT')):
        if set(table) != gans:
            problems.append(f'{name} 未覆盖 10 干: {gans ^ set(table)}')
    for table, name in ((ZHI_BODY, 'ZHI_BODY'), (ZHI_BODY_EXT, 'ZHI_BODY_EXT')):
        if set(table) != set(DI_ZHI):
            problems.append(f'{name} 未覆盖 12 支: {set(DI_ZHI) ^ set(table)}')
    for table, name in ((PILLAR_BODY, 'PILLAR_BODY'), (PILLAR_BODY_CH11, 'PILLAR_BODY_CH11')):
        if set(table) != set(PILLAR_KEYS):
            problems.append(f'{name} 未覆盖四柱: {set(PILLAR_KEYS) ^ set(table)}')
    for table, name in ((HAI_DISEASE, 'HAI_DISEASE'), (PO_DISEASE, 'PO_DISEASE'),
                        (XING_DISEASE, 'XING_DISEASE')):
        for key in table:
            if not key <= set(DI_ZHI):
                problems.append(f'{name} 含非法地支键: {key}')
    return problems


if __name__ == '__main__':
    issues = _self_check()
    print('self_check:', 'OK' if not issues else issues)
