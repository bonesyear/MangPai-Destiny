"""
juefa - 盲派诀法层·主观层（subjective）

理论来源：段建业《盲派命理高级内容篇》第十四章「盲派诀法集锦」
  （OCR 19533-21101：14.1 伤官诀/过河拆桥格等特殊格局；14.2 断语22项+八字断句集；
    14.3 巾箱秘术字碰字）。

四大块：
  1. 伤官诀五行喜忌 5 类（金水喜见官/土金喜佩印怕见官/水木喜财官/木火喜见印/
     火土看组合）——伤官见官非一律凶，按五行×节令×配置分向；
  2. 盲派断语 22 项——查表型触发（计数/入墓/三刑/争合/禄支冲穿/悬针等）；
     第 15/17/19 项以「财/食为用神」为前提，未提供 yongshen_result 一律不评估
     （防过杀）；第 18 项须 shensha_result（天乙×羊刃同柱）；
  3. 八字断句集 8 域 26 条——可查表子集即时评估，象法换读类存查；
  4. 巾箱秘术字碰字 6 组 + 日元月令诀言词典（书仅载 6 条样例，词典驱动可扩展）。

不做（避免重复检测，仅存诀言引用）：过河拆桥格（caiming.py 已实现分键）、
贼神捕神（zeishen_bushen.py）。岁运引动属应期层，本模块只出原局信号与隐患标记。

分层：subjective/，单向依赖 objective；不接 engine（同 yunfan/zhiye 模式，
仅 __init__ 重导出）。置信度：中（断语为经验 heuristic，命中≠定验）。
"""
from typing import Dict, List, Optional

from mangpai.objective.bazi_calc import ten_god
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.constants import (
    DI_ZHI, GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG,
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI, XING_PAIRS, SAN_HE,
    TOMB_MAP, LU,
)

__all__ = ['analyze_juefa', 'DUANYU_22', 'DUANJU_TABLE', 'ZIPENGZI_RULES',
           'JINXIANG_JUEYAN', 'SHANGGUAN_JUE_VERSE']

_PILLARS = ['year', 'month', 'day', 'hour']
_PILLAR_CN = {'year': '年', 'month': '月', 'day': '日', 'hour': '时'}

# ── 诀言常量（原文录存）──
SHANGGUAN_JUE_VERSE = (
    '金水伤官喜见官，官来调候格局清。土金伤官宜佩印，印来制伤贵气生。'
    '水木伤官喜财官，财官相佐福禄盈。木火伤官官要旺，官星制伤有权柄。'
    '火土伤官看组合，或喜或忌局中定。伤官见官分宜畏，全在五行与节令。'
)
GUOHE_CHAIQIAO_VERSE = (
    '过河拆桥是真机，主位财重生宾官。财官能量聚一处，制住此官发巨资。'
    '宾位官杀关联我，得权之后制官宜。原局制住功业大，运岁制住亦堪奇。'
    '桥为官杀财为河，拆桥即在制官时。此格多主大富命，商海巨鳄掌枢机。'
)
ZEI_BUSHEN_VERSE = (
    '辛金巳午捕神旺，亥水伤官贼神藏。捕神制贼效率高，官贵格局非寻常。'
    '运入北方贼神地，制贼得力步朝堂。贼捕之理通造化，功名大小此中量。'
)
HEZHI_VERSE = '癸水重重杀星明，乙木食神制杀清。食神制杀合杀贵，武职权柄在军中。合制格局亦妙法，制住忌神便成名。'
LUREN_VERSE = '甲木归禄在时寅，双丙透干食神真。木火通明青云路，日禄归时贵气深。禄刃为体怕损伤，配置得宜福寿臻。'
ZIPENGZI_VERSE = (
    '字碰字来象乃成，吉凶祸福由此生。丙逢壬癸江湖客，戊见甲寅筋骨伤。'
    '辛金遇丁牢狱灾，乙木逢辛残疾病。巳亥相逢多驿马，辰戌相冲宝库开。'
    '字字组合藏玄机，诀言对应事即明。'
)
YUNSUI_YINDONG_VERSE = (
    '原局诀言定根基，运岁引动应期至。运来字碰原局字，吉凶之事便发起。'
    '流年再逢关键处，如钟报时不差迟。冲合刑穿皆为引，最怕伏吟反吟时。'
)

