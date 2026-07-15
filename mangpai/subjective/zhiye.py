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
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
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


def _pos_idx(pos: str) -> int:
    k = pos.split('_')[0]
    return PILLAR_KEYS.index(k) if k in PILLAR_KEYS else -1


def _action_between_cats(
    wa: List[Dict], day_gan: str, gans: List[str], zhis: List[str],
    cat_a: str, cat_b: str, types: Set[str],
) -> List[Dict]:
    """两十神大类柱之间的指定类型动作（双向）。"""
    out: List[Dict] = []
    for a in wa:
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


def _score_teacher(day_gan, gans, zhis, wa) -> Tuple[int, List[str]]:
    score = 0
    ev: List[str] = []
    cnt = _wx_count(day_gan, gans, zhis)
    # 木火通明
    if cnt.get('木', 0) >= 1 and cnt.get('火', 0) >= 1:
        score += 2
        ev.append('木火通明（文象）')
    # 食伤在门户（时柱）
    if '食伤' in _pillar_cats(day_gan, gans[3], zhis[3]):
        score += 2
        ev.append('食伤在时柱门户（以口为业）')
    # 印星月令为用
    if '印' in _pillar_cats(day_gan, gans[1], zhis[1]):
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
    # 伤官制官/伤官见官
    if _action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'}):
        score += 2
        ev.append('伤官制官（辩护对抗）')
    elif _has_cat(day_gan, gans, zhis, '食伤') and _has_cat(day_gan, gans, zhis, '官杀'):
        score += 1
        ev.append('伤官见官')
    # 食神制官
    if any(_compute_shishen(day_gan, g) == '食神' for g in gans if g) and \
       _has_cat(day_gan, gans, zhis, '官杀'):
        score += 1
        ev.append('食神制官（条文制规则）')
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
    score = 0
    ev: List[str] = []
    # 财星做功
    if _has_cat(day_gan, gans, zhis, '财'):
        score += 1
        ev.append('财星做功')
    # 财印门户（开店）
    portal_cats = _pillar_cats(day_gan, gans[3], zhis[3])
    if '财' in portal_cats or '印' in portal_cats:
        score += 1
        ev.append('财/印在时柱门户（开店）')
    # 食伤生财
    if _has_cat(day_gan, gans, zhis, '食伤') and _has_cat(day_gan, gans, zhis, '财'):
        score += 1
        ev.append('食伤生财（贸易/生产）')
    # 相冲做功（运输）
    if any(a.get('type') == '冲' for a in wa):
        score += 1
        ev.append('相冲做功（贸易运输）')
    # 官杀当财被制
    if _has_cat(day_gan, gans, zhis, '官杀') and \
       _action_between_cats(wa, day_gan, gans, zhis, '官杀', '食伤', {'克'}):
        score += 1
        ev.append('官杀当财被制（大生意）')
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


