"""
zhiye - 盲派职业象法·主观层（subjective）

理论来源：段建业《盲派命理高级内容篇》7.3「职业象法」（源文 10654-11089 行）
核心思想：职业定位以「象法为王」——先定取财方式（经营/风险/智力/体力/工薪），
          再以干支类象 + 十神组合精确定行业。多象定一象（取做功最有力的组合）。

五类职业定位（源文 7.3 三-七节）：
  1. 会计/财务：亥子辰水（数字象），财穿印做功、金水财星组合、食伤带财、
     财库/印库不开管他营。
  2. 医生/医疗：金（辛酉=针刀）+ 火（丙丁巳=炎症）相克，食伤做功，金羊刃带库
     （辛酉见丑）、食神合印（中医）、土金食伤带印（制药）、辰丑库（医院），
     七杀+伤官包制（牙科）。
  3. 教师/教育：木火通明（甲乙见丙丁），食伤在门户（时柱），印星月令为用，
     财星虚透合印，金水伤官见印库（理科）。
  4. 律师/法务：申酉金（律令）、辛金（法律金融），伤官制官/伤官见官、
     食神制官，卯酉冲/卯午破（依律破例）。
  5. 商人/经营：财星做功，财印门户（开店），食伤生财（贸易），内食神（办厂），
     相冲做功（运输），官杀当财被制（大生意）；五行行业（金水金融物流/木火
     文教餐饮/土金地产矿/火土能源化工）。
  6. 军警/军阀/武职（非常规）：官杀成势 + 羊刃/灾煞 + 申酉金/辛 + 全阳；
     局象官杀包局/夹官/全阳、换官象加权。
  7. 演艺/演员（非常规）：食伤+桃花+财（色相求财），桃花居夫妻宫，丙丁火+桃花；
     局象食伤包局、换食伤象加权。

消费关系：
  - objective.constants（五行生克/藏干）
  - objective.canggan.get_canggan_mangpai（藏干，十神定位）
  - objective.xiangfa.get_liushi_ganzhi_xiang（六十干支组合象 person 字段，行业象）
  - objective.zuogong_detect.detect_relations（克/合/冲/穿/破，做功组合）
  - objective.shensha.compute_shensha_ext（羊刃/灾煞/桃花，军警与演艺象）
  - subjective.xiangfa_ops.analyze_xiangfa_ops（合象 hexiang/换象 huanxiang/局象 juxiang
    互证：换官象→律师/公门/军职，换财象→商人，换食伤象→演艺/医生/教师；
    官杀包局/全阳/夹官→军职公门，食伤包局→演艺(配官杀→公检法)；合象产新象印证组合）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：职业象法为高度解释性归纳（类象+组合启发式，非精确分类器）；多象定一象
          的阈值各师有微调；商人象最宽，须结合五行行业细分。
置信度：中

M2 基础职业类目（七桶未成象时的第二梯队，段氏《中级》取财方法·体力取财）：
  「体力取财做功之神应是比肩、劫财与禄神」，做功效率低者「八亿的农民与民工
  都在这一阶层」——贫/小康 + 功神含比劫（合/冲/穿两端、克/刑/破制方）或
  禄神当财 + 无工薪/经营/风险路径 -> laborer（农民/工人·体力劳动者，
  田土参与做功提示农、金参与提示工）；严重破财凶向（比劫夺财 severe）或
  贫而全局无做功 -> unemployed（无业）。七桶最高分 < 阈值时不再硬塞，
  输出「未分类」+ 最高分桶名作提示（hint），fallback 升格为合法第一输出。
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME, TOMB_MAP,
    PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext, resolve_shensha
from mangpai.objective.muku import analyze_muku
from mangpai.objective.xiangfa import get_liushi_ganzhi_xiang
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.yongshen import assess_direction_signals

_YANG_GANS = set('甲丙戊庚壬')

# ── 最低分阈值：多象定一象的成象门槛 ──
#   五桶（医生/教师/律师/商人/军政，外加会计/演艺）取最高分定位职业，但最高分低于
#   此阈值时各桶均为弱信号共现、不足成象，fallback「无明确职业倾向」而非硬塞最像
#   的一桶。校准（《命理珍宝》郝金阳10例端到端）：
#     非标命局各桶弱信号共现，最高分≤5：乞丐(merchant5)/坐牢(teacher4)/破财(merchant4)/
#       找二婚(doctor3) -> 抑制为「无明确职业倾向」；
#     真职业成象，最高分≥6：律师7/军警10/演艺7/教师7/商人6 -> 保留。
#   已知例外：开车(第4期 military9)为庚坐申禄+丑金库身有力抗杀，引擎理法自洽判武职，
#   与郝断「申为传送主车=司机」金标准相左；该例无凶向信号(fanju/pocai)不触发军警
#   gating，且分高(9)过阈值，非阈值可覆盖，属已知口径分歧（见 calib-zhenbao 注）。
_MIN_SCORE_THRESHOLD = 6


# ───────────────────── 共用小工具 ─────────────────────

def _compute_shishen(day_gan: str, gan: str) -> str:
    day_wx = GAN_WX.get(day_gan, '')
    gan_wx = GAN_WX.get(gan, '')
    if not day_wx or not gan_wx:
        return ''
    same_polarity = (day_gan in _YANG_GANS) == (gan in _YANG_GANS)
    if gan_wx == day_wx:
        return '比肩' if same_polarity else '劫财'
    if WX_SHENG.get(day_wx) == gan_wx:
        return '食神' if same_polarity else '伤官'
    if WX_SHENG.get(gan_wx) == day_wx:
        return '偏印' if same_polarity else '正印'
    if WX_KE.get(day_wx) == gan_wx:
        return '偏财' if same_polarity else '正财'
    if WX_KE.get(gan_wx) == day_wx:
        return '七杀' if same_polarity else '正官'
    return ''


def _cat(ss: str) -> str:
    if not ss:
        return ''
    if ss in ('正官', '七杀'):
        return '官杀'
    if ss in ('正财', '偏财'):
        return '财'
    if ss in ('正印', '偏印'):
        return '印'
    if ss in ('食神', '伤官'):
        return '食伤'
    if ss in ('比肩', '劫财'):
        return '比劫'
    return ''


def _wx_cat(day_gan: str, wx: str) -> str:
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx or not wx:
        return ''
    if wx == day_wx:
        return '比劫'
    if WX_SHENG.get(day_wx) == wx:
        return '食伤'
    if WX_SHENG.get(wx) == day_wx:
        return '印'
    if WX_KE.get(day_wx) == wx:
        return '财'
    if WX_KE.get(wx) == day_wx:
        return '官杀'
    return ''


def _pillar_cats(day_gan: str, gan: str, zhi: str) -> Set[str]:
    cats: Set[str] = set()
    c = _cat(_compute_shishen(day_gan, gan))
    if c:
        cats.add(c)
    zw = ZHI_WX.get(zhi, '')
    if zw:
        cats.add(_wx_cat(day_gan, zw))
    for idx, (cg, _) in enumerate(get_canggan_mangpai(zhi)):
        if idx <= 1:
            cats.add(_cat(_compute_shishen(day_gan, cg)))
    cats.discard('')
    return cats


def _ensure_relations(day_gan, gans, zhis, relations):
    if relations is not None:
        return relations
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {}
    try:
        return detect_relations(
            day_gan, zhis[PILLAR_KEYS.index('day')],
            gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
    except Exception:
        return {}


def _main_qi_cats(day_gan: str, gans: List[str], zhis: List[str], i: int) -> Set[str]:
    """柱主气十神集（干本身 + 支本气）——柱级 _pillar_cats 含藏干中气，
    四支柱几乎必然带入财/印/食伤而泛触；主气粒度只认透干与支本气
    （K3 职业批1 统一粒度：merchant 门户/lawyer 制官/teacher 印重/
    military 驾杀 共用）。"""
    out: Set[str] = set()
    if gans[i]:
        out.add(_cat(_compute_shishen(day_gan, gans[i])))
    cg = get_canggan_mangpai(zhis[i])
    if cg:
        out.add(_cat(_compute_shishen(day_gan, cg[0][0])))
    return out - {''}


def _main_qi_char_count(day_gan: str, gans: List[str], zhis: List[str],
                        cat: str) -> int:
    """主气十神字数（透干+支本气逐字计，同柱干支各算一字，0-8）——柱集计
    数（_main_qi_cats）下 甲寅/丙午 类透干通根只算一柱，埋没了「官星两现」
    的强度信息（K3 职业批2：官商之间/金成势金融 以字数论强弱）。"""
    n = 0
    for i in range(4):
        if gans[i] and _cat(_compute_shishen(day_gan, gans[i])) == cat:
            n += 1
        cg = get_canggan_mangpai(zhis[i])
        if cg and _cat(_compute_shishen(day_gan, cg[0][0])) == cat:
            n += 1
    return n


def _action_main_qi(action: Dict, day_gan: str, gans: List[str], zhis: List[str],
                    ) -> Tuple[Set[str], Set[str]]:
    """动作两端当事人的主气十神（干动作看两端干、支动作看两端支本气；
    暗合=支中藏干相合，当事人含本气+中气——口径同 _score_merchant._act_cats）。
    日干位记 {'日主'}。"""
    fi, ti = _pos_idx(action.get('from_pos', '')), _pos_idx(action.get('to_pos', ''))
    if fi < 0 or ti < 0:
        return set(), set()

    def _one(pos, i):
        if pos == 'day_gan':
            return {'日主'}
        if pos.endswith('_gan'):
            return {_cat(_compute_shishen(day_gan, gans[i]))} - {''}
        cg = get_canggan_mangpai(zhis[i])
        if not cg:
            return set()
        if action.get('type') == '暗合':
            return {_cat(_compute_shishen(day_gan, g)) for g, _ in cg[:2]} - {''}
        return {_cat(_compute_shishen(day_gan, cg[0][0]))} - {''}

    return _one(action.get('from_pos', ''), fi), _one(action.get('to_pos', ''), ti)


def _has_main_qi_action(wa: List[Dict], day_gan: str, gans: List[str],
                        zhis: List[str], cat_a: str, cat_b: str,
                        types: Set[str]) -> bool:
    """指定类型动作且两端主气当事人分别为 cat_a/cat_b（双向）——
    _action_between_cats 的主气粒度版（柱级判据把藏干中气携带者全判
    当事人，官命案伤官见官结构全中泛触）。"""
    for a in wa:
        if a.get('auxiliary') or a.get('type') not in types:
            continue
        fa, ta = _action_main_qi(a, day_gan, gans, zhis)
        if (cat_a in fa and cat_b in ta) or (cat_b in fa and cat_a in ta):
            return True
    return False


def _pos_idx(pos: str) -> int:
    k = pos.split('_')[0]
    return PILLAR_KEYS.index(k) if k in PILLAR_KEYS else -1


def _is_zhu_pos(pos: str) -> bool:
    """主位（日/时柱）判定。"""
    return pos.split('_')[0] in ('day', 'hour') if pos else False


def _action_between_cats(
    wa: List[Dict], day_gan: str, gans: List[str], zhis: List[str],
    cat_a: str, cat_b: str, types: Set[str],
) -> List[Dict]:
    """两十神大类柱之间的指定类型动作（双向）。

    只认做功动作（非 auxiliary）——M4 扩展检出（宾位干克/宾位入墓/宾宾合制）
    为结构事实，不证"被制"做功。
    """
    out: List[Dict] = []
    for a in wa:
        if a.get('auxiliary'):
            continue
        if a.get('type') not in types:
            continue
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        if fi < 0 or ti < 0:
            continue
        fa = _pillar_cats(day_gan, gans[fi], zhis[fi])
        ta = _pillar_cats(day_gan, gans[ti], zhis[ti])
        if (cat_a in fa and cat_b in ta) or (cat_b in fa and cat_a in ta):
            out.append(a)
    return out


def _action_between_wx(
    wa: List[Dict], gans: List[str], zhis: List[str],
    wx_a: str, wx_b: str, types: Set[str],
) -> List[Dict]:
    """两五行柱之间的指定类型动作（按柱主五行，双向）。"""
    def _pillar_wx(i: int) -> str:
        # 柱主五行：地支主气优先，否则天干
        zw = ZHI_WX.get(zhis[i], '')
        return zw or GAN_WX.get(gans[i], '')
    out: List[Dict] = []
    for a in wa:
        if a.get('type') not in types:
            continue
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        if fi < 0 or ti < 0:
            continue
        fw, tw = _pillar_wx(fi), _pillar_wx(ti)
        if (fw == wx_a and tw == wx_b) or (fw == wx_b and tw == wx_a):
            out.append(a)
    return out


def _has_cat(day_gan: str, gans: List[str], zhis: List[str], cat: str) -> bool:
    return any(cat in _pillar_cats(day_gan, gans[i], zhis[i]) for i in range(4))


def _wx_count(day_gan: str, gans: List[str], zhis: List[str]) -> Dict[str, int]:
    cnt: Dict[str, int] = {w: 0 for w in ('木', '火', '土', '金', '水')}
    for g in gans:
        w = GAN_WX.get(g, '')
        if w:
            cnt[w] += 1
    for z in zhis:
        w = ZHI_WX.get(z, '')
        if w:
            cnt[w] += 1
    return cnt


# ───────────────────── 五类职业打分 ─────────────────────

def _score_accountant(day_gan, gans, zhis, wa, muku) -> Tuple[int, List[str]]:
    score = 0
    ev: List[str] = []
    # 亥子辰水（数字象）：base+1，若伴随会计 distinctive 信号再加+1
    shui_zhis = [z for z in zhis if z in ('亥', '子', '辰')]
    has_distinct = bool(_action_between_cats(wa, day_gan, gans, zhis, '财', '印', {'穿'}))
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    if cai_wx in ('金', '水') and _has_cat(day_gan, gans, zhis, '财'):
        has_distinct = True
    closed = {t.get('zhi') for t in (muku.get('closed_tombs') or [])}
    if closed:
        has_distinct = True
    if shui_zhis:
        score += 2 if has_distinct else 1
        ev.append(f'亥子辰水现{len(shui_zhis)}字（数字象{"，配会计组合" if has_distinct else "，弱信号"})')
    # 财穿印做功
    if _action_between_cats(wa, day_gan, gans, zhis, '财', '印', {'穿'}):
        score += 2
        ev.append('财穿印做功（钱财管理×数字计算）')
    # 金水财星组合
    if cai_wx in ('金', '水') and _has_cat(day_gan, gans, zhis, '财'):
        score += 1
        ev.append('金水财星组合（金融理财）')
    # 食伤带财
    if _has_cat(day_gan, gans, zhis, '食伤') and _has_cat(day_gan, gans, zhis, '财'):
        score += 1
        ev.append('食伤带财（头脑管钱）')
    # 财库/印库不开管他营
    yin_wx = ''
    for w, child in WX_SHENG.items():
        if child == day_wx:
            yin_wx = w
            break
    tomb_zhis = set()
    for w in (cai_wx, yin_wx):
        if w == '木':
            tomb_zhis.add('未')
        elif w == '火':
            tomb_zhis.add('戌')
        elif w == '金':
            tomb_zhis.add('丑')
        elif w in ('水', '土'):
            tomb_zhis.add('辰')
    if tomb_zhis & closed:
        score += 1
        ev.append('财/印库不开（管公家他人之财）')
    # 水财坐实+食伤算计+局无官杀 +3（K3 职业批2 雇员帐房通道）：财五行属水
    # （数字/流动之象）且透干、亥子辰在局、食伤主气算计、局中无官杀主气
    # （非官非吏=受雇管帐）——书锚 yx-会计「我就是个会计呀」（壬子水财透干
    # 通根+申金食神算计+局无官杀）。有官杀主气者财归经营/管理（老板/官员
    # 之命，水财亦可房地产/贸易），不以雇员会计论；金≥3者金归金融成象。
    _n_gs_char = _main_qi_char_count(day_gan, gans, zhis, '官杀')
    _jin_cnt = (sum(1 for z in zhis if z in ('申', '酉'))
                + sum(1 for g in gans if g in ('庚', '辛')))
    _n_ss_main = sum(1 for i in range(4)
                     if '食伤' in _main_qi_cats(day_gan, gans, zhis, i))
    _n_cai_main = sum(1 for i in range(4)
                      if '财' in _main_qi_cats(day_gan, gans, zhis, i))
    _cai_tou = any(g and _cat(_compute_shishen(day_gan, g)) == '财' for g in gans)
    if (cai_wx == '水' and _cai_tou and shui_zhis and _n_ss_main >= 1
            and _n_gs_char == 0 and _jin_cnt < 3):
        score += 3
        ev.append('水财坐实+食伤算计（局无官杀，雇员帐房/会计）')
    # 金成势金融 +6（K3 职业批2 独力通道）：申酉庚辛≥4字 + 印主气≥3柱 +
    # 局无财主气 + 官杀主气≤1字——金印成势而局中无财=管公家钱财之金融机构
    # （金=金融/数字，印=机构/公家，局中无财=所管非己之财），书锚 yx-2658
    # 「实际此女为一家银行行长，金有金融之意」（金5印3无财）、reg67-银行
    # 行长央行「银行·金融官员」（金4印3无财）、《高级》案例七「财库包局，
    # 银行工作」。带官杀≥2字者金归律令/兵刃（lawyer/military 侧，li151 穷
    # 教书匠官2字不入此象）；有财主气者以财论经营（merchant 侧）。
    _n_yin_main = sum(1 for i in range(4)
                      if '印' in _main_qi_cats(day_gan, gans, zhis, i))
    if _jin_cnt >= 4 and _n_yin_main >= 3 and _n_cai_main == 0 and _n_gs_char <= 1:
        score += 6
        ev.append(f'金成势{_jin_cnt}字+印重{_n_yin_main}柱（局中无财，金融机构管公家钱）')
    return score, ev


def _score_doctor(day_gan, gans, zhis, wa, ss) -> Tuple[int, List[str]]:
    score = 0
    ev: List[str] = []
    # 金（辛酉=针刀）+ 火（丙丁巳=炎症）相克（须实际火克金动作）
    jin = any(z in ('申', '酉') for z in zhis) or any(g in ('庚', '辛') for g in gans)
    huo = any(z in ('巳', '午') for z in zhis) or any(g in ('丙', '丁') for g in gans)
    if _action_between_wx(wa, gans, zhis, '金', '火', {'克'}):
        score += 2
        ev.append('火克金（针刀+炎症，外科/牙医）')
    elif jin and huo:
        score += 1
        ev.append('金针刀+火炎症并存（相战未成动作）')
    if _action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'}):
        # 七杀+伤官包制（牙科）
        score += 1
        ev.append('七杀+伤官包制（治金=治骨齿）')
    # 食伤做功
    if _has_cat(day_gan, gans, zhis, '食伤'):
        score += 1
        ev.append('食伤做功（技术求财）')
    # 金羊刃带库（辛酉见丑）
    yr = (ss.get('羊刃') or {}).get('zhi', '')
    if yr in ('酉',) and '丑' in zhis:
        score += 1
        ev.append('金羊刃带丑库（手术象）')
    # 食神合印（中医）
    if _action_between_cats(wa, day_gan, gans, zhis, '食伤', '印', {'天干合', '地支合', '半合'}):
        score += 1
        ev.append('食神合印（中医/药）')
    # 辰丑库（医院象，须金在局方取丑=金库/辰=药库）
    if jin and '丑' in zhis:
        score += 1
        ev.append('丑金库（医院/器械库）')
    elif '辰' in zhis and _has_cat(day_gan, gans, zhis, '食伤'):
        score += 1
        ev.append('辰中药库（医院象）')
    return score, ev


def _score_teacher(day_gan, gans, zhis, wa, ss=None) -> Tuple[int, List[str]]:
    score = 0
    ev: List[str] = []
    # 木火通明（压低共存加分）：段氏口径为「甲乙见丙丁」（天干木火相见）+2；
    # 仅地支木火共存为弱信号 +1（旧版干支统算 +2，木≥1火≥1 即中，过宽）。
    gan_wx = [GAN_WX.get(g, '') for g in gans if g]
    cnt = _wx_count(day_gan, gans, zhis)
    gan_muhuo = ('木' in gan_wx) and ('火' in gan_wx)
    if gan_muhuo:
        score += 2
        ev.append('木火通明（甲乙见丙丁，文象）')
    elif cnt.get('木', 0) >= 1 and cnt.get('火', 0) >= 1:
        score += 1
        ev.append('地支木火共存（文象弱信号）')
    # 食伤在门户（时柱）
    if '食伤' in _pillar_cats(day_gan, gans[3], zhis[3]):
        score += 2
        ev.append('食伤在时柱门户（以口为业）')
    # 印星月令为用——K3 职业批2 主气化：藏干中气带入之虚印不计（月干十神/
    # 月支本气为印方取，虚印泛触把演艺/吏员命全打上学校标签）
    if '印' in _main_qi_cats(day_gan, gans, zhis, 1):
        score += 1
        ev.append('月令印星（书本知识/学校）')
    # 财星虚透合印
    if _action_between_cats(wa, day_gan, gans, zhis, '财', '印', {'天干合'}):
        score += 1
        ev.append('财星虚透合印（才华换知识）')
    # 金水伤官见印库（理科）
    if (_has_cat(day_gan, gans, zhis, '食伤') and cnt.get('金', 0) and cnt.get('水', 0)
            and _has_cat(day_gan, gans, zhis, '印')):
        score += 1
        ev.append('金水伤官见印（数理理科）')
    # 印重馆阁 +2（K3 职业批1 新通道）：主气印≥2柱 + 主气食伤0柱 + 金不重型
    # （申酉庚辛<3）——印重无泄之纯学问/馆阁文职象（书锚 yx-6061 翰林院学士，
    # 印重成象贫而贵）；金重者归金融/律令不归文，食伤主气在局者走吐秀/门户
    # 通道（famous-乔布斯/外贸商 等印食并见经营命不触此条）。
    _n_yin_main = sum(1 for i in range(4)
                      if '印' in _main_qi_cats(day_gan, gans, zhis, i))
    _n_ss_main = sum(1 for i in range(4)
                     if '食伤' in _main_qi_cats(day_gan, gans, zhis, i))
    _jin_cnt = (sum(1 for z in zhis if z in ('申', '酉'))
                + sum(1 for g in gans if g in ('庚', '辛')))
    if _n_yin_main >= 2 and _n_ss_main == 0 and _jin_cnt < 3:
        score += 2
        ev.append('印重无食伤（馆阁纯学问之象）')
    # 食伤鬻文 +3（K3 职业批2 作家通道）：食伤主气≥3柱 + 财主气≥2柱 + 局无
    # 桃花 + 印主气0柱——食伤吐秀之极而财明现=以文鬻财（书锚 yx-梁羽生 作家：
    # 庚日子水伤官三柱+甲卯财两位）。有印者归馆阁/印食文墨，有桃花者归演艺。
    _n_cai_main = sum(1 for i in range(4)
                      if '财' in _main_qi_cats(day_gan, gans, zhis, i))
    _n_gs_main = sum(1 for i in range(4)
                     if '官杀' in _main_qi_cats(day_gan, gans, zhis, i))
    _has_tao = bool(((ss or {}).get('桃花') or {}).get('in_pillars'))
    if _n_ss_main >= 3 and _n_cai_main >= 2 and not _has_tao and _n_yin_main == 0:
        score += 3
        ev.append(f'食伤{_n_ss_main}柱吐秀+财{_n_cai_main}位（食伤鬻文，以文为业）')
    # 印食文墨授业 +4（K3 职业批2 教师 fn 主通道）：月令主气印（学校/单位
    # 之门）+ 印食共现（印=知识、食伤=表达，传授之象）+ 木火文象 + 财在局
    # （工薪取财）+ 金不重型（金重归金融/律令）+ 无卯酉冲（酒家门户象优先，
    # cj-老板）——段氏 7.3「先定取财方式」：官杀多寡定单位形态，三型居其一：
    #   无官杀·财食皆≥2 = 纯文职教书（书锚 zj-邢铭芬「教师」，印重无官）；
    #   官杀1·食伤≥3   = 吐秀授业（书锚 zj-教师无官，食伤成势以口为业）；
    #   官杀2·印≥2     = 印化官杀之文书传业（书锚 cj-2097 作家，甲寅印重）。
    # 印食并见之经营命（famous-乔布斯 食伤生财做实、yx-房地产 财重）不入三型
    # 强度，不触此条。
    _maoyou = any(
        a.get('type') == '冲'
        and _pos_idx(a.get('from_pos', '')) >= 0
        and _pos_idx(a.get('to_pos', '')) >= 0
        and frozenset({zhis[_pos_idx(a.get('from_pos', ''))],
                       zhis[_pos_idx(a.get('to_pos', ''))]}) == frozenset({'卯', '酉'})
        for a in wa)
    _muhuo_any = gan_muhuo or (cnt.get('木', 0) >= 1 and cnt.get('火', 0) >= 1)
    _month_yin_main = '印' in _main_qi_cats(day_gan, gans, zhis, 1)
    if (_month_yin_main and _n_yin_main >= 1 and _n_ss_main >= 1
            and _muhuo_any and _n_cai_main >= 1 and _jin_cnt < 3
            and not _maoyou and (
                (_n_gs_main == 0 and _n_cai_main >= 2 and _n_ss_main >= 2)
                or (_n_gs_main == 1 and _n_ss_main >= 3)
                or (_n_gs_main == 2 and _n_yin_main >= 2))):
        score += 4
        ev.append('印食文墨授业（月令印+印食共现+木火，教书/传授为业）')
    return score, ev


def _score_lawyer(day_gan, gans, zhis, wa) -> Tuple[int, List[str]]:
    score = 0
    ev: List[str] = []
    # 申酉金/辛金（律令法律）：base+1，有对抗组合再加+1
    has_jin = any(z in ('申', '酉') for z in zhis) or any(g in ('辛',) for g in gans)
    combo = bool(_action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'})) \
        or (_has_cat(day_gan, gans, zhis, '食伤') and _has_cat(day_gan, gans, zhis, '官杀'))
    # 卯酉冲/卯午破亦为对抗组合
    for a in wa:
        if a.get('type') in ('冲', '破'):
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi >= 0 and ti >= 0:
                pair = frozenset({zhis[fi], zhis[ti]})
                if pair == frozenset({'卯', '酉'}) or pair == frozenset({'卯', '午'}):
                    combo = True
                    break
    if has_jin:
        score += 2 if combo else 1
        ev.append(f'申酉金/辛金（律令法律{"，配对抗组合" if combo else "，弱信号"}）')
    # 伤官制官（实克动作，辩护对抗）；K3 职业批1 主气粒度收窄：克动作两端
    # 当事人主气为食伤/官杀方计 +2（实制）；柱级共存（藏干中气带入的伤官见官，
    # 官命案/银行/工人命局全中泛触）降为 +1 弱信号；食神制官共存条款删除
    # （条文制规则与伤官制官同形，柱级判据下纯泛触——银行簇/低保/工人全中）。
    if _has_main_qi_action(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'}):
        score += 2
        ev.append('伤官制官（辩护对抗）')
    elif _action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'}):
        score += 1
        ev.append('食伤制官（柱级共存，对抗弱信号）')
    # 卯酉冲/卯午破（依律破例，律师 distinctive）
    for a in wa:
        t = a.get('type', '')
        if t not in ('冲', '破'):
            continue
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        if fi < 0 or ti < 0:
            continue
        pair = frozenset({zhis[fi], zhis[ti]})
        if pair == frozenset({'卯', '酉'}) or pair == frozenset({'卯', '午'}):
            score += 2
            ev.append(f'{"".join(pair)}{t}（依律破例）')
            break
    return score, ev


def _score_merchant(day_gan, gans, zhis, wa) -> Tuple[int, List[str]]:
    """商人/经营象（重构：真实做功信号替换共现信号，上限 5→9，阈值 6 可达）。

    旧版全为 co-occurrence（_has_cat 存在即加分），上限 5 < _MIN_SCORE_THRESHOLD=6，
    merchant 永不能独力成象。重构后只认做功（非辅助动作两端涉财/食伤-财联动/
    主位合制宾财），共现仅留门户与五行行业辅证：
      财星入局做功 +2 / 主位合制宾财 +2 / 食伤生财做功 +2 /
      财印门户 +1 / 官杀当财被制 +1 / 冲财做功（贸易运输）+1 —— 上限 9。
    """
    score = 0
    ev: List[str] = []
    has_cai = _has_cat(day_gan, gans, zhis, '财')
    has_shishang = _has_cat(day_gan, gans, zhis, '食伤')
    non_aux = [a for a in wa if not a.get('auxiliary')]

    def _end_cats(a):
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        fa = _pillar_cats(day_gan, gans[fi], zhis[fi]) if fi >= 0 else set()
        ta = _pillar_cats(day_gan, gans[ti], zhis[ti]) if ti >= 0 else set()
        return fi, ti, fa, ta

    def _is_duocai_end(pos: str) -> bool:
        """夺财比劫端（主气判据）：干端=该干本身为比劫（日干本身克财=「我克者
        财」得财，非夺）；支端=支本气为比劫。同柱干/藏干余气不作夺财之神——
        段氏制财得财以做功主气为功神（同 P1 制尽判据「只排主位藏干不排主位
        透干」之主气粒度）。旧版以整柱 _pillar_cats 判：日支端因日干=比肩恒
        为夺财端，日支合财/制财（主位经营取财第一象，段氏「我合财、制宾财
        得财」）被全量误排，merchant 召回结构性塌陷（li213 申子合财误排同此）。
        """
        i = _pos_idx(pos)
        if i < 0:
            return False
        if pos.endswith('_gan'):
            if PILLAR_KEYS[i] == 'day':
                return False  # 日干本身
            return _cat(_compute_shishen(day_gan, gans[i])) == '比劫'
        cg = get_canggan_mangpai(zhis[i])
        return bool(cg) and _cat(_compute_shishen(day_gan, cg[0][0])) == '比劫'

    def _is_duocai(a) -> bool:
        """比劫夺财/争财动作（一端夺财比劫、另一端财）——段氏「制财得财」以
        功神非比劫为前提，夺财做功非经营取财，不入商人象（乞丐/清家荡产之
        子冲午类动作以此排除）。"""
        fi, ti, fa, ta = _end_cats(a)
        if fi < 0 or ti < 0:
            return False
        if _is_duocai_end(a.get('from_pos', '')) and '财' in ta:
            return True
        if _is_duocai_end(a.get('to_pos', '')) and '财' in fa:
            return True
        return False

    def _act_cats(a):
        """动作层十神（当事人主气粒度）：干动作（天干合/干克）只看两端干，
        支动作只看两端支本气——同柱携带之支/干非动作当事人，柱级十神
        （_pillar_cats 含藏干中气）判财/功神皆过宽（P0-c 旧版过触之源）。
        日干位记为 {'日主'}（日主=我，做功第一主体，非同比劫）。"""
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        if fi < 0 or ti < 0:
            return fi, ti, set(), set()

        def _one(pos, i):
            if pos == 'day_gan':
                return {'日主'}
            if pos.endswith('_gan'):
                return {_cat(_compute_shishen(day_gan, gans[i]))} - {''}
            cg = get_canggan_mangpai(zhis[i])
            if not cg:
                return set()
            if a.get('type') == '暗合':
                # 暗合=支中藏干相合（段氏「暗合者，支中藏干相合也」）——当事人
                # 即藏干（本气+中气），非独本气（寅丑暗合=己癸辛与甲丙戊之合，
                # 丑中癸财乃正当事人）
                return {_cat(_compute_shishen(day_gan, g)) for g, _ in cg[:2]} - {''}
            return {_cat(_compute_shishen(day_gan, cg[0][0]))} - {''}

        return fi, ti, _one(a.get('from_pos', ''), fi), _one(a.get('to_pos', ''), ti)

    # 群比夺财背景（比劫主气数 = 透干比劫[非日干] + 四支本气比劫，≥4 成群）：
    # 《中级》「只有比劫做功，比劫主竞争」（运动员/争夺之象，非经营取财）——
    # 群比环伺下 日主/比劫 制财为争夺、财自身发动之制亦难自保（财处被夺之
    # 地，做功非经营），皆不计（P0-c「制财得财以功神非比劫为前提」之延伸）。
    _bj_qi = sum(1 for i, g in enumerate(gans)
                 if g and PILLAR_KEYS[i] != 'day'
                 and _cat(_compute_shishen(day_gan, g)) == '比劫')
    _bj_qi += sum(1 for z in zhis
                  if get_canggan_mangpai(z)
                  and _cat(_compute_shishen(day_gan, get_canggan_mangpai(z)[0][0])) == '比劫')
    qunbi_duocai = _bj_qi >= 4

    # 财根被坏（段氏「财星太弱，财根被破…想赚钱又得不到钱」）：财本气之支被
    # 比劫主气之支冲（劫财冲财=坏财之根，非 7.3「相冲做功…物品交换」之贸易
    # 流动），被坏之财所在支的动作不以经营做功论（其做功为财之挣扎，虚功）。
    cai_root_broken: Set[str] = set()
    for a in non_aux:
        if a.get('type') != '冲':
            continue
        fi, ti, fa, ta = _act_cats(a)
        if fi < 0:
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if '比劫' in fa and '财' in ta and tp.endswith('_zhi'):
            cai_root_broken.add(tp)
        if '比劫' in ta and '财' in fa and fp.endswith('_zhi'):
            cai_root_broken.add(fp)

    # 1. 财星入局做功 +2——经营之本。动作层涉财（当事人主气见财）+ 方向/功神
    #    判据（段氏主宾论 + 《高级》7.3「经营做功之神：伤官、食神、财星」）：
    #      冲：双向（7.3「相冲做功…主商贸往来，象物品交换」，财参与即流动）；
    #      合类：须主位端参与、主位功神端主气非印/官杀/比劫（印主文化取财、
    #            官杀合财非经营[官杀当财须食伤制之]、比劫主合为夺）、且财在
    #            对面（我合宾财/财来就我）或日时互合己财——己财被宾位合走
    #            （合绊）非我得财；
    #      制类（克/穿/刑/破）：须主位发动（宾位发动=财被外制/财坏印，非我
    #            得财做功）；群比局中 日主/比劫/财 发动之制为争夺（群比夺财、
    #            财难自保），不计。
    cai_work = False
    chong_cai = False  # 冲且涉财（贸易运输）
    for a in non_aux:
        t = a.get('type', '')
        if t not in _HE_TYPES and t not in _ZHI_TYPES:
            continue
        if _is_duocai(a):
            continue
        fi, ti, fa, ta = _act_cats(a)
        if fi < 0 or ('财' not in fa and '财' not in ta):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if fp in cai_root_broken or tp in cai_root_broken:
            continue  # 财根被坏，做功为虚
        if t == '冲':
            cai_work = True
            chong_cai = True
        elif t in _HE_TYPES:
            zhu_f, zhu_t = _is_zhu_pos(fp), _is_zhu_pos(tp)
            for zc, oc, zc_zhu, oc_zhu, zc_pos in (
                    (fa, ta, zhu_f, zhu_t, fp), (ta, fa, zhu_t, zhu_f, tp)):
                if not zc_zhu:
                    continue
                # 功神不净：印/官杀；比劫在宾位端为夺，在日支端为日主坐根
                # （我之身，合制宾财=制财得财，同信号8《理象学》复例四判据）
                if {'印', '官杀'} & zc or ('比劫' in zc and zc_pos != 'day_zhi'):
                    continue
                if '财' in oc or ('财' in zc and oc_zhu):
                    cai_work = True
                    break
        else:  # 克/穿/刑/破：主位发动方为我得财之制
            if not _is_zhu_pos(fp):
                continue
            if qunbi_duocai and {'日主', '比劫', '财'} & fa:
                continue  # 群比夺财：争夺非经营
            cai_work = True
    if cai_work:
        score += 2
        ev.append('财星入局做功（经营之本）')
    # 2. 主位合财/制财做功 +2——段氏「财星明现 + 合财/制财做功，商人经营取财」。
    #    方向判据（段氏主宾论「我合/制他人之财方为己得」）：财须在宾位端
    #    （己财被宾合=财被合走/合绊，非我得），或日主自合财（财来就我）；
    #    主位功神端主气限 食伤/财/日主（印主文化、官杀合财非经营、比劫为夺）。
    he_or_zhi_cai = False
    for a in non_aux:
        t = a.get('type', '')
        if t not in _HE_TYPES and t not in _ZHI_TYPES:
            continue
        if _is_duocai(a):
            continue
        fi, ti, fa, ta = _act_cats(a)
        if fi < 0:
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if fp in cai_root_broken or tp in cai_root_broken:
            continue  # 财根被坏，做功为虚
        zhu_f, zhu_t = _is_zhu_pos(fp), _is_zhu_pos(tp)
        if t in _ZHI_TYPES:
            # 主制宾财：主位发动、财在宾位端、功神端主气净
            if zhu_f and not zhu_t and '财' in ta and not ({'印', '官杀', '比劫'} & fa):
                if qunbi_duocai and {'日主', '比劫'} & fa:
                    continue  # 群比夺财
                he_or_zhi_cai = True
                break
        elif t in _HE_TYPES:
            for zc, oc, zc_zhu, oc_zhu, zc_pos in (
                    (fa, ta, zhu_f, zhu_t, fp), (ta, fa, zhu_t, zhu_f, tp)):
                if not zc_zhu:
                    continue  # 须主位端参与
                if {'印', '官杀'} & zc or ('比劫' in zc and zc_pos != 'day_zhi'):
                    continue  # 主位功神端不净（日支坐根之比劫除外，同信号8判据）
                if '财' in oc:  # 主位功神合宾财（含日主合财干=财来就我）
                    he_or_zhi_cai = True
                    break
                if '财' in zc and oc_zhu:  # 日时互合，己财在坐下/门户
                    he_or_zhi_cai = True
                    break
            if he_or_zhi_cai:
                break
    if he_or_zhi_cai:
        score += 2
        ev.append('主位合财/制财做功（商人经营取财）')
    # 3. 食伤生财做功 +2——食伤柱与财柱联动，或生用「食伤」动作且财明现（贸易/生产）
    ss_cai = bool(_action_between_cats(non_aux, day_gan, gans, zhis, '食伤', '财',
                                       _HE_TYPES | _ZHI_TYPES))
    if not ss_cai and has_cai and has_shishang:
        ss_cai = any(a.get('type') == '食伤' for a in non_aux)
    if ss_cai:
        score += 2
        ev.append('食伤生财做功（贸易/生产）')
    # 4. 财印门户（开店，结构象保留）+1——K3 职业批1 收窄（首版教训修正）：
    #    旧版柱级 _pillar_cats 含藏干中气，时柱几乎必有财/印，泛触（教师/官命
    #    案全中，fp 26 例命中 25）。收窄为主气粒度（时干十神/时支本气），并保
    #    留食伤主气门户（以口为业兼营门面之象，书锚 yx-酒店丁未时/董竹君庚申
    #    时=食伤坐门户之真商人）；heldout 三书锚商人（ans10 戊申时主气财/
    #    li002 辛亥时主气印/li131 癸卯时主气印）主气命中，不受收窄影响。
    _hour_main = _main_qi_cats(day_gan, gans, zhis, 3)
    if {'财', '印'} & _hour_main or '食伤' in _hour_main:
        score += 1
        if {'财', '印'} & _hour_main:
            ev.append('财/印在时柱门户（开店）')
        else:
            ev.append('食伤在时柱门户（经营门面，以口为业兼营）')
    # 5. 官杀当财被制（大生意）+1
    if _has_cat(day_gan, gans, zhis, '官杀') and \
       _action_between_cats(non_aux, day_gan, gans, zhis, '官杀', '食伤', {'克'}):
        score += 1
        ev.append('官杀当财被制（大生意）')
    # 6. 冲财做功（贸易运输）+1
    if chong_cai:
        score += 1
        ev.append('冲财做功（贸易运输）')
    # 6a. 卯酉冲门户 +1（K3 职业批2 酒家门户象）：卯酉=门户（《中级》象法
    #     「卯酉为出入之门」），冲则门户大开迎客，配财在局=开店经营之象
    #     （书锚 cj-老板「卯酉冲酒家门户」开酒店）。与 lawyer「依律破例」
    #     同象异读：财主气在局者以商论。
    _n_cai_main_m = sum(1 for i in range(4)
                        if '财' in _main_qi_cats(day_gan, gans, zhis, i))
    if _n_cai_main_m >= 1 and any(
            a.get('type') in ('冲', '破')
            and _pos_idx(a.get('from_pos', '')) >= 0
            and _pos_idx(a.get('to_pos', '')) >= 0
            and frozenset({zhis[_pos_idx(a.get('from_pos', ''))],
                           zhis[_pos_idx(a.get('to_pos', ''))]}) == frozenset({'卯', '酉'})
            for a in non_aux):
        score += 1
        ev.append('卯酉冲门户（门户大开迎客，酒家/开店经营）')
    # 6b. 自坐财库 +1（结构辅证，同门户）——《高级》6.3「戌为火库，若局中火为
    #     财，则戌为财库，象意银行、金库、仓库」+ 案例七「财库包局，银行工作」：
    #     日支为日主财星之库（库 mapping 复用 objective.TOMB_MAP），坐下与财
    #     为伴，财藏库而旺者多以经营/金融成象。
    _day_zhi = zhis[PILLAR_KEYS.index('day')]
    _cai_wx = WX_KE.get(GAN_WX.get(day_gan, ''), '')
    if _cai_wx and _cai_wx in TOMB_MAP.get(_day_zhi, []):
        score += 1
        ev.append(f'自坐财库（{_day_zhi}为{_cai_wx}财之库，象意银行/金库）')
    # 7. 内食神格（办厂/生产经营）+2——段氏《高级》7.2「尤以内食神（地支食神）为典型，
    #    主企业内部生产、创造」「内食神格：地支食神做功，或食神生财，主实体企业、
    #    生产经营」（7.3 商人口诀：内食神格厂生产）。内食神=食神为地支本气且不透干
    #    （透干为外食神主口才技艺，不在此象）。
    if not any(_compute_shishen(day_gan, g) == '食神' for g in gans if g):
        inner = [z for z in zhis
                 if get_canggan_mangpai(z)
                 and _compute_shishen(day_gan, get_canggan_mangpai(z)[0][0]) == '食神']
        if inner:
            score += 2
            ev.append(f'内食神格（{"".join(inner)}藏食神本气不透，办厂/生产经营）')
    # 8. 坐根制财（制财得财）+2——《段氏理象学》复例四：「丁巳日之巳合制年上
    #    财星，卯木助巳火之力，地支是制财之功…下海经商，应巳申之合取财，发
    #    财数百万」。日支本气比劫=日主坐根（我之身，非宾位他人之劫——宾主
    #    论同 K3 富屋贫人主位比劫豁免），其 合/刑/穿/克 宾位财本气之支为
    #    主位制宾财之正格（夺财判据所排乃宾位比劫夺财与冲财争夺[子冲午类]，
    #    不排日主坐根之合制；冲不在此列，冲财仍归争夺）。
    _day_i = PILLAR_KEYS.index('day')
    _day_cg = get_canggan_mangpai(zhis[_day_i])
    if _day_cg and _cat(_compute_shishen(day_gan, _day_cg[0][0])) == '比劫':
        for a in non_aux:
            t = a.get('type', '')
            if t not in _HE_TYPES and t not in {'克', '刑', '穿', '破'}:
                continue
            fi, ti, fa, ta = _act_cats(a)
            if fi < 0:
                continue
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            if fp == 'day_zhi' and tp.endswith('_zhi') and not _is_zhu_pos(tp) \
                    and '财' in ta and tp not in cai_root_broken:
                score += 2
                ev.append('坐根制财（日支为根合制宾财，制财得财）')
                break
            if tp == 'day_zhi' and fp.endswith('_zhi') and not _is_zhu_pos(fp) \
                    and '财' in fa and fp not in cai_root_broken:
                score += 2
                ev.append('坐根制财（日支为根合制宾财，制财得财）')
                break
    # 五行行业（商人行业细分辅证，不作独立加分——金水既可会计数字亦可化工，
    # 须由其他商人信号定位）
    cnt = _wx_count(day_gan, gans, zhis)
    if cnt.get('金', 0) and cnt.get('水', 0):
        ev.append('金水→金融/物流/化工')
    if cnt.get('木', 0) and cnt.get('火', 0):
        ev.append('木火→文教/餐饮/家具')
    if cnt.get('土', 0) and cnt.get('金', 0):
        ev.append('土金→地产/建筑/矿')
    if cnt.get('火', 0) and cnt.get('土', 0):
        ev.append('火土→能源/化工/娱乐')
    return score, ev


def _score_military(day_gan, gans, zhis, wa, ss) -> Tuple[int, List[str]]:
    """军警/军阀/武职象：官杀成势 + 羊刃/灾煞 + 申酉金/辛 + 全阳。

    非常规职业命中路径（源文 7.3 五行行业+象法）：杀旺成势、七杀透干、羊刃灾煞
    并现、申酉金/辛律令兵刃，主军警/武职/权柄。与 juxiang 官杀包局/夹官/全阳互证。
    """
    score = 0
    ev: List[str] = []
    guansha_pillars = sum(1 for i in range(4) if '官杀' in _pillar_cats(day_gan, gans[i], zhis[i]))
    # 官杀成势方为武贵之基（仅 2 柱官杀不构成武势，避免火金相战类命局误入武职）
    if guansha_pillars >= 3:
        score += 2
        ev.append(f'官杀成势（{guansha_pillars}柱）=武贵/权柄之基')
    if any(_compute_shishen(day_gan, g) == '七杀' for g in gans if g):
        score += 1
        ev.append('七杀透干（肃杀/兵威）')
    if (ss.get('羊刃') or {}).get('in_pillars'):
        score += 1
        ev.append('羊刃（武斗/兵刃）')
    if (ss.get('灾煞') or {}).get('in_pillars'):
        score += 1
        ev.append('灾煞（凶险/非常之职）')
    if any(z in ('申', '酉') for z in zhis) or any(g == '辛' for g in gans):
        score += 1
        ev.append('申酉金/辛（律令/兵刃）')
    return score, ev


def _score_performer(day_gan, gans, zhis, wa, ss) -> Tuple[int, List[str]]:
    """演艺/演员象：食伤+桃花+财（色相求财）为主，丙丁火+桃花辅。

    非常规职业命中路径（源文 7.3 象法）：食伤+桃花主演艺/色情，配财为卖身/色相
    求财；桃花居夫妻宫（日柱）=色相入婚位。与 juxiang 食伤包局/换食伤象互证。
    """
    score = 0
    ev: List[str] = []
    has_shishang = _has_cat(day_gan, gans, zhis, '食伤')
    has_cai = _has_cat(day_gan, gans, zhis, '财')
    tao = ss.get('桃花') or {}
    has_tao = bool(tao.get('in_pillars'))
    tao_in_day = 'day' in (tao.get('in_pillars') or [])
    cnt = _wx_count(day_gan, gans, zhis)
    if has_shishang and has_tao and has_cai:
        score += 4
        ev.append('食伤+桃花+财（演艺/色情求财，卖身之象）')
    elif has_shishang and has_tao:
        score += 3
        ev.append('食伤+桃花（演艺之象）')
    if has_tao and has_cai:
        score += 1
        ev.append('桃花+财（色相求财）')
    if tao_in_day:
        score += 2
        ev.append('桃花居日柱夫妻宫（色相入婚位）')
    if '食伤' in _pillar_cats(day_gan, gans[3], zhis[3]):
        score += 1
        ev.append('食伤在时柱门户（以艺为业）')
    if has_tao and cnt.get('火', 0) >= 2:
        score += 1
        ev.append('丙丁火+桃花（声色演艺）')
    # 无桃花之艺 +3（K3 职业批1 新通道）：柱级食伤≥2柱成势 + 食伤参与做功
    # （主气当事人）+ 局无桃花 + 无明财（主气）——凭技艺立身之艺人。桃花作
    # 核心条件在本样本双向失败（fp 9 例全有桃花/真艺人 7 例全无桃花），桃花
    # 诸条款保留不动，另开无桃花通道（书锚：阿炳/帕瓦罗蒂/gj-影星合杀 皆
    # 食伤成势做功而无桃花；财明现者食伤生财归经营，不以艺论——famous-乔布斯
    # 豁免）。
    if not has_tao:
        n_ss_pillars = sum(1 for i in range(4)
                           if '食伤' in _pillar_cats(day_gan, gans[i], zhis[i]))
        cai_ming = any('财' in _main_qi_cats(day_gan, gans, zhis, i)
                       for i in range(4))
        ss_work = any(
            '食伤' in fa or '食伤' in ta
            for fa, ta in (_action_main_qi(a, day_gan, gans, zhis)
                           for a in wa if not a.get('auxiliary')))
        if n_ss_pillars >= 2 and ss_work and not cai_ming:
            score += 3
            ev.append('食伤成势做功（无桃花之艺，凭技艺立身）')
    # 金水声音 +4（K3 职业批2 歌坛通道）：日主为金 + 水食伤主气在局 + 食伤
    # 主气≥2柱 + 比劫主气≥3柱（身旺任泄）——象法金水相生主声音/歌喉（金=
    # 钟磬之声、水=婉转流动），身旺食伤泄秀者以声为业（书锚 cj-歌星：辛日
    # 三辛透干身旺、亥亥水伤成势）。金日主水食伤而身不旺者泄重不立（帕瓦罗蒂
    # 比劫1柱不触，归别象），非金日主之水食伤归文墨/技艺（梁羽生归鬻文）。
    if GAN_WX.get(day_gan) == '金':
        _n_ss_main = sum(1 for i in range(4)
                         if '食伤' in _main_qi_cats(day_gan, gans, zhis, i))
        _n_bj_main = sum(1 for i in range(4)
                         if '比劫' in _main_qi_cats(day_gan, gans, zhis, i))
        _shui_ss = False
        for i in range(4):
            if '食伤' not in _main_qi_cats(day_gan, gans, zhis, i):
                continue
            if gans[i] and _cat(_compute_shishen(day_gan, gans[i])) == '食伤' \
                    and GAN_WX.get(gans[i]) == '水':
                _shui_ss = True
                break
            _cg = get_canggan_mangpai(zhis[i])
            if _cg and _cat(_compute_shishen(day_gan, _cg[0][0])) == '食伤' \
                    and ZHI_WX.get(zhis[i]) == '水':
                _shui_ss = True
                break
        if _shui_ss and _n_ss_main >= 2 and _n_bj_main >= 3:
            score += 4
            ev.append('金水声音（金水伤官身旺泄秀，以歌喉/声音为业）')
    return score, ev


# ───────────────────── 聚合 ─────────────────────

_CAREER_LABELS = {
    'accountant': '会计/财务',
    'doctor': '医生/医疗',
    'teacher': '教师/教育',
    'lawyer': '律师/法务/公检法',
    'merchant': '商人/经营',
    'military': '军警/军阀/武职',
    'performer': '演艺/演员',
}

# M2 基础职业类目（七桶未成象时的第二梯队，段氏《中级》体力取财）
_BASE_CAREER_LABELS = {
    'laborer': '农民/工人·体力劳动者',
    'unemployed': '无业',
}

_HE_TYPES: Set[str] = {'天干合', '地支合', '暗合', '半合'}
_ZHI_TYPES: Set[str] = {'冲', '克', '穿', '刑', '破'}
# 田土（农）/ 金机器（工）细分提示
_TU_ZHIS: Set[str] = {'丑', '辰', '未', '戌'}
_JIN_ZHIS: Set[str] = {'申', '酉'}


def _classify_base_career(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    wa: List[Dict],
    caiming_result: Optional[Dict],
    direction: Optional[Dict],
) -> Dict:
    """基础职业类目判定（七桶未成象时的第二梯队）。

    段氏《中级》取财方法·体力取财：「体力取财做功之神应是比肩、劫财与禄神」，
    做功效率低者属「八亿的农民与民工」阶层。判定：
      - 无业（unemployed）：清家荡产（比劫夺财 severe 且 tier 贫）；或贫而全局
        无做功；或用神被坏+贫且无体力做功（段氏第50期「用神被坏则是被迫离职
        下岗」）；
      - 体力劳动者（laborer）：财命贫/小康 + 比劫参与做功（各类动作两端皆算
        「参与」，《中级》「官合劫财为制劫财…劫财参与做功，所以是体力劳动者」）
        或禄神当财，且无工薪/经营/风险路径、非反局。细分提示：田土（丑辰未戌）
        参与做功→农，金（申酉）参与→工（机器）。

    Returns:
        {} 或 {'bucket': 'laborer'|'unemployed', 'hint': '农'|'工'|'',
               'evidence': [str]}
    """
    ds = direction or {}
    cm = caiming_result or {}
    tier = cm.get('tier', '')
    views = (cm.get('caifu_view') or {}).get('views') or []
    methods = (cm.get('qucai_method') or {}).get('methods') or []
    non_aux = [a for a in wa if not a.get('auxiliary')]

    # ── 无业（unemployed）──
    # 清家荡产（比劫夺财 severe 且tier贫=荡产至贫，乞丐口径）或贫而全局无做功；
    # 用神被坏+贫（段氏第50期「下岗或辞职者都是月令之官印出了问题…用神被坏则
    # 是被迫离职下岗」）且无体力做功者，判无业（有体力活干者落 laborer）。
    pocai_severe_pin = ds.get('pocai_severe') and tier == '贫'
    if pocai_severe_pin:
        return {'bucket': 'unemployed', 'hint': '',
                'evidence': ['严重破财凶向且荡产至贫（' + '；'.join(ds.get('reasons') or [])[:40]
                             + '），无业']}

    # 比劫参与做功（段氏：体力取财做功之神应是比肩、劫财与禄神——「参与」含被合制，
    # 《中级》「官合劫财为制劫财…劫财参与做功，所以是体力劳动者」，故各类动作两端皆算）
    bijiao_work = False
    work_zhis: Set[str] = set()
    for a in non_aux:
        t = a.get('type', '')
        if t not in _HE_TYPES and t not in _ZHI_TYPES:
            continue
        for pos in (a.get('from_pos', ''), a.get('to_pos', '')):
            i = _pos_idx(pos)
            if i < 0:
                continue
            work_zhis.add(zhis[i])
            if '比劫' in _pillar_cats(day_gan, gans[i], zhis[i]):
                bijiao_work = True

    if tier == '贫' and not non_aux:
        return {'bucket': 'unemployed', 'hint': '',
                'evidence': ['财命贫且全局无做功，无业']}
    if (tier == '贫' and not bijiao_work and ds.get('yongshen_xiong')):
        return {'bucket': 'unemployed', 'hint': '',
                'evidence': ['用神被坏+贫（段氏：用神被坏则被迫离职下岗），无业']}

    # ── 体力劳动者（农/工）──
    # 反局命局为非常态（格局破），不适用正常职业取象，回未分类。
    if ds.get('fanju'):
        return {}
    if tier not in ('贫', '小康'):
        return {}
    if {'工薪', '经营', '风险'} & set(methods):
        return {}
    lu_tili = '禄神当财' in views
    # 富屋贫人（段氏高级篇「身弱财旺…反为财所累」，《中级》「富屋贫人，干体力活
    # 维生，实际是个宾馆服务员」）：身弱扶抑 + 财多（≥2位明现）+ tier 贫 -> 体力。
    fuwu_pinren = False
    if tier == '贫':
        try:
            from mangpai.subjective.yongshen import classify_strength
            if str(classify_strength(day_gan, gans, zhis)) == '身弱':
                fuwu_pinren = (cm.get('caifu_view') or {}).get('cai_count', 0) >= 2
        except Exception:
            pass
    if not (bijiao_work or lu_tili or fuwu_pinren):
        return {}
    hint = '农' if work_zhis & _TU_ZHIS else ('工' if work_zhis & _JIN_ZHIS else '农')
    ev: List[str] = []
    if bijiao_work:
        ev.append('功神含比劫（段氏：体力取财做功之神应是比肩、劫财与禄神）')
    if lu_tili:
        ev.append('禄神当财，身体力行体力取财')
    if fuwu_pinren:
        ev.append('身弱财旺，富屋贫人（段氏：干体力活维生）')
    ev.append(f'财命{tier}，做功效率低（农民与民工阶层）')
    return {'bucket': 'laborer', 'hint': hint, 'evidence': ev}


def classify_zhiye(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
    caiming_result: Optional[Dict] = None,
) -> Dict:
    """职业象法七类打分定位（多象定一象）。

    消费 xiangfa_ops.analyze_xiangfa_ops 的合象/换象/局象作互证：
      换官象/官杀包局/全阳/夹官→律师/公门/军职加权，换财象→商人加权，
      换食伤象/食伤包局→演艺/医生/教师加权（食伤包局配官杀→公检法）。
    消费 objective.xiangfa.get_liushi_ganzhi_xiang 的 person 字段（六十干支组合象
    行业象，如辛酉→法律/外科、戊戌→教师、甲申→交警/司法）作辅证。
    yunfan_result: 「当前运岁」反局切片（yunfan.current_fan_slice 产出，A1），
      军警 gating 的凶向信号源之一（与原局反局同链）。
    caiming_result: 财命综合结果（M2 基础职业类目消费 tier/取财法/财看法；
      缺省时于七桶未成象的 fallback 区自调 analyze_caiming）。

    Returns:
        {
          'scores': {career: int}, 'evidence': {career: [str]},
          'liushi_hints': [str], 'xiangfa_corroborate': [str],
          'primary': str, 'primary_label': str, 'desc': str,
          'hint_bucket': str, 'hint_label': str,  # 未分类时的最高分桶提示
          'base_career': {...},                    # M2 基础职业类目命中（laborer/unemployed）
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {
            'primary': '', 'primary_label': '', 'desc': '四柱不全，无法定位职业',
            'fallback_no_clear': False, 'min_score_threshold': _MIN_SCORE_THRESHOLD,
        }

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    try:
        ss = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        ss = {}

    scores: Dict[str, int] = {}
    evidence: Dict[str, List[str]] = {}

    s, e = _score_accountant(day_gan, gans, zhis, wa, muku)
    scores['accountant'], evidence['accountant'] = s, e
    s, e = _score_doctor(day_gan, gans, zhis, wa, ss)
    scores['doctor'], evidence['doctor'] = s, e
    s, e = _score_teacher(day_gan, gans, zhis, wa, ss)
    scores['teacher'], evidence['teacher'] = s, e
    s, e = _score_lawyer(day_gan, gans, zhis, wa)
    scores['lawyer'], evidence['lawyer'] = s, e
    s, e = _score_merchant(day_gan, gans, zhis, wa)
    scores['merchant'], evidence['merchant'] = s, e
    s, e = _score_military(day_gan, gans, zhis, wa, ss)
    scores['military'], evidence['military'] = s, e
    s, e = _score_performer(day_gan, gans, zhis, wa, ss)
    scores['performer'], evidence['performer'] = s, e

    # 羊刃驾杀武职通道 +3（K3 职业批1 真军警 fn 侧）：成势门「官杀柱级≥3」
    # 在金标军警上召回仅 2/8（蒋介石/公安/刑警等 2 柱官杀够不着门）。段氏
    # 杀刃相制=武权：官杀主气≥2柱 + 阳刃在局 + 刃支与官杀主气端有制/合动作
    # （刃无官杀动作=闲刃，reg67-合例一富命之子刃穿未官…实以财做功主象，
    # 财星入局做功触发者杀刃以商战论，豁免）；已成势（柱级≥3）者不重复加。
    _n_gs_main = sum(1 for i in range(4)
                     if '官杀' in _main_qi_cats(day_gan, gans, zhis, i))
    _yr = ss.get('羊刃') or {}
    _ren_zhis = {z for z in zhis if z in (_yr.get('zhi_all') or [])}
    if (_n_gs_main >= 2 and _ren_zhis
            and not any('官杀成势' in ln for ln in evidence.get('military', []))
            and not any('财星入局做功' in ln for ln in evidence.get('merchant', []))):
        _jia_sha = False
        for a in wa:
            if a.get('auxiliary'):
                continue
            for pos, other in ((a.get('from_pos', ''), a.get('to_pos', '')),
                               (a.get('to_pos', ''), a.get('from_pos', ''))):
                i, j = _pos_idx(pos), _pos_idx(other)
                if i < 0 or j < 0 or not pos.endswith('_zhi') \
                        or zhis[i] not in _ren_zhis:
                    continue
                if '官杀' in _main_qi_cats(day_gan, gans, zhis, j):
                    _jia_sha = True
                    break
            if _jia_sha:
                break
        if _jia_sha:
            scores['military'] = scores.get('military', 0) + 3
            evidence['military'] = evidence.get('military', []) + [
                '羊刃驾杀（杀刃相制=武权，刃与官杀有制合动作）']

    # 六十干支组合象 person 辅证
    liushi_hints: List[str] = []
    for i in range(4):
        gz = (gans[i] or '') + (zhis[i] or '')
        if len(gz) == 2:
            info = get_liushi_ganzhi_xiang(gz)
            person = info.get('person', '') if info else ''
            if person:
                liushi_hints.append(f'{PILLAR_NAMES_CN[i]}柱{gz}：{person}')

    # xiangfa_ops 局象/换象互证（加权）——非常规职业（军警/演艺/公检法）命中路径
    # K3 职业批1：互证加权每桶封顶 +2（换象/包局/夹官/全阳逐条 +1/+2 无上限
    # 堆叠把非军警命推过阈值——yx-导演 military 9 中 corro 占 5、gj-煤矿 9 占 5、
    # reg67-申机器工人 lawyer 8 占 4；真军警反而 0-5 分覆没，corro 虚高是
    # military/lawyer fp/fn 倒置之源）。
    corroborate: List[str] = []
    _corro_adds: Dict[str, int] = {}

    def _corro(bucket: str, n: int) -> None:
        _corro_adds[bucket] = _corro_adds.get(bucket, 0) + n

    try:
        from mangpai.subjective.xiangfa_ops import analyze_xiangfa_ops
        xo = analyze_xiangfa_ops(day_gan, gans, zhis, relations=rel, muku_result=muku,
                                 shensha_result=ss)
        has_guansha = _has_cat(day_gan, gans, zhis, '官杀')
        has_cai = _has_cat(day_gan, gans, zhis, '财')
        has_tao = bool((ss.get('桃花') or {}).get('in_pillars'))
        # 换象（制尽则换）：换官象→律师/公门/军职，换财象→商人，换食伤象→演艺/医生/教师
        for f in (xo.get('huanxiang') or []):
            dom = f.get('domain', '')
            if dom in ('官权', '官杀'):
                _corro('lawyer', 1)
                _corro('military', 1)
                corroborate.append(f'换官象→律师/公门/军职加权（{f.get("desc","")[:20]}）')
            elif dom in ('财',):
                _corro('merchant', 1)
                corroborate.append(f'换财象→商人加权（{f.get("desc","")[:20]}）')
            elif dom in ('食艺', '食伤'):
                _corro('performer', 1)
                _corro('doctor', 1)
                _corro('teacher', 1)
                corroborate.append(f'换食伤象→演艺/医生/教师加权（{f.get("desc","")[:20]}）')
        # 局象（全局氛围象）：官杀包局/全阳/夹官→军职公门，食伤包局→演艺(配官杀→执法)
        jia_guan = 0
        for f in (xo.get('juxiang') or []):
            t = f.get('type', '')
            dom = f.get('domain', '')
            qx = f.get('qi_xiang', '')
            if t == '包局':
                if dom == '官杀':
                    _corro('military', 2)
                    _corro('lawyer', 1)
                    corroborate.append('官杀包局→军职/公门加权')
                elif dom == '财':
                    _corro('merchant', 1)
                elif dom == '食伤':
                    _corro('performer', 1)
                    if has_guansha:
                        _corro('lawyer', 1)  # 食伤制官=执法/公检法
                    if has_cai or has_tao:
                        _corro('performer', 1)
                elif dom == '印':
                    _corro('teacher', 1)
            elif t == '全阳':
                _corro('military', 1)
                corroborate.append('全阳之局→刚烈武职加权')
            elif t == '夹局' and '官' in qx:
                jia_guan += 1
            elif t == '专旺' and dom == '官杀':
                _corro('military', 1)
        if jia_guan:
            _corro('military', 1)
            _corro('lawyer', 1)
            corroborate.append(f'夹官局→军职/公门加权（{jia_guan}处）')
        if xo.get('hexiang'):
            corroborate.append(f'合象{len(xo["hexiang"])}处（产新象印证组合）')
    except Exception:
        pass
    for _b, _n in _corro_adds.items():
        scores[_b] = scores.get(_b, 0) + min(_n, 2)
        if _n > 2:
            corroborate.append(f'{_b}互证加权{_n}封顶+2（防堆叠虚高）')

    # 军警/武职 gating（P0 B/C + M1）：军警为官命之武职，反局/比劫夺财破财
    # /忌神制用神(R2)/用神被合绊(R3) 等凶向命中者不得判武职（坐牢的、破财的、
    # 乞丐不开军警车）。须置于象法互证加权之后，方不被全阳/夹官等再加分覆盖。
    # 凶向信号缺省自调（laoyu 过火不计入）。
    # 岁运反局（A1）经 yunfan_result 透传，与原局反局同链 gating。
    # M2：ds 提前算好，同时供基础职业类目（无业/体力劳动者）消费。
    try:
        ds = assess_direction_signals(
            day_gan, gans, zhis, relations=rel,
            yunfan_result=yunfan_result,
        )
    except Exception:
        ds = {}
    if ds.get('fanju') or ds.get('pocai') or ds.get('guohe_pocai') \
            or ds.get('yongshen_xiong') or ds.get('mingju_xiong'):
        if scores.get('military', 0) > 0:
            gate = '军警gating（凶向：' + '；'.join(ds.get('reasons') or []) + '）'
            scores['military'] = 0
            evidence['military'] = [gate]
    # lawyer gating（K3 职业批1）：伤官见官为忌破格（mingju_xiong）者不以律师
    # 成象——伤官制官为用方主辩护对抗，为忌则破格困顿/官非（书锚 gj-低保伤官
    # 「土金伤官怕见官…靠低保维生」：与律师同形而吉凶相反）。
    if ds.get('mingju_xiong') and scores.get('lawyer', 0) > 0:
        gate = 'lawyer gating（伤官见官为忌破格主困顿，不以律师成象：' \
            + '；'.join(ds.get('reasons') or []) + '）'
        scores['lawyer'] = 0
        evidence['lawyer'] = [gate]
    # merchant gating（P0-c）：严重破财凶向（比劫夺财 severe=清家荡产/乞丐级）
    # 命局不以经营成象——其「财做功」为夺财交战而非经营取财（段氏制财得财以
    # 功神非比劫为前提）；一般破财（normal）之经商者不在此限（破财的商人仍是商人）。
    if ds.get('pocai_severe') and scores.get('merchant', 0) > 0:
        gate = 'merchant gating（严重破财凶向不以经营成象：' \
            + '；'.join(ds.get('reasons') or []) + '）'
        scores['merchant'] = 0
        evidence['merchant'] = [gate]
    # 富屋贫人 gating（P0-c）：身弱 + 财明现≥2位 + 无印生身任财——段氏「身弱
    # 财旺：非但不能得财，反为财所累…富屋贫人，干体力活维生」，此类命合财/制财
    # 做功为财所累之象而非经营之能，不以商人成象（有印生身任财者不在此限）。
    # K3：主位比劫帮身者豁免——段氏宾主论：主位（日/时柱）比劫=自家人帮身
    # 任财（财多身弱，比劫帮身为福），宾位比劫=他人竞争者不帮身。富屋贫人以
    # 「身弱无主位帮扶不能任财」为前提（qi14 亿万企业家：日支寅禄帮身，财3位
    # 而富；b67-初中：比劫全在宾位年柱，仍为富屋贫人）。
    if scores.get('merchant', 0) > 0:
        try:
            from mangpai.subjective.yongshen import classify_strength as _cs
            _strength = str(_cs(day_gan, gans, zhis))
        except Exception:
            _strength = ''
        _cai_cnt = sum(1 for i in range(4)
                       if '财' in _pillar_cats(day_gan, gans[i], zhis[i]))
        _has_yin = _has_cat(day_gan, gans, zhis, '印')
        _has_bijiao = False
        for _i in (PILLAR_KEYS.index('day'), PILLAR_KEYS.index('hour')):
            _cats = _pillar_cats(day_gan, gans[_i], zhis[_i])
            if PILLAR_KEYS[_i] == 'day':
                _cats = _cats - {_cat(_compute_shishen(day_gan, gans[_i]))}  # 日干自身不算帮身
            if '比劫' in _cats:
                _has_bijiao = True
                break
        if _strength == '身弱' and _cai_cnt >= 2 and not _has_yin and not _has_bijiao:
            gate = (f'merchant gating（身弱财旺{_cai_cnt}位无印无比劫任财，富屋贫人——'
                    f'段氏：干体力活维生，不为商）')
            scores['merchant'] = 0
            evidence['merchant'] = [gate]

    # 多象定一象：取最高分。同分决胜（K3，段氏 7.3 总则「先定取财方式：先断其
    # 属于经营、风险、智力、体力、工薪中哪一类…再精确定位」+ 引言「象法为宗」）：
    #   非常规象（performer/military，桃花/羊刃神煞驱动，象法最切）> 取财方式层
    #   （merchant=经营取财）> 行业桶（accountant/doctor/teacher/lawyer，保持原序）。
    _tie_pri = ('performer', 'military', 'merchant', 'accountant', 'doctor',
                'teacher', 'lawyer')
    primary = max(scores, key=lambda k: (scores[k], -_tie_pri.index(k))) if scores else ''
    top_score = scores[primary] if scores else 0
    # 最低分阈值：最高分低于阈值时各桶均为弱信号共现、不足成象，fallback
    # 「无明确职业倾向」而非硬塞最像的一桶（乞丐/坐牢/破财等非标命局）。
    fallback_no_clear = bool(scores) and top_score < _MIN_SCORE_THRESHOLD
    hint_bucket = primary if (fallback_no_clear and primary) else ''
    hint_label = _CAREER_LABELS.get(hint_bucket, '')
    base_career: Dict = {}
    if fallback_no_clear or top_score == 0:
        primary = ''
        # M2 基础职业类目：行业七桶未成象时，按取财方式+效率落 体力劳动者/无业
        # （段氏《中级》体力取财=比劫/禄神做功+效率低=农民民工阶层）。
        # fallback 由「无明确职业倾向」升格为合法第一输出：基础类目命中给类目，
        # 未命中给「未分类」+ 最高分桶提示（hint），不再硬塞七桶。
        cm = caiming_result
        if cm is None:
            try:
                from mangpai.subjective.caiming import analyze_caiming
                cm = analyze_caiming(day_gan, gans, zhis, relations=rel,
                                     shensha_result=ss, yunfan_result=yunfan_result)
            except Exception:
                cm = {}
        base_career = _classify_base_career(day_gan, gans, zhis, wa, cm, ds)
        if base_career:
            primary = base_career['bucket']
            hint_bucket, hint_label = '', ''  # 已落基础类目，不再给七桶提示

    if primary in _BASE_CAREER_LABELS:
        primary_label = _BASE_CAREER_LABELS[primary]
        if base_career.get('hint'):
            primary_label += f'（象提示：偏{base_career["hint"]}）'
    elif fallback_no_clear or top_score == 0:
        primary_label = '未分类'
    else:
        primary_label = _CAREER_LABELS.get(primary, '')

    desc = f'职业定位：{primary_label or "未明"}'
    if primary and primary in _BASE_CAREER_LABELS and base_career.get('evidence'):
        desc += '（' + '、'.join(base_career['evidence'][:3]) + '）'
    elif primary and evidence.get(primary):
        desc += '（' + '、'.join(evidence.get(primary, [])[:3]) + '）'
    elif fallback_no_clear:
        desc += (f'（各桶最高分{top_score}<{_MIN_SCORE_THRESHOLD}，弱信号共现不足成象'
                 + (f'；倾向参考：{hint_label}' if hint_label else '') + '）')

    return {
        'scores': scores,
        'evidence': evidence,
        'liushi_hints': liushi_hints,
        'xiangfa_corroborate': corroborate,
        'primary': primary,
        'primary_label': primary_label,
        'hint_bucket': hint_bucket,      # 未分类时的最高分桶提示（M2）
        'hint_label': hint_label,
        'base_career': base_career,      # M2 基础职业类目命中（laborer/unemployed）
        'fallback_no_clear': fallback_no_clear,
        'min_score_threshold': _MIN_SCORE_THRESHOLD,
        'desc': desc,
    }


def analyze_zhiye(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
    caiming_result: Optional[Dict] = None,
) -> Dict:
    """职业象法综合（analyze_zhiye = classify_zhiye 的对外别名）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    shensha_result: engine 透传的神煞结果，优先用传入值、缺省才就地重算。
    yunfan_result: 「当前运岁」反局切片（A1），军警 gating 凶向信号源。
    caiming_result: 财命综合结果（M2 基础职业类目消费），缺省 fallback 区自调。
    """
    return classify_zhiye(day_gan, gans, zhis, relations=relations,
                          shensha_result=shensha_result,
                          yunfan_result=yunfan_result,
                          caiming_result=caiming_result)


__all__ = [
    'classify_zhiye',
    'analyze_zhiye',
]