# ── 断语 22 项数据表（verse=原书七言断语；gating 标特殊门槛）──
DUANYU_22: List[Dict] = [
    {'id': 1, 'title': '财官印禄两头钳，决非走卒等人闲', 'domain': '富贵总评',
     'verse': '年时财官印禄钳，富贵根基已先天。纵有风波终不困，决非庸碌等闲人。'},
    {'id': 2, 'title': '独财能招千金，财多不富需比助', 'domain': '财运',
     'verse': '独财一位坐旺乡，千金可招福自长。财星叠见反不富，比劫相助方为良。'},
    {'id': 3, 'title': '财星若有库，发财能存住；财库临三合，必发万金', 'domain': '财运/应期',
     'verse': '财星入库如藏珍，不逢刑冲难见金。库逢三合或冲开，万贯家财自然来。'},
    {'id': 4, 'title': '官杀混杂，喜者存之，憎者去之；武人留杀，文人留官', 'domain': '事业/职业分流',
     'verse': '官杀混杂局不清，去留舒配贵方成。武职留杀显威权，文职留官享清名。'},
    {'id': 5, 'title': '伤官见官，为祸百端；伤官伤尽，官场风流', 'domain': '事业/官非/婚姻',
     'verse': '伤官见官祸连绵，是非口舌官非缠。伤官伤尽反为奇，才华横溢步云梯。'},
    {'id': 6, 'title': '枭神夺食，必主灾殃；枭印重重，克子伤身', 'domain': '子女/健康/福气',
     'verse': '枭神夺食最不良，衣食有损病灾殃。女命逢之克子息，男命遇此多乖张。'},
    {'id': 7, 'title': '比劫重重必克父，财星破印母先亡', 'domain': '六亲（父母）',
     'verse': '比劫如林父难安，财星坏印母先残。提纲克年亲不全，六亲缘分看宫星。'},
    {'id': 8, 'title': '女命财官一入墓，终身难嫁难找主', 'domain': '婚姻（女命）',
     'verse': '坤命财官入墓中，姻缘路上多阻风。红鸾不动心难许，孤灯自守到老终。',
     'needs_gender': 'female'},
    {'id': 9, 'title': '伤官生财为人正，食伤有刑是苦命', 'domain': '性情/财运/六亲',
     'verse': '伤官生财自奔忙，勤劳致富性本良。食伤带刑福气损，六亲无靠命多殃。'},
    {'id': 10, 'title': '伤官见官女命差，命定风流无桃花', 'domain': '婚姻（女命）',
     'verse': '女命伤官见官星，心高气傲克夫刑。婚姻不顺多争吵，外缘虽多难真情。',
     'needs_gender': 'female'},
    {'id': 11, 'title': '女命食伤带三刑，克夫伤子六亲凶', 'domain': '婚姻/子女/六亲',
     'verse': '食伤带刑女命凶，克夫伤子祸重重。三刑若临日时位，家破人亡运不通。',
     'needs_gender': 'female'},
    {'id': 12, 'title': '争合风流又好色，三角恋爱做小妾', 'domain': '婚姻/性情',
     'verse': '天干争合心不定，情路多歧风流性。尤其女命逢争合，易入偏房妾室命。'},
    {'id': 13, 'title': '官杀太弱婚不顺，食伤太旺婚难成', 'domain': '婚姻（女命）',
     'verse': '官杀微弱夫星藏，姻缘迟来或无形。食伤太旺克夫星，纵有姻缘也难长。',
     'needs_gender': 'female'},
    {'id': 14, 'title': '七杀无制，见比肩抗杀，为犯罪分子', 'domain': '牢狱/官非',
     'verse': '七杀无制如虎狼，比肩抗杀逞凶狂。不是牢狱即伤残，江湖行走必遭殃。'},
    {'id': 15, 'title': '身弱财旺日主合财，没钱要抢钱', 'domain': '牢狱/财运',
     'verse': '身弱财旺不胜财，日主合财惹祸灾。求财无门生歹意，非法夺取牢狱来。',
     'needs_yongshen': True},
    {'id': 16, 'title': '禄作寿元不可伤，岁运重伤命自亡', 'domain': '寿元/灾祸',
     'verse': '禄神乃是寿元星，最怕刑冲穿害侵。岁运并临伤禄处，阎王索命不留情。'},
    {'id': 17, 'title': '财星定为养生源，被伤被破走黄泉', 'domain': '寿元/财运/健康',
     'verse': '财星养命是源泉，无财则贫有财安。财星若被劫刃破，不是丧命也伤残。',
     'needs_yongshen': True},
    {'id': 18, 'title': '贵人头上带刃剑，死于非命遭人算', 'domain': '灾祸（横死）',
     'verse': '天乙贵人逢羊刃，吉神带凶煞气侵。表面风光内藏险，恐遭暗算命归阴。',
     'needs_shensha': True},
    {'id': 19, 'title': '食神为寿食有伤，岁运再逢必死亡', 'domain': '寿元',
     'verse': '食神本是寿星名，最怕枭神夺食惊。又怕旺财来破印，岁运逢之寿元倾。',
     'needs_yongshen': True},
    {'id': 20, 'title': '寅申穿梭禄受伤，岁运逢冲非命亡', 'domain': '灾祸/寿元',
     'verse': '寅申巳亥四长生，穿梭往来动不停。禄神若在穿梭地，岁运冲激命必倾。'},
    {'id': 21, 'title': '重金伐木凶机伏，年月悬针命主苦', 'domain': '健康/贫贱',
     'verse': '木秀逢金砍伐伤，筋骨疼痛病在床。年月更逢金锐利，悬针煞现苦命当。'},
    {'id': 22, 'title': '合处逢冲，冲处逢合，一般为结婚应期', 'domain': '婚姻应期',
     'verse': '姻缘应期有妙法，合处逢冲喜事发。冲处逢合亦为婚，鸳鸯和合便成家。'},
]

# ── 八字断句集 8 域（checkable=False 者存查，不参与 hits）──
DUANJU_TABLE: List[Dict] = [
    # 父母
    {'domain': '父母', 'text': '父母宫位与父母星同时被坏，方可断父母死亡', 'checkable': False,
     'note': '元规则（双条件 gate），见断语第7项'},
    {'domain': '父母', 'text': '父临库，父当早死', 'checkable': True, 'rule': 'fu_ru_ku'},
    {'domain': '父母', 'text': '财星破印母先亡', 'checkable': True, 'rule': 'cai_po_yin'},
    # 婚姻
    {'domain': '婚姻', 'text': '配偶星多，选不了对象，搞不定', 'checkable': True, 'rule': 'spouse_many'},
    {'domain': '婚姻', 'text': '妻星妻宫犯冲，老婆要进来', 'checkable': True, 'rule': 'wife_star_chong'},
    {'domain': '婚姻', 'text': '夫宫穿夫星，不叫制，是一种仇恨', 'checkable': True, 'rule': 'gong_chuan_star'},
    # 事业
    {'domain': '事业', 'text': '七杀制伤官，伤官当权力看', 'checkable': False, 'note': '象法换读，须做功层'},
    {'domain': '事业', 'text': '官没伤，官还在，职务还有', 'checkable': False, 'note': '岁运存续判断'},
    {'domain': '事业', 'text': '食神穿杀，下野，贬了官', 'checkable': True, 'rule': 'shishen_chuan_sha'},
    {'domain': '事业', 'text': '劫财下面带的官，人家的权力（别人是一把手）', 'checkable': True, 'rule': 'jie_xia_guan'},
    # 财运
    {'domain': '财运', 'text': '财库喜刑，发财的命', 'checkable': True, 'rule': 'caiku_xichong'},
    {'domain': '财运', 'text': '坐下财库，必须刑冲', 'checkable': True, 'rule': 'day_caiku'},
    {'domain': '财运', 'text': '闭了财库，破财', 'checkable': True, 'rule': 'caiku_bi'},
    {'domain': '财运', 'text': '财把劫财制住了，劫财当财看', 'checkable': False, 'note': '象法换读，须做功层'},
    # 牢狱
    {'domain': '牢狱', 'text': '食神不自由，库一关被抓', 'checkable': True, 'rule': 'shishen_rumu'},
    {'domain': '牢狱', 'text': '伤官合官，肯定是打官司', 'checkable': True, 'rule': 'shangguan_he_guan'},
    {'domain': '牢狱', 'text': '身弱财旺，日主合财，没钱要抢钱', 'checkable': False, 'note': '同断语第15项'},
    # 性情
    {'domain': '性情', 'text': '伤官透天干，发表的意思', 'checkable': True, 'rule': 'shangguan_tou'},
    {'domain': '性情', 'text': '水多寒湿欠光明，性格阴郁', 'checkable': True, 'rule': 'shui_duo_hanshi'},
    {'domain': '性情', 'text': '金见水沉为牢狱，也主思想消极', 'checkable': True, 'rule': 'jin_chen_shui'},
    # 健康
    {'domain': '健康', 'text': '旺者成病衰者痛，被泄被克都是病', 'checkable': False, 'note': '五行旺衰病机总则'},
    {'domain': '健康', 'text': '青龙干头怕见虎，白虎多逢肢体伤（甲木见庚金多）', 'checkable': True, 'rule': 'qinglong_baihu'},
    {'domain': '健康', 'text': '女命日坐是阳刃，子宫刀伤断的准', 'checkable': True, 'rule': 'female_day_ren'},
    # 杂项
    {'domain': '杂项', 'text': '只有读懂原局，才能知道大运流年的好坏', 'checkable': False, 'note': '元规则：原局优先'},
    {'domain': '杂项', 'text': '六合换象，如果没有制住也不能换', 'checkable': False, 'note': '象法层引用（换象门槛=制住）'},
    {'domain': '杂项', 'text': '三刑全见，里面有六亲时，主六亲有伤病或残疾', 'checkable': True, 'rule': 'sanxing_quan'},
]