def classify_zhiye(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """职业象法七类打分定位（多象定一象）。

    消费 xiangfa_ops.analyze_xiangfa_ops 的合象/换象/局象作互证：
      换官象/官杀包局/全阳/夹官→律师/公门/军职加权，换财象→商人加权，
      换食伤象/食伤包局→演艺/医生/教师加权（食伤包局配官杀→公检法）。
    消费 objective.xiangfa.get_liushi_ganzhi_xiang 的 person 字段（六十干支组合象
    行业象，如辛酉→法律/外科、戊戌→教师、甲申→交警/司法）作辅证。

    Returns:
        {
          'scores': {career: int}, 'evidence': {career: [str]},
          'liushi_hints': [str], 'xiangfa_corroborate': [str],
          'primary': str, 'primary_label': str, 'desc': str,
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
    s, e = _score_teacher(day_gan, gans, zhis, wa)
    scores['teacher'], evidence['teacher'] = s, e
    s, e = _score_lawyer(day_gan, gans, zhis, wa)
    scores['lawyer'], evidence['lawyer'] = s, e
    s, e = _score_merchant(day_gan, gans, zhis, wa)
    scores['merchant'], evidence['merchant'] = s, e
    s, e = _score_military(day_gan, gans, zhis, wa, ss)
    scores['military'], evidence['military'] = s, e
    s, e = _score_performer(day_gan, gans, zhis, wa, ss)
    scores['performer'], evidence['performer'] = s, e

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
    corroborate: List[str] = []
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
                scores['lawyer'] = scores.get('lawyer', 0) + 1
                scores['military'] = scores.get('military', 0) + 1
                corroborate.append(f'换官象→律师/公门/军职加权（{f.get("desc","")[:20]}）')
            elif dom in ('财',):
                scores['merchant'] = scores.get('merchant', 0) + 1
                corroborate.append(f'换财象→商人加权（{f.get("desc","")[:20]}）')
            elif dom in ('食艺', '食伤'):
                scores['performer'] = scores.get('performer', 0) + 1
                scores['doctor'] = scores.get('doctor', 0) + 1
                scores['teacher'] = scores.get('teacher', 0) + 1
                corroborate.append(f'换食伤象→演艺/医生/教师加权（{f.get("desc","")[:20]}）')
        # 局象（全局氛围象）：官杀包局/全阳/夹官→军职公门，食伤包局→演艺(配官杀→执法)
        jia_guan = 0
        for f in (xo.get('juxiang') or []):
            t = f.get('type', '')
            dom = f.get('domain', '')
            qx = f.get('qi_xiang', '')
            if t == '包局':
                if dom == '官杀':
                    scores['military'] = scores.get('military', 0) + 2
                    scores['lawyer'] = scores.get('lawyer', 0) + 1
                    corroborate.append('官杀包局→军职/公门加权')
                elif dom == '财':
                    scores['merchant'] = scores.get('merchant', 0) + 1
                elif dom == '食伤':
                    scores['performer'] = scores.get('performer', 0) + 1
                    if has_guansha:
                        scores['lawyer'] = scores.get('lawyer', 0) + 1  # 食伤制官=执法/公检法
                    if has_cai or has_tao:
                        scores['performer'] = scores.get('performer', 0) + 1
                elif dom == '印':
                    scores['teacher'] = scores.get('teacher', 0) + 1
            elif t == '全阳':
                scores['military'] = scores.get('military', 0) + 1
                corroborate.append('全阳之局→刚烈武职加权')
            elif t == '夹局' and '官' in qx:
                jia_guan += 1
            elif t == '专旺' and dom == '官杀':
                scores['military'] = scores.get('military', 0) + 1
        if jia_guan:
            scores['military'] = scores.get('military', 0) + 1
            scores['lawyer'] = scores.get('lawyer', 0) + 1
            corroborate.append(f'夹官局→军职/公门加权（{jia_guan}处）')
        if xo.get('hexiang'):
            corroborate.append(f'合象{len(xo["hexiang"])}处（产新象印证组合）')
    except Exception:
        pass

    # 军警/武职 gating（P0 B/C）：军警为官命之武职，反局/比劫夺财破财等凶向
    # 命中者不得判武职（坐牢的、破财的、乞丐不开军警车）。须置于象法互证加权
    # 之后，方不被全阳/夹官等再加分覆盖。凶向信号缺省自调（laoyu 过火不计入）。
    try:
        ds = assess_direction_signals(
            day_gan, gans, zhis, relations=rel,
        )
        if ds.get('fanju') or ds.get('pocai') or ds.get('guohe_pocai'):
            if scores.get('military', 0) > 0:
                gate = '军警gating（凶向：' + '；'.join(ds.get('reasons') or []) + '）'
                scores['military'] = 0
                evidence['military'] = [gate]
    except Exception:
        pass

    # 多象定一象：取最高分
    primary = max(scores, key=lambda k: scores[k]) if scores else ''
    top_score = scores[primary] if scores else 0
    # 最低分阈值：最高分低于阈值时各桶均为弱信号共现、不足成象，fallback
    # 「无明确职业倾向」而非硬塞最像的一桶（乞丐/坐牢/破财等非标命局）。
    fallback_no_clear = bool(scores) and top_score < _MIN_SCORE_THRESHOLD
    if fallback_no_clear or top_score == 0:
        primary = ''
    primary_label = '无明确职业倾向' if fallback_no_clear else _CAREER_LABELS.get(primary, '')

    desc = f'职业定位：{primary_label or "未明"}'
    if primary and evidence.get(primary):
        desc += '（' + '、'.join(evidence.get(primary, [])[:3]) + '）'
    elif fallback_no_clear:
        desc += f'（各桶最高分{top_score}<{_MIN_SCORE_THRESHOLD}，弱信号共现不足成象）'

    return {
        'scores': scores,
        'evidence': evidence,
        'liushi_hints': liushi_hints,
        'xiangfa_corroborate': corroborate,
        'primary': primary,
        'primary_label': primary_label,
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
) -> Dict:
    """职业象法综合（analyze_zhiye = classify_zhiye 的对外别名）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    shensha_result: engine 透传的神煞结果，优先用传入值、缺省才就地重算。
    """
    return classify_zhiye(day_gan, gans, zhis, relations=relations,
                          shensha_result=shensha_result)


__all__ = [
    'classify_zhiye',
    'analyze_zhiye',
]