# ── 字碰字 6 组规则（14.3，OCR 20920-20948）──
ZIPENGZI_RULES: List[Dict] = [
    {'id': 'bing_ren_gui', 'pair': ('丙', ['壬', '癸']), 'scope': 'gan',
     'xiang': '太阳遇江河湖海',
     'ji': '配置佳：航运、贸易、旅游之才', 'xiong': '奔波远行江湖、血液/眼睛疾病'},
    {'id': 'wu_jiayin', 'pair': ('戊', ['甲', '寅']), 'scope': 'both',
     'xiang': '高山厚土遇参天大树，木土相战',
     'ji': '', 'xiong': '脾胃疾病、筋骨损伤、车祸、皮肤伤病'},
    {'id': 'xin_ding', 'pair': ('辛', ['丁']), 'scope': 'gan',
     'xiang': '珠玉遇炉火锻冶',
     'ji': '为喜：成名、冶炼、电力事业', 'xiong': '为忌：官非、牢狱、血光'},
    {'id': 'yi_xin', 'pair': ('乙', ['辛']), 'scope': 'gan',
     'xiang': '花草禾苗遇剪刀针尖',
     'ji': '', 'xiong': '肢体伤残、手术、针砭之苦、胆小怕事'},
    {'id': 'si_hai', 'pair': ('巳', ['亥']), 'scope': 'zhi',
     'xiang': '驿马相冲',
     'ji': '', 'xiong': '动荡至极、远行、搬家、职业多变、心思不定'},
    {'id': 'chen_xu', 'pair': ('辰', ['戌']), 'scope': 'zhi',
     'xiang': '水库火库相冲，库冲则开',
     'ji': '财库/官库开：发财、得权', 'xiong': '伤官库/比劫库开：争斗、破财'},
]

# ── 巾箱秘术日元月令诀言词典（书中仅载 6 条样例，OCR 20857-21061；可扩展）──
JINXIANG_JUEYAN: Dict[tuple, Dict] = {
    ('甲子', '寅'): {'verse': '甲子日元寅月生，禄马同窠福气清。最喜阳火出干头，木火通明贵福寿。若逢庚辛干支重，奔波劳碌贫贱终。',
                 'note': '喜丙丁透干；忌庚辛重'},
    ('乙卯', '辰'): {'verse': '乙卯日元辰月生，藤萝系甲木向荣。最忌重金来伐木，庚申辛酉命必促。双庚夹身无水解，阎王索命不久住。',
                 'note': '忌庚辛/庚申辛酉；双庚夹身无水解大凶'},
    ('丙午', '卯'): {'verse': '丙午日元卯月生，木火通明势如龙。壬癸出干江湖走，戊己制水方安宁。',
                 'note': '壬癸透→江湖；戊己制水→安'},
    ('壬戌', '子'): {'verse': '壬戌日元子月生，财官双美火土荣。辰戌相冲开宝库，运逢东南发万钟。',
                 'note': '辰戌冲开财库→发'},
    ('乙巳', '卯'): {'verse': '乙巳日元卯月生，禄地食神福气增。双子夹巳卯刑子，到老病死无子哭。',
                 'note': '双子夹巳+子卯刑→无子'},
    ('己巳', '戌'): {'verse': '己巳日元戌月生，火土铸印贵格成。庚金伤官双透干，运逢丙丁耀门庭。',
                 'note': '庚伤双透，丙丁运贵'},
}

# ── 十神分组 ──
_GROUP = {
    '正印': '印', '偏印': '印', '正官': '官', '七杀': '杀',
    '正财': '财', '偏财': '财', '比肩': '比劫', '劫财': '比劫',
    '食神': '食伤', '伤官': '伤官', '日主': '日主',
}


# ══ 内部：预计算结构 ══

def _build_ctx(gans: List[str], zhis: List[str], day_gan: str) -> Dict:
    """统一预计算：天干十神/藏干十神/分组计数/五行计数。"""
    ss = {}
    for i, g in enumerate(gans):
        ss[_PILLARS[i]] = '日主' if i == 2 else ten_god(day_gan, g)
    # 藏干十神（各支全藏干；get_canggan_mangpai 返回 [(干, 本/中/余气)]）
    hidden: Dict[str, List] = {}
    for i, z in enumerate(zhis):
        hidden[_PILLARS[i]] = [(hg, ten_god(day_gan, hg))
                               for hg, _qi in get_canggan_mangpai(z)]

    def count(gods, full_hidden=False):
        """gods: 十神集合。full_hidden=False 只计天干+支本气；True 计全藏干。"""
        n = sum(1 for v in ss.values() if v in gods)
        for zgs in hidden.values():
            for j, (_, hss) in enumerate(zgs):
                if not full_hidden and j > 0:
                    break
                if hss in gods:
                    n += 1
        return n

    tou = {g: ss[p] for p in _PILLARS}     # 天干透出十神
    return {
        'ss': ss, 'hidden': hidden, 'count': count, 'tou': tou,
        'gan_wx': [GAN_WX.get(g, '') for g in gans],
        'zhi_wx': [ZHI_WX.get(z, '') for z in zhis],
    }


def _in_pairs(a, b, pairs):
    return (a, b) in pairs or (b, a) in pairs


def _zhi_rel(zhis, z, pairs):
    """z 与局中他支存在 pairs 关系 → 返回对方支列表。"""
    return [w for w in zhis if w != z and _in_pairs(z, w, pairs)]


def _tomb_of(wx):
    """五行的墓支（TOMB_MAP 反查）。"""
    return [z for z, wxs in TOMB_MAP.items() if wx in wxs]


# ══ 伤官诀 5 类 ══

def _shangguan_jue(gans, zhis, day_gan, ctx) -> Dict:
    """伤官诀五行喜忌。返回 {'matched': bool, ...}。"""
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx:
        return {'matched': False}
    sg_wx = WX_SHENG.get(day_wx, '')          # 我生者=伤官五行
    month_zhi = zhis[1]
    sg_tou = any(GAN_WX.get(g) == sg_wx for g in gans)
    sg_present = sg_tou or any(ZHI_WX.get(z) == sg_wx for z in zhis)
    wx_in_chart = lambda wx: any(GAN_WX.get(g) == wx for g in gans) or \
        any(ZHI_WX.get(z) == wx for z in zhis)
    wx_count = lambda wx: sum(1 for g in gans if GAN_WX.get(g) == wx) + \
        sum(1 for z in zhis if ZHI_WX.get(z) == wx)

    base = {'verse': SHANGGUAN_JUE_VERSE}
    if day_wx == '金' and sg_wx == '水' and sg_present and month_zhi in ('亥', '子', '丑', '申', '酉'):
        # 金水伤官喜见官（冬月正格；申酉金旺生水为变格，如乾隆酉月子水伤官）
        r = dict(base, matched=True, type='金水伤官',
                 variant='正格' if month_zhi in ('亥', '子', '丑') else '变格（金旺生水）')
        if wx_in_chart('火'):
            r['verdict'] = '喜见官（调候暖局，限原局配置；岁运见官坏连体伤官反主灾）'
        else:
            r['verdict'] = '金水伤官格成但原局无火官杀，调候未应'
        if ZHI_WX.get(zhis[2]) == '水':
            r['veto_note'] = '伤官与日干连体（日支水），不可冲伤；岁运冲之凶（寿元/才智受损）'
        return r
    if day_wx == '土' and sg_wx == '金' and sg_present and \
            (month_zhi in ('申', '酉', '戌') or wx_count('金') >= 3):
        r = dict(base, matched=True, type='土金伤官',
                 variant='正格' if month_zhi in ('申', '酉', '戌') else '变格（金成势）')
        facets = []
        if wx_in_chart('火'):
            facets.append('伤官佩印（火印制伤生身，贵格候选）')
        if wx_in_chart('木') and not wx_in_chart('火'):
            facets.append('怕见官（木官杀无火印通关，伤官见官破格，主困顿/官非）')
        r['verdict'] = '；'.join(facets) if facets else '土金伤官格成，喜忌未显（无火印亦无木官）'
        return r
    if day_wx == '水' and sg_wx == '木' and sg_tou:
        # 水木伤官喜财官（月令可放宽：伤官透而水有印根即论，如案例五酉月）
        r = dict(base, matched=True, type='水木伤官')
        facets = []
        if wx_in_chart('火') and wx_in_chart('土'):
            facets.append('喜财官（火财泄木、土官杀制水护财，主升迁/名利）')
        # 枭夺食忌：偏印（庚/辛）透且与木伤官干紧贴（相邻柱）
        xiao_gans = {'壬': '庚', '癸': '辛'}
        xiao = xiao_gans.get(day_gan)
        sg_idx = [i for i, g in enumerate(gans) if GAN_WX.get(g) == '木']
        xiao_idx = [i for i, g in enumerate(gans) if g == xiao]
        if any(abs(i - j) == 1 for i in sg_idx for j in xiao_idx):
            facets.append('忌：偏印紧贴伤官（枭神夺食）破格')
        r['verdict'] = '；'.join(facets) if facets else '水木伤官格成，财官未齐'
        return r
    if day_wx == '木' and sg_wx == '火' and sg_present and month_zhi in ('巳', '午', '未'):
        r = dict(base, matched=True, type='木火伤官')
        if wx_in_chart('水'):
            r['verdict'] = '伤官佩印（水印制火生身，木火通明有制，主文教/职权）'
            r['note'] = '总诀另载「官要旺，官星制伤有权柄」——书内两套并存，案例实印佩印，以印为主信号'
        else:
            r['verdict'] = '木火伤官格成但无水印制火，泄身太过'
        return r
    if day_wx == '火' and sg_wx == '土' and sg_present:
        r = dict(base, matched=True, type='火土伤官', combination_dependent=True)
        if wx_in_chart('水') and wx_count('土') >= 2:
            r['verdict'] = '伤官制杀候选（土伤官有力制水官杀，化凶为权/富）；' \
                           '此类或喜或忌全在组合，交 yongshen/gongliang 层定方向'
        else:
            r['verdict'] = '火土伤官格成，看组合（喜忌不定，交方向层）'
        return r
    return {'matched': False, 'verse': SHANGGUAN_JUE_VERSE}


# ══ 断语 22 项检测 ══

def _duanyu_hits(gans, zhis, day_gan, ctx, gender,
                 yongshen_result, shensha_result):
    hits: List[Dict] = []
    skipped: List[Dict] = []
    meta = {d['id']: d for d in DUANYU_22}
    c = ctx['count']
    tou_ss = list(ctx['ss'].values())

    def emit(i, detail, confidence='中'):
        hits.append({'id': i, 'title': meta[i]['title'], 'domain': meta[i]['domain'],
                     'verse': meta[i]['verse'], 'detail': detail, 'confidence': confidence})

    def skip(i, reason):
        skipped.append({'id': i, 'title': meta[i]['title'], 'reason': reason})

    cai, yin = {'正财', '偏财'}, {'正印', '偏印'}
    guan, sha, guansha = {'正官'}, {'七杀'}, {'正官', '七杀'}
    bijiao = {'比肩', '劫财'}
    shishang = {'食神', '伤官'}

    # 1 财官印禄两头钳（年柱与时柱各带财/官/印/禄之一）
    lu_zhi = LU.get(day_gan, '')
    def _ji_shen_at(i):
        got = []
        if ctx['ss'][_PILLARS[i]] in cai | guansha | yin:
            got.append(ctx['ss'][_PILLARS[i]])
        for j, (_, hss) in enumerate(ctx['hidden'][_PILLARS[i]]):
            if j == 0 and hss in cai | guansha | yin:
                got.append(hss + '(藏)')
        if zhis[i] == lu_zhi:
            got.append('禄')
        return got
    y_got, h_got = _ji_shen_at(0), _ji_shen_at(3)
    if y_got and h_got:
        emit(1, f"年柱带{'、'.join(y_got)}，时柱带{'、'.join(h_got)}，根基归宿两钳")

    # 2 独财 / 财多不富
    cai_n = c(cai, full_hidden=True)
    if cai_n == 1:
        emit(2, '财星独一位（含藏干仅1），清纯为我所专，主聚财')
    elif cai_n >= 3:
        emit(2, f'财星{cai_n}重多杂，财多不富，需比劫助身担财或成从财格')

    # 3 财库（财五行之墓在局；逢三合/刑冲为库动）
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')  # 我克者=财五行
    ku_zhis = [z for z in _tomb_of(cai_wx) if z in zhis]
    if ku_zhis:
        ku = ku_zhis[0]
        open_by = []
        for trio in SAN_HE:
            if ku in trio and sum(1 for t in trio if t in zhis) >= 2 and \
                    any(t in zhis for t in trio if t != ku):
                open_by.append(f"三合{'/'.join(trio)}会库")
        if _zhi_rel(zhis, ku, LIU_CHONG):
            open_by.append('冲开库')
        if _zhi_rel(zhis, ku, XING_PAIRS):
            open_by.append('刑开库')
        detail = f'{cai_wx}财之库（{ku}）在局，主存钱守成'
        detail += '；' + '，'.join(open_by) + '，库动财源涌' if open_by else '；库门未动，待岁运三合刑冲'
        emit(3, detail)

    # 4 官杀混杂（官与杀并见，透干或支本气）
    if c(guan) >= 1 and c(sha) >= 1:
        he_qu = []
        for i, g in enumerate(gans):
            if ctx['ss'][_PILLARS[i]] in guansha:
                partner = TIAN_GAN_HE.get(g, '')
                if partner and partner in [x for j, x in enumerate(gans) if j != i]:
                    he_qu.append(f'{g}被合去')
        emit(4, '正官七杀并见，心性不定事业驳杂，宜去留其一'
                + (f'（{"、".join(he_qu)}）' if he_qu else '（未见合去）')
                + '；武职留杀、文职留官')

    # 5 伤官见官 / 伤官伤尽（伤尽须全藏干查无官杀）
    sg_tou = '伤官' in tou_ss
    zg_tou = '正官' in tou_ss
    guansha_all = c(guansha, full_hidden=True)
    shishang_all = c(shishang, full_hidden=True)
    if sg_tou and zg_tou:
        emit(5, '伤官见官（同透）：无财印通关则叛逆官非、事业挫折（五行伤官诀例外者另判）')
    elif shishang_all >= 3 and guansha_all == 0:
        emit(5, f'食伤{shishang_all}重而全局无一点官星（含藏干），伤官伤尽，反主才华超群')

    # 6 枭神夺食 / 枭印重重
    if '偏印' in tou_ss and '食神' in tou_ss:
        emit(6, '偏印克食神同透，损福失业、子女缘薄，重则病灾')
    elif c({'偏印'}) >= 2:
        emit(6, f"偏印{c({'偏印'})}重，泄耗日主，主身体不佳、子息艰难")

    # 7 比劫重重克父 / 财星破印母亡（须星+宫双坏方验）
    bi_n, cai_n2, yin_n = c(bijiao), c(cai), c(yin)
    star_bad = []
    if bi_n >= 3 and cai_n2 <= 1:
        star_bad.append('比劫重重财星孤弱（父星受克）')
    if cai_n2 >= 3 and yin_n <= 1:
        star_bad.append('财旺印孤（母星受克）')
    if star_bad:
        y_zhi_bad = bool(_zhi_rel(zhis[1:], zhis[0], LIU_CHONG) or
                         _zhi_rel(zhis[1:], zhis[0], XING_PAIRS) or
                         _zhi_rel(zhis[1:], zhis[0], LIU_HAI))
        # 书「提纲（月柱）克年柱，亦主父母不全」（gaoji:20230）——方向=月干
        # 克年干（F12 修正：旧码 WX_KE_ME 检出「年干克他干」，方向接反）
        y_gan_ke = WX_KE.get(GAN_WX.get(gans[1], ''), '') == GAN_WX.get(gans[0], '')
        if y_zhi_bad or y_gan_ke:
            emit(7, '；'.join(star_bad) + '，且年柱（父母宫）受坏——星宫双坏，父母缘薄可断')
        else:
            emit(7, '；'.join(star_bad) + '，但年柱未受坏——星坏宫未坏，不轻断生死', confidence='低')

    # 8 女命财官入墓（墓库紧闭方验）
    if gender == 'female':
        guan_wx = WX_KE_ME.get(day_wx, '')  # 克我者=官杀五行
        guan_tombs = [z for z in _tomb_of(guan_wx) if z in zhis]
        guan_tou = any(s in guansha for s in tou_ss)
        if guan_tombs and not guan_tou:
            tomb = guan_tombs[0]
            opened = _zhi_rel(zhis, tomb, LIU_CHONG) or _zhi_rel(zhis, tomb, LIU_HE) or \
                     _zhi_rel(zhis, tomb, XING_PAIRS)
            if not opened:
                emit(8, f'官杀五行（{guan_wx}）之墓（{tomb}）在局且官杀不透、无冲合开库，夫缘深藏，婚姻极不顺')
            else:
                emit(8, f'官杀入墓（{tomb}）但墓有冲合开库，夫星可出，凶减', confidence='低')
    else:
        skip(8, '需女命（gender=female）')

    # 9 伤官生财 / 食伤有刑
    if sg_tou and (cai & set(tou_ss) or c(cai) >= 1):
        emit(9, '伤官生财组合，凭技术口才智慧求财，勤劳致富')
    xs_zhis = [zhis[i] for i in range(4) if ctx['ss'][_PILLARS[i]] in shishang]
    for xz in xs_zhis:
        partners = _zhi_rel(zhis, xz, XING_PAIRS)
        # 三刑（寅巳申/丑戌未/子卯），自刑同支不计
        partners = [p for p in partners if p != xz]
        if partners:
            emit(9, f'食伤支{xz}与{"".join(partners)}相刑，食伤有刑——福气才华子女受损，一生劳苦')
            break

    # 10 女命伤官见官（伤官透干或居本气支 ∧ 正官透）
    if gender == 'female':
        sg_benqi = any(zgs and zgs[0][1] == '伤官' for zgs in ctx['hidden'].values())
        if (sg_tou or sg_benqi) and zg_tou:
            extra = ''
            for i, g in enumerate(gans):
                if ctx['ss'][_PILLARS[i]] == '正官':
                    partner = TIAN_GAN_HE.get(g, '')
                    rivals = [x for j, x in enumerate(gans) if j != i and x == partner]
                    if len(rivals) >= 2:
                        extra = '；比劫争合夫星（三角加重）'
            emit(10, '女命伤官见官（夫星受克），挑剔夫妻不和' + extra)
    else:
        skip(10, '需女命（gender=female）')

    # 11 女命食伤带三刑（刑及日支夫宫/时支子息宫）
    if gender == 'female':
        for i in range(4):
            if ctx['ss'][_PILLARS[i]] in shishang:
                xz = zhis[i]
                partners = [p for p in _zhi_rel(zhis, xz, XING_PAIRS) if p != xz]
                if partners and (xz == zhis[2] or xz == zhis[3] or
                                 zhis[2] in partners or zhis[3] in partners):
                    emit(11, f'食伤支{xz}三刑刑及{"夫宫(日支)" if zhis[2] in (xz, *partners) else "子息宫(时支)"}，夫子有灾家庭破碎')
                    break
    else:
        skip(11, '需女命（gender=female）')

    # 12 争合（一干被≥2同干合；支同理）
    zhenghe = []
    for g in set(gans):
        partner = TIAN_GAN_HE.get(g, '')
        if partner and gans.count(partner) >= 2:
            zhenghe.append(f'两{partner}争合一{g}')
    for z in set(zhis):
        partners = [w for w in zhis if _in_pairs(z, w, LIU_HE) and w != z]
        if len(partners) >= 2:
            zhenghe.append(f'支{"".join(partners)}争合{z}')
    if zhenghe:
        emit(12, '；'.join(zhenghe) + '——心性不定感情多角' + ('，女命尤忌（易为偏房）' if gender == 'female' else ''))

    # 13 女命官杀太弱 / 食伤太旺
    if gender == 'female':
        gs_n, st_n = c(guansha), c(shishang)
        if gs_n == 0:
            emit(13, '女命官杀全无，夫缘浅薄婚难成')
        elif gs_n <= 1 and st_n >= 3:
            emit(13, f'女命官杀孤弱而食伤{st_n}重，克夫星太过，婚难维持')
    else:
        skip(13, '需女命（gender=female）')

    # 14 七杀无制 + 比肩抗杀
    if c(sha) >= 1 and c(yin) == 0 and c(shishang) == 0 and c(bijiao) >= 2:
        emit(14, f"七杀{c(sha)}无印化无食伤制，比劫{c(bijiao)}与之相抗——以暴抗暴，官非牢狱伤残之象")

    # 15 身弱财旺日主合财（须 yongshen）
    if yongshen_result is None:
        skip(15, '未提供 yongshen_result，防过杀不评估')
    else:
        strength = (yongshen_result.get('bijiao_duocai') or {}).get('strength', '')
        he_gan = TIAN_GAN_HE.get(day_gan, '')
        he_is_cai = he_gan in gans and ten_god(day_gan, he_gan) in cai
        if strength == '身弱' and c(cai) >= 3 and he_is_cai:
            emit(15, f'身弱财旺（{c(cai)}财）且日主合{he_gan}财——富屋贫人求财无门，运不助身易铤而走险')

    # 16 禄作寿元（原局隐患；岁运应期不判）
    if lu_zhi and lu_zhi in zhis:
        hurts = []
        for h in (_zhi_rel(zhis, lu_zhi, LIU_CHONG) + _zhi_rel(zhis, lu_zhi, XING_PAIRS) +
                  _zhi_rel(zhis, lu_zhi, LIU_HAI)):
            if h != lu_zhi and h not in hurts:
                hurts.append(h)
        if hurts:
            emit(16, f'日主禄在{lu_zhi}，原局被{"".join(hurts)}刑冲穿——寿元隐患，岁运再伤禄为应期')

    # 17 财为养命源（须 yongshen：财为用神=身强/从弱）
    if yongshen_result is None:
        skip(17, '未提供 yongshen_result，防过杀不评估')
    else:
        strength = (yongshen_result.get('bijiao_duocai') or {}).get('strength', '')
        if strength in ('身强', '从弱'):
            cai_hurt = []
            if c(bijiao) >= 1 and c(cai) >= 1:
                cai_hurt.append('比劫夺财')
            for i in range(4):
                if ZHI_WX.get(zhis[i]) == cai_wx and _zhi_rel(zhis, zhis[i], LIU_CHONG):
                    cai_hurt.append(f'财支{zhis[i]}逢冲')
            if cai_hurt:
                emit(17, f'财为用神（{strength}）而{"、".join(cai_hurt)}——养命源受损，贫病之象')

    # 18 贵人头上带刃剑（须 shensha）
    # F1 标注：生产恒 skip——唯一生产调用方 yongshen.py:886 不传
    # shensha_result（配置断路）；仅测试直达。接线决策留 shensha 修复批。
    if shensha_result is None:
        skip(18, '未提供 shensha_result，不评估')
    else:
        ty_p = set(shensha_result.get('天乙贵人', {}).get('in_pillars', []))
        yr_p = set(shensha_result.get('羊刃', {}).get('in_pillars', []))
        sha_p = {p for p, s in ctx['ss'].items() if s == '七杀'}
        both = ty_p & (yr_p | sha_p)
        if both:
            emit(18, f'天乙贵人与{"羊刃" if ty_p & yr_p else "七杀"}同临{"、".join(_PILLAR_CN[p] for p in sorted(both))}柱，吉神染凶，防贵人反目突遭横祸')

    # 19 食神为寿（须 yongshen）
    if yongshen_result is None:
        skip(19, '未提供 yongshen_result，防过杀不评估')
    else:
        if '食神' in tou_ss:
            dangers = []
            if '偏印' in tou_ss:
                dangers.append('偏印透干（枭夺食）')
            if c(cai) >= 2 and c(yin) == 1:
                dangers.append('财旺破印（印不护食）')
            if dangers:
                emit(19, f'食神透干为寿元星，原局{"、".join(dangers)}——寿元隐患，岁运枭财再透为应期')

    # 20 寅申穿梭禄受伤（原局信号）
    if lu_zhi in ('寅', '申', '巳', '亥') and lu_zhi in zhis:
        chong = _zhi_rel(zhis, lu_zhi, LIU_CHONG)
        if chong:
            emit(20, f'禄在{lu_zhi}（四生长驿马地）逢{"".join(chong)}对冲，禄被冲动——主重大变动灾祸（车祸/突发疾病），岁运再冲为应期')

    # 21 重金伐木（木日主金≥3无水化；水被合绊不能化金不算；庚申/辛酉在年月为悬针）
    if GAN_WX.get(day_gan) == '木':
        jin_n = sum(1 for g in gans if GAN_WX.get(g) == '金') + \
            sum(1 for z in zhis if ZHI_WX.get(z) == '金')
        # 水须「能化金」：被合绊之水（如子丑合绊，书例辛酉辛丑乙卯丙子）不计
        shui_free = 0
        for i, g in enumerate(gans):
            if GAN_WX.get(g) == '水' and TIAN_GAN_HE.get(g) not in \
                    [x for j, x in enumerate(gans) if j != i]:
                shui_free += 1
        for i, z in enumerate(zhis):
            if ZHI_WX.get(z) == '水' and not any(
                    j != i and _in_pairs(z, zhis[j], LIU_HE) for j in range(4)):
                shui_free += 1
        if jin_n >= 3 and shui_free == 0:
            xuanzhen = [f'{_PILLAR_CN[_PILLARS[i]]}柱{gans[i]}{zhis[i]}'
                        for i in (0, 1) if gans[i] + zhis[i] in ('庚申', '辛酉')]
            emit(21, f'木日主金{jin_n}重无水解化（合绊之水不化），筋骨肝胆神经之疾、早年多灾'
                     + (f'；悬针煞现（{"、".join(xuanzhen)}），一生贫苦' if xuanzhen else ''))

    # 22 合处逢冲/冲处逢合（原局信号；结婚应期须岁运层）
    if gender:
        spouse_ss = cai if gender == 'male' else guansha
        day_zhi = zhis[2]
        signals = []
        he_partners = [w for w in zhis if w != day_zhi and _in_pairs(day_zhi, w, LIU_HE)]
        chong_partners = _zhi_rel(zhis, day_zhi, LIU_CHONG)
        if he_partners:
            signals.append(f'夫妻宫{day_zhi}与{"".join(he_partners)}合——岁运冲开合解为婚动（合处逢冲）')
        if chong_partners:
            signals.append(f'夫妻宫{day_zhi}与{"".join(chong_partners)}冲——岁运合住解冲为婚成（冲处逢合）')
        if signals:
            emit(22, '；'.join(signals))
    else:
        skip(22, '需 gender 定配偶星/夫妻宫语境')

    return hits, skipped


# ══ 断句集可查表子集 ══

def _duanju_hits(gans, zhis, day_gan, ctx, gender):
    hits: List[Dict] = []
    c = ctx['count']
    tou_ss = list(ctx['ss'].values())
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')  # 我克者=财五行
    table = {d['rule']: d for d in DUANJU_TABLE if d.get('checkable')}

    def emit(rule, detail):
        d = table[rule]
        hits.append({'domain': d['domain'], 'text': d['text'], 'detail': detail})

    bijiao = {'比肩', '劫财'}
    cai, yin = {'正财', '偏财'}, {'正印', '偏印'}
    guansha = {'正官', '七杀'}

    # 父母：父临库父早死（财五行之墓在局）；财星破印母先亡
    if any(z in zhis for z in _tomb_of(cai_wx)) and c(cai, full_hidden=True) <= 1:
        emit('fu_ru_ku', f'{cai_wx}财（父星）之墓在局，父星入墓库，父当早死（须年宫同验方断，见断语7）')
    if c(cai) >= 3 and c(yin) <= 1:
        emit('cai_po_yin', '财旺印孤，财星破印，母先亡（须年宫同验方断）')

    # 婚姻：配偶星多 / 妻星妻宫犯冲 / 夫宫穿夫星
    if gender:
        spouse = cai if gender == 'male' else guansha
        if c(spouse, full_hidden=True) >= 3:
            emit('spouse_many', f'配偶星{c(spouse, full_hidden=True)}重，选择困难搞不定')
        star_z = [zhis[i] for i in range(4) if ZHI_WX.get(zhis[i]) in
                  {GAN_WX.get(g) for g in gans if ten_god(day_gan, g) in spouse} and i != 2]
        if gender == 'male' and _zhi_rel(zhis, zhis[2], LIU_CHONG) and c(cai) >= 1:
            emit('wife_star_chong', f'妻宫{zhis[2]}逢冲且财星在局——婚姻动象（应期信号，非凶）')
        chuan_targets = [z for z in star_z if _in_pairs(zhis[2], z, LIU_HAI)]
        if chuan_targets:
            emit('gong_chuan_star', f'日支{zhis[2]}穿配偶星支{"".join(chuan_targets)}——穿非制，主夫妻仇恨')

    # 事业：食神穿杀（食神柱支与七杀柱支成穿）；劫财下官
    ss_pos = ctx['ss']
    shi_z = [zhis[i] for i in range(4) if ss_pos[_PILLARS[i]] == '食神']
    sha_z = [zhis[i] for i in range(4) if ss_pos[_PILLARS[i]] == '七杀']
    for a in shi_z:
        for b in sha_z:
            if a != b and _in_pairs(a, b, LIU_HAI):
                emit('shishen_chuan_sha', f'食神支{a}穿七杀支{b}——下野贬官')
    for i, g in enumerate(gans):
        if ss_pos[_PILLARS[i]] == '劫财':
            partner = TIAN_GAN_HE.get(g, '')
            for j, g2 in enumerate(gans):
                if j != i and g2 == partner and ss_pos[_PILLARS[j]] == '正官':
                    emit('jie_xia_guan', f'劫财{g}合官{g2}——权力属他人（别人是一把手）')

    # 财运：财库喜刑冲 / 坐下财库须刑冲 / 闭了财库破财
    ku_list = [z for z in _tomb_of(cai_wx) if z in zhis]
    if ku_list:
        ku = ku_list[0]
        if _zhi_rel(zhis, ku, XING_PAIRS) or _zhi_rel(zhis, ku, LIU_CHONG):
            emit('caiku_xichong', f'财库{ku}逢刑冲，库开发财的命')
        if zhis[2] == ku and not (_zhi_rel(zhis, ku, XING_PAIRS) or _zhi_rel(zhis, ku, LIU_CHONG)):
            emit('day_caiku', f'日支坐财库{ku}而无刑冲，库闭难大发，待岁运刑冲')
        if _zhi_rel(zhis, ku, LIU_HE):
            emit('caiku_bi', f'财库{ku}被{"、".join(_zhi_rel(zhis, ku, LIU_HE))}合闭——破财')

    # 牢狱：食神入墓 / 伤官合官
    shi_wx = WX_SHENG.get(day_wx, '')
    if any(z in zhis for z in _tomb_of(shi_wx)) and '食神' in tou_ss:
        emit('shishen_rumu', f'食神透而{shi_wx}之墓在局，食神入墓被闭——失去自由之象')
    for i, g in enumerate(gans):
        if ss_pos[_PILLARS[i]] == '伤官':
            partner = TIAN_GAN_HE.get(g, '')
            for j, g2 in enumerate(gans):
                if j != i and g2 == partner and ss_pos[_PILLARS[j]] in guansha:
                    emit('shangguan_he_guan', f'伤官{g}合{g2}{ss_pos[_PILLARS[j]]}——官司诉讼')

    # 性情：伤官透 / 水多寒湿 / 金沉水底
    if '伤官' in tou_ss:
        emit('shangguan_tou', '伤官透干——爱表达发表')
    shui_n = ctx['gan_wx'].count('水') + ctx['zhi_wx'].count('水')
    huo_n = ctx['gan_wx'].count('火') + ctx['zhi_wx'].count('火')
    if shui_n >= 3 and zhis[1] in ('亥', '子', '丑') and huo_n == 0:
        emit('shui_duo_hanshi', f'水{shui_n}重冬生无火，寒湿欠光明——性格阴郁')
    jin_n = ctx['gan_wx'].count('金') + ctx['zhi_wx'].count('金')
    if jin_n >= 2 and shui_n >= 3:
        emit('jin_chen_shui', f'金{jin_n}水{shui_n}，金沉水底——牢狱象+思想消极')

    # 健康：青龙怕白虎（甲见庚多）/ 女命日坐阳刃
    if ('甲' in gans or day_gan == '甲') and gans.count('庚') >= 2:
        emit('qinglong_baihu', f'甲木（青龙）逢庚（白虎）×{gans.count("庚")}——肢体伤')
    if gender == 'female':
        from mangpai.objective.shensha import _YANG_REN_FULL
        ren_list = _YANG_REN_FULL.get(day_gan, [])
        if zhis[2] in ren_list:
            emit('female_day_ren', f'女命日支{zhis[2]}为羊刃——子宫刀伤')

    # 杂项：三刑全见
    for trio in (('寅', '巳', '申'), ('丑', '戌', '未')):
        if all(t in zhis for t in trio):
            emit('sanxing_quan', f'{"、".join(trio)}三刑全见——刑中藏干为六亲星者主该六亲伤病残疾（六亲定位接 liuqin）')

    return hits


# ══ 字碰字 ══

def _zipengzi_hits(gans, zhis) -> List[Dict]:
    hits = []
    for rule in ZIPENGZI_RULES:
        a, bs = rule['pair']
        scope = rule['scope']
        pool_a = gans if scope == 'gan' else (zhis if scope == 'zhi' else gans + zhis)
        pool_b = pool_a if scope != 'both' else gans + zhis
        if a in pool_a and any(b in pool_b for b in bs):
            hit_bs = [b for b in bs if b in pool_b]
            hits.append({'id': rule['id'],
                         'combo': f"{a}见{''.join(hit_bs)}",
                         'xiang': rule['xiang'],
                         'ji': rule['ji'], 'xiong': rule['xiong'],
                         'verse': ZIPENGZI_VERSE})
    return hits


# ══ 主入口 ══

def analyze_juefa(
    gans: List[str],
    zhis: List[str],
    day_gan: str,
    gender: Optional[str] = None,
    yongshen_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """盲派诀法层分析（高级篇第14章）。

    参数：
      gans/zhis — 四柱天干/地支（年月日时序）
      day_gan — 日干
      gender — 'male'/'female'；None 则女命专属断语与婚姻应期项跳过
      yongshen_result — yongshen 方向总线结果（第15/17/19项前提；缺省跳过防过杀）
      shensha_result — 神煞结果（第18项天乙×羊刃同柱前提；缺省跳过）

    返回：
      shangguan_jue / duanyu_hits / duanyu_skipped / duanju_hits /
      zipengzi_hits / jueyan / related_verses / hit_count / summary
    """
    gans = list(gans or [])
    zhis = list(zhis or [])
    if len(gans) != 4 or len(zhis) != 4 or not day_gan:
        return {'shangguan_jue': {'matched': False}, 'duanyu_hits': [],
                'duanyu_skipped': [], 'duanju_hits': [], 'zipengzi_hits': [],
                'jueyan': None, 'related_verses': {}, 'hit_count': 0,
                'summary': '输入不全，诀法未评估'}

    ctx = _build_ctx(gans, zhis, day_gan)
    sg = _shangguan_jue(gans, zhis, day_gan, ctx)
    duanyu_hits, duanyu_skipped = _duanyu_hits(
        gans, zhis, day_gan, ctx, gender, yongshen_result, shensha_result)
    duanju_hits = _duanju_hits(gans, zhis, day_gan, ctx, gender)
    zipengzi_hits = _zipengzi_hits(gans, zhis)

    day_gz = gans[2] + zhis[2]
    jueyan = JINXIANG_JUEYAN.get((day_gz, zhis[1]))
    if jueyan:
        jueyan = dict(jueyan, day_gz=day_gz, month_zhi=zhis[1])

    related = {'过河拆桥格': GUOHE_CHAIQIAO_VERSE, '贼神捕神': ZEI_BUSHEN_VERSE,
               '合制格': HEZHI_VERSE, '禄刃格': LUREN_VERSE}

    parts = []
    if sg.get('matched'):
        parts.append(f"伤官诀·{sg['type']}：{sg.get('verdict', '')}")
    if duanyu_hits:
        parts.append(f"断语命中{len(duanyu_hits)}项（{ '、'.join(str(h['id']) for h in duanyu_hits) }）")
    if duanju_hits:
        parts.append(f"断句{len(duanju_hits)}条")
    if zipengzi_hits:
        parts.append('字碰字：' + '、'.join(h['combo'] for h in zipengzi_hits))
    if jueyan:
        parts.append(f"巾箱诀言（{day_gz}日元{zhis[1]}月）：{jueyan['note']}")
    summary = '；'.join(parts) if parts else '诀法无命中'

    return {
        'shangguan_jue': sg,
        'duanyu_hits': duanyu_hits,
        'duanyu_skipped': duanyu_skipped,
        'duanju_hits': duanju_hits,
        'zipengzi_hits': zipengzi_hits,
        'jueyan': jueyan,
        'related_verses': related,
        'hit_count': len(duanyu_hits) + len(duanju_hits) + len(zipengzi_hits),
        'summary': summary,
    }
