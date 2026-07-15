"""
laoyu - 盲派牢狱专辑·主观层（subjective）

理论来源：段建业《盲派中级命理学》第十二章「牢狱专辑」（源文 5578-5870 行）
核心思想：牢狱之灾有五大看法，命中占其一即有牢狱之象，占多者灾重：

  1. 牢狱字：亥水、丑土、辰土为十二地支中之阴支，有牢狱象。
     阳性有用的东西被这些坏了 -> 牢狱；阳制阴不为牢狱。
  2. 水多金沉：金见水沉为牢狱。
  3. 枭神夺食：食伤为重要做功之神，被枭神克夺 -> 失去自由坐牢。
  4. 劫财+伤官：劫财伤官组合主结伙违法，再与官杀对抗必为牢狱（比劫伤官怕见官）。
  5. 反局+辰丑：凡出现反局，且辰、丑等字在局中 -> 多数应牢狱。

附加犯罪特征：
  - 伤官与官杀不和（想法做法与法律冲突）
  - 七杀夹制日主 / 七杀无制（犯罪结构）
  - 小偷：劫财为手、官为盗贼，劫财与官在主位组合 -> 小偷

出狱：日主得禄之年 / 日主合出冲出之年 / 牢狱为库则冲穿坏库出狱。

消费关系：
  - objective.zuogong_detect.detect_relations（刑冲穿害、合、做功）
  - objective.constants（五行生克、藏干、LU 禄表）
  - subjective.zhengfan.analyze_zhengfan（反局判定）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
置信度：中（牢狱五法为段氏主流归纳，旺衰/对抗阈值为启发式）。
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME, TOMB_MAP, CANG_GAN_MANGPAI,
    LU, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.objective.shensha import compute_shensha_ext
from mangpai.subjective.zhengfan import analyze_zhengfan

_YANG_GANS = set('甲丙戊庚壬')

# 牢狱字（阴地支）
_LAOYU_ZI: Set[str] = {'亥', '丑', '辰'}

# 阳干阳支（用于判定阳制阴 / 阴灭阳）
_YANG_GAN_SET = set('甲丙戊庚壬')
_YANG_ZHI_SET = {'子', '寅', '辰', '午', '申', '戌'}  # 顺序阳支
# 注意：辰虽阳支序，但段氏将辰归牢狱字（阴湿土）。此处阳支判定以五行/象论。
# 段氏「阳制阴不为牢狱」之「阴」专指 亥/丑/辰 牢狱字，故阳制阴=制去牢狱字，反而不主牢狱。

# 魁罡四日（庚辰、壬辰、庚戌、戊戌）——段氏魁罡主性刚毅、好斗，逢刑冲官杀主官非牢狱
_KUIGANG_DAYS: Set[Tuple[str, str]] = {('庚', '辰'), ('壬', '辰'), ('庚', '戌'), ('戊', '戌')}


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


def _mingxian_cats(day_gan: str, gans: List[str], zhis: List[str]) -> List[Set[str]]:
    """逐柱明现十神大类（天干+本/中气，余气不计）。"""
    out: List[Set[str]] = []
    for i in range(4):
        cats: Set[str] = set()
        if i < len(gans) and gans[i]:
            c = _cat(_compute_shishen(day_gan, gans[i]))
            if c:
                cats.add(c)
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break
                c = _cat(_compute_shishen(day_gan, cg))
                if c:
                    cats.add(c)
        out.append(cats)
    return out


def _has_shen_in_mingxian(day_gan: str, gans: List[str], zhis: List[str],
                          target_ss: Set[str]) -> bool:
    """天干或藏干本/中气是否含目标十神（明现）。"""
    for i in range(4):
        if i < len(gans) and gans[i]:
            if _compute_shishen(day_gan, gans[i]) in target_ss:
                return True
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break
                if _compute_shishen(day_gan, cg) in target_ss:
                    return True
    return False


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


# ───────────────────── 1. 牢狱字 ─────────────────────

def detect_laoyu_zi(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """牢狱字检测：亥/丑/辰 在局，且是否有「阴灭阳」(阳性有用之物被牢狱字坏了)。

    段氏：阳性有用的东西被 亥/丑/辰 坏了 -> 牢狱；阳制阴（制去牢狱字）不为牢狱。

    Returns:
        {
          'laoyu_zi': [str],          # 命中牢狱字
          'positions': [str],         # 牢狱字所在柱位
          'yin_mie_yang': bool,       # 阴灭阳（牢狱字坏阳性用神）
          'yang_zhi_yin': bool,       # 阳制阴（制牢狱字，反不主牢狱）
          'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'laoyu_zi': [], 'positions': [], 'yin_mie_yang': False,
                'yang_zhi_yin': False, 'details': ['四柱不全']}

    hits: List[str] = []
    positions: List[str] = []
    for i, z in enumerate(zhis):
        if z in _LAOYU_ZI:
            hits.append(z)
            positions.append(f'{PILLAR_NAMES_CN[i]}{z}')
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    # 阴灭阳：牢狱字（亥/丑/辰）冲/克/穿/刑/晦 阳性用神（食神/正印/正财/正官等阳性做功神）
    # 简化：牢狱字参与 克/穿/刑/冲 阳干阳支之用神
    yin_mie_yang = False
    control_types = {'冲', '克', '穿', '刑'}
    for a in wa:
        t = a.get('type', '')
        from_pos = a.get('from_pos', '')
        to_pos = a.get('to_pos', '')
        if t not in control_types:
            continue
        # 牢狱字作用于阳性柱
        for pos in (from_pos, to_pos):
            if not pos or '_' not in pos:
                continue
            pk = pos.split('_')[0]
            zi = a.get('action') or ''
            # 该柱地支是否牢狱字
            pidx = PILLAR_KEYS.index(pk) if pk in PILLAR_KEYS else -1
            if pidx < 0:
                continue
            z_at = zhis[pidx]
            if z_at in _LAOYU_ZI:
                # 对方柱是否阳性用神（食神/印等）
                other_pos = to_pos if pos == from_pos else from_pos
                if other_pos and '_' in other_pos:
                    opk = other_pos.split('_')[0]
                    oidx = PILLAR_KEYS.index(opk) if opk in PILLAR_KEYS else -1
                    if oidx >= 0 and other_pos.endswith('_zhi'):
                        oz = zhis[oidx]
                        og = gans[oidx]
                        # 阳干
                        if og in _YANG_GAN_SET:
                            ss = _compute_shishen(day_gan, og)
                            if ss in ('食神', '正印', '正财', '正官'):
                                yin_mie_yang = True

    # 阴灭阳补充：湿土(辰/丑)晦阳火(丙/丁/巳/午)——段氏最常见的「以阴灭阳」
    # 湿土晦火使火用神(食神/印/财/禄身)失能，为牢狱象。
    if not yin_mie_yang:
        shi_tu = [z for z in zhis if z in ('辰', '丑')]
        yang_huo = [g for g in gans if g in ('丙', '丁')] + \
                   [z for z in zhis if z in ('巳', '午')]
        if shi_tu and yang_huo:
            yin_mie_yang = True

    # 阳制阴：阳性柱制去牢狱字（反不主牢狱）
    yang_zhi_yin = False
    for a in wa:
        t = a.get('type', '')
        if t not in control_types:
            continue
        from_pos = a.get('from_pos', '')
        to_pos = a.get('to_pos', '')
        if from_pos and '_' in from_pos and from_pos.endswith('_gan'):
            fpk = from_pos.split('_')[0]
            fidx = PILLAR_KEYS.index(fpk) if fpk in PILLAR_KEYS else -1
            if fidx >= 0 and gans[fidx] in _YANG_GAN_SET:
                if to_pos and '_' in to_pos and to_pos.endswith('_zhi'):
                    tpk = to_pos.split('_')[0]
                    tidx = PILLAR_KEYS.index(tpk) if tpk in PILLAR_KEYS else -1
                    if tidx >= 0 and zhis[tidx] in _LAOYU_ZI:
                        yang_zhi_yin = True

    details: List[str] = []
    if hits:
        details.append(f'牢狱字：{"、".join(hits)}（{"、".join(positions)}）')
    if yin_mie_yang:
        details.append('阴灭阳：牢狱字坏阳性用神，牢狱之象')
    if yang_zhi_yin:
        details.append('阳制阴：阳干制牢狱字，反不主牢狱（减凶）')

    return {
        'laoyu_zi': hits,
        'positions': positions,
        'yin_mie_yang': yin_mie_yang,
        'yang_zhi_yin': yang_zhi_yin,
        'details': details,
    }


# ───────────────────── 2. 水多金沉 ─────────────────────

def detect_shui_duo_jin_chen(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """水多金沉：金（申/酉/庚/辛）多而水（亥/子/壬/癸）更旺，金沉于水 -> 牢狱。

    段氏：「水多金沉为牢狱」「金见水沉为牢狱」。
    判定：金五行明现 ≥2，水五行明现且数 ≥ 金数（水多金沉）。

    Returns:
        {'shui_duo_jin_chen': bool, 'jin_count': int, 'shui_count': int, 'details': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'shui_duo_jin_chen': False, 'jin_count': 0, 'shui_count': 0, 'details': ['四柱不全']}

    jin_count = 0
    shui_count = 0
    for i in range(4):
        if i < len(gans) and gans[i]:
            w = GAN_WX.get(gans[i], '')
            if w == '金':
                jin_count += 1
            elif w == '水':
                shui_count += 1
        if i < len(zhis) and zhis[i]:
            w = ZHI_WX.get(zhis[i], '')
            if w == '金':
                jin_count += 1
            elif w == '水':
                shui_count += 1

    triggered = jin_count >= 2 and shui_count >= jin_count
    details: List[str] = []
    if triggered:
        details.append(f'水多金沉：金{jin_count}见水{shui_count}，金沉于水，牢狱之象')
    elif jin_count >= 1 and shui_count >= 2:
        details.append(f'金见水沉：金{jin_count}水{shui_count}（水偏多，牢狱信号偏弱）')
    return {
        'shui_duo_jin_chen': triggered,
        'jin_count': jin_count,
        'shui_count': shui_count,
        'details': details,
    }


# ───────────────────── 3. 枭神夺食 ─────────────────────

def detect_xiao_duo_shi(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """枭神夺食：食神为重要做功之神，被偏印（枭）克夺 -> 失去自由坐牢。

    判定：偏印明现 + 食神明现（枭克食，食为用神被夺）。

    Returns:
        {'xiao_duo_shi': bool, 'has_xiao': bool, 'has_shi': bool, 'details': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'xiao_duo_shi': False, 'has_xiao': False, 'has_shi': False, 'details': ['四柱不全']}

    has_xiao = _has_shen_in_mingxian(day_gan, gans, zhis, {'偏印'})
    has_shi = _has_shen_in_mingxian(day_gan, gans, zhis, {'食神'})
    triggered = has_xiao and has_shi
    details: List[str] = []
    if triggered:
        details.append('枭神夺食：偏印克食神，食为做功之神被夺，失去自由坐牢')
    return {
        'xiao_duo_shi': triggered,
        'has_xiao': has_xiao,
        'has_shi': has_shi,
        'details': details,
    }


# ───────────────────── 4. 劫财+伤官 vs 官杀 ─────────────────────

def detect_jieshang_guansha(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """劫财+伤官 组合（结伙违法）与官杀对抗 -> 牢狱。

    段氏：「劫财、伤官的组合，主结伙违法之意，再与官杀对抗必为牢狱。」
          「比劫伤官怕见官」「伤官与官杀不和为牢狱之征」。
    判定：劫财明现 + 伤官明现 + 官杀明现（三方对抗）。

    Returns:
        {
          'jieshang_guansha': bool,
          'has_jie': bool, 'has_shang': bool, 'has_guansha': bool,
          'duikang': bool, 'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'jieshang_guansha': False, 'has_jie': False, 'has_shang': False,
                'has_guansha': False, 'duikang': False, 'details': ['四柱不全']}

    has_jie = _has_shen_in_mingxian(day_gan, gans, zhis, {'劫财', '比肩'})
    has_shang = _has_shen_in_mingxian(day_gan, gans, zhis, {'伤官'})
    has_guansha = _has_shen_in_mingxian(day_gan, gans, zhis, {'正官', '七杀'})
    duikang = has_jie and has_shang and has_guansha
    details: List[str] = []
    if has_jie and has_shang:
        details.append('劫财+伤官组合：主结伙违法之意')
    if duikang:
        details.append('与官杀对抗：比劫伤官见官，牢狱之征')
    return {
        'jieshang_guansha': duikang,
        'has_jie': has_jie,
        'has_shang': has_shang,
        'has_guansha': has_guansha,
        'duikang': duikang,
        'details': details,
    }


# ───────────────────── 5. 反局 + 辰丑 ─────────────────────

def detect_fanju_chen_chou(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """反局 + 辰/丑：反局且辰丑在局 -> 多数应牢狱。

    段氏：「凡出现反局的情况，有辰、丑等字在局中，多数应牢狱。」
    依赖 subjective.zhengfan.analyze_zhengfan 判反局。

    Returns:
        {
          'fanju': bool, 'fanju_type': str,
          'has_chen_chou': bool, 'chen_chou': [str],
          'laoyu': bool, 'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'fanju': False, 'fanju_type': '', 'has_chen_chou': False,
                'chen_chou': [], 'laoyu': False, 'details': ['四柱不全']}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    try:
        zf = analyze_zhengfan(day_gan, gans, zhis, relations=rel)
    except Exception:
        zf = {}
    fanju = zf.get('type') == 'fan'
    fanju_type = zf.get('configuration', '')

    chen_chou = [z for z in zhis if z in ('辰', '丑')]
    has_chen_chou = len(chen_chou) > 0
    laoyu = fanju and has_chen_chou

    details: List[str] = []
    if fanju:
        details.append(f'反局：{fanju_type}（{zf.get("reason","")}）')
    if has_chen_chou:
        details.append(f'辰丑在局：{"、".join(chen_chou)}')
    if laoyu:
        details.append('反局+辰丑，多数应牢狱')
    return {
        'fanju': fanju,
        'fanju_type': fanju_type,
        'has_chen_chou': has_chen_chou,
        'chen_chou': chen_chou,
        'laoyu': laoyu,
        'details': details,
        'zhengfan': zf,
    }


# ───────────────────── 附加：七杀夹制 / 无制 ─────────────────────

def detect_shaqie_zhi(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """七杀夹制日主 / 七杀无制 -> 牢狱象。

    段氏（资料未提，闲注归纳）：七杀夹制日主或七杀无制，都有牢狱之象。
    判定：
      - 七杀无制：七杀明现且无食神制、无印化；
      - 七杀夹克：日柱前后（年月或日时）两柱皆现七杀，夹克日主。

    Returns:
        {'sha_wu_zhi': bool, 'sha_jia_ke': bool, 'details': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'sha_wu_zhi': False, 'sha_jia_ke': False, 'details': ['四柱不全']}

    sha_pillars: List[int] = []
    for i in range(4):
        if i < len(gans) and gans[i] and _compute_shishen(day_gan, gans[i]) == '七杀':
            sha_pillars.append(i)
            continue
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break
                if _compute_shishen(day_gan, cg) == '七杀':
                    sha_pillars.append(i)
                    break

    has_shi = _has_shen_in_mingxian(day_gan, gans, zhis, {'食神', '伤官'})  # 食伤制杀
    has_yin = _has_shen_in_mingxian(day_gan, gans, zhis, {'正印', '偏印'})  # 印化杀
    sha_wu_zhi = len(sha_pillars) > 0 and not has_shi and not has_yin

    # 七杀夹克：日柱(idx=2)两侧（年月1/日时3）皆有七杀
    sha_jia_ke = 2 in sha_pillars and (1 in sha_pillars or 0 in sha_pillars) and (3 in sha_pillars)
    # 放宽：日柱本身带杀 + 前后任一带杀
    if not sha_jia_ke and 2 in sha_pillars and ((0 in sha_pillars or 1 in sha_pillars) and 3 in sha_pillars):
        sha_jia_ke = True

    details: List[str] = []
    if sha_wu_zhi:
        details.append('七杀无制：七杀明现无食制无印化，犯罪结构')
    if sha_jia_ke:
        details.append('七杀夹克：日柱前后皆七杀，夹克日主，牢狱之象')
    return {'sha_wu_zhi': sha_wu_zhi, 'sha_jia_ke': sha_jia_ke, 'details': details}


# ───────────────────── 附加：小偷 ─────────────────────

def detect_xiaotou(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """小偷：劫财为手、官为盗贼，劫财与官在主位（日时）组合 -> 小偷。

    段氏：「小偷：劫财为手，官为盗贼，劫财和官在主位组合时为小偷。」

    Returns:
        {'xiaotou': bool, 'jie_zhuwei': bool, 'guan_zhuwei': bool, 'details': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'xiaotou': False, 'jie_zhuwei': False, 'guan_zhuwei': False, 'details': ['四柱不全']}

    # 主位=日(idx=2)/时(idx=3)。劫财为手（不含比肩）。
    jie_zhuwei = False
    guan_zhuwei = False
    for i in (2, 3):
        if i < len(gans) and gans[i]:
            ss = _compute_shishen(day_gan, gans[i])
            if ss == '劫财':
                jie_zhuwei = True
            if ss in ('正官', '七杀'):
                guan_zhuwei = True
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break
                ss = _compute_shishen(day_gan, cg)
                if ss == '劫财':
                    jie_zhuwei = True
                if ss in ('正官', '七杀'):
                    guan_zhuwei = True
    xiaotou = jie_zhuwei and guan_zhuwei
    details: List[str] = []
    if xiaotou:
        details.append('小偷象：劫财(手)与官(盗贼)在主位组合')
    return {
        'xiaotou': xiaotou,
        'jie_zhuwei': jie_zhuwei,
        'guan_zhuwei': guan_zhuwei,
        'details': details,
    }


# ───────────────────── 附加：劫煞亡神 / 魁罡 / 官杀入墓（高级篇 ch11 扩展） ─────────────────────

def detect_jiesha_wangshen(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """劫煞亡神（高级篇 ch11）：劫煞主官非牢狱，亡神主失财官非。

    段氏：劫煞、亡神为凶性神煞，逢官杀明现或刑冲并，主官非牢狱之灾。劫煞尤验
    （主突然之灾、官司刑杖）；亡神主暗损、失权失财。本函数消费 shensha 三层收口
    之「灾祸三煞」层（劫煞/亡神），与牢狱五法并行加分。

    Returns:
        {
          'has_jiesha': bool, 'has_wangshen': bool,
          'jiesha_zhi': str, 'wangshen_zhi': str,
          'with_guansha': bool, 'with_xingchong': bool,
          'laoyu_signal': bool, 'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'has_jiesha': False, 'has_wangshen': False, 'laoyu_signal': False, 'details': ['四柱不全']}
    try:
        shen = compute_shensha_ext(day_gan, zhis)
    except Exception:
        shen = {}
    js = shen.get('劫煞') or {}
    ws_ = shen.get('亡神') or {}
    has_jiesha = bool(js.get('in_pillars'))
    has_wangshen = bool(ws_.get('in_pillars'))
    jiesha_zhi = js.get('zhi', '')
    wangshen_zhi = ws_.get('zhi', '')

    # 与官杀并 / 与刑冲并
    has_guansha = _has_shen_in_mingxian(day_gan, gans, zhis, {'正官', '七杀'})
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    with_xingchong = any(a.get('type') in ('冲', '刑', '穿') for a in wa)

    laoyu_signal = (has_jiesha or has_wangshen) and (has_guansha or with_xingchong)
    details: List[str] = []
    if has_jiesha:
        details.append(f'劫煞({jiesha_zhi})主官非刑杖')
    if has_wangshen:
        details.append(f'亡神({wangshen_zhi})主失权失财')
    if laoyu_signal:
        details.append('劫煞亡神与官杀/刑冲并，牢狱官非之象')
    return {
        'has_jiesha': has_jiesha, 'has_wangshen': has_wangshen,
        'jiesha_zhi': jiesha_zhi, 'wangshen_zhi': wangshen_zhi,
        'with_guansha': has_guansha, 'with_xingchong': with_xingchong,
        'laoyu_signal': laoyu_signal, 'details': details,
    }


def detect_kuigang(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """魁罡（高级篇 ch11）：庚辰/壬辰/庚戌/戊戌四日为魁罡，性刚好斗逢刑冲官杀主官非。

    段氏：魁罡日生人性格刚毅、好胜好斗，命中再见官杀明现或日柱逢刑冲，
    主官非牢狱；魁罡无制（无食伤制/印化）则刚而无礼易犯法。

    Returns:
        {
          'is_kuigang': bool, 'kuigang_day': str,
          'with_guansha': bool, 'with_xingchong': bool, 'wu_zhi': bool,
          'laoyu_signal': bool, 'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_kuigang': False, 'laoyu_signal': False, 'details': ['四柱不全']}
    day_zhi = zhis[PILLAR_KEYS.index('day')]
    is_kuigang = (day_gan, day_zhi) in _KUIGANG_DAYS
    if not is_kuigang:
        return {'is_kuigang': False, 'kuigang_day': '', 'with_guansha': False,
                'with_xingchong': False, 'wu_zhi': False, 'laoyu_signal': False, 'details': []}

    has_guansha = _has_shen_in_mingxian(day_gan, gans, zhis, {'正官', '七杀'})
    has_shi = _has_shen_in_mingxian(day_gan, gans, zhis, {'食神', '伤官'})
    has_yin = _has_shen_in_mingxian(day_gan, gans, zhis, {'正印', '偏印'})
    wu_zhi = not has_shi and not has_yin
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    # 日柱逢刑冲（日干或日支被冲刑）
    day_positions = {'day_gan', 'day_zhi'}
    with_xingchong = any(a.get('type') in ('冲', '刑', '穿') and
                         (a.get('from_pos', '') in day_positions or
                          a.get('to_pos', '') in day_positions) for a in wa)

    laoyu_signal = is_kuigang and (with_xingchong or (has_guansha and wu_zhi))
    details: List[str] = [f'魁罡日（{day_gan}{day_zhi}），性刚好斗']
    if with_xingchong:
        details.append('日柱逢刑冲，魁罡刚而受激')
    if has_guansha and wu_zhi:
        details.append('魁罡无制（无食伤制/印化）且见官杀，刚而无礼易犯法')
    if laoyu_signal:
        details.append('魁罡逢官杀刑冲，官非牢狱之象')
    return {
        'is_kuigang': is_kuigang, 'kuigang_day': f'{day_gan}{day_zhi}',
        'with_guansha': has_guansha, 'with_xingchong': with_xingchong,
        'wu_zhi': wu_zhi, 'laoyu_signal': laoyu_signal, 'details': details,
    }


def detect_guansha_rumu(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """官杀入墓（高级篇 ch11）：官杀五行入墓且墓不开，主官非失权牢狱。

    段氏：官杀（克我者）入墓库（墓库收官杀五行）且墓库未冲刑开库，
    主官非、罢官失权、牢狱之灾。复用 TOMB_MAP（墓库→所收五行）。

    Returns:
        {
          'in_tomb': bool, 'guan_wx': str, 'tomb_zhi': str,
          'tomb_open': bool, 'laoyu_signal': bool, 'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'in_tomb': False, 'laoyu_signal': False, 'details': ['四柱不全']}
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')  # 官杀五行=克我
    if not guan_wx:
        return {'in_tomb': False, 'laoyu_signal': False, 'details': []}
    # 官杀须明现方有入墓可言
    has_guansha = _has_shen_in_mingxian(day_gan, gans, zhis, {'正官', '七杀'})
    tomb_zhi = ''
    for z in zhis:
        if z and guan_wx in TOMB_MAP.get(z, []):
            tomb_zhi = z
            break
    in_tomb = has_guansha and bool(tomb_zhi)
    # 墓开否（该墓支被冲/刑开库）
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    tomb_open = False
    if tomb_zhi:
        tomb_open = any(
            a.get('type') in ('冲', '刑') and
            ((a.get('from_pos', '').endswith('_zhi') and
              zhis[PILLAR_KEYS.index(a['from_pos'].split('_')[0])] == tomb_zhi if a['from_pos'].split('_')[0] in PILLAR_KEYS else False) or
             (a.get('to_pos', '').endswith('_zhi') and
              zhis[PILLAR_KEYS.index(a['to_pos'].split('_')[0])] == tomb_zhi if a['to_pos'].split('_')[0] in PILLAR_KEYS else False))
            for a in wa
        )
    laoyu_signal = in_tomb and not tomb_open
    details: List[str] = []
    if in_tomb:
        details.append(f'官杀({guan_wx}五行)入墓{tomb_zhi}，' +
                       ('墓未开，官非失权牢狱之象' if not tomb_open else '然墓被冲刑开库，凶减'))
    return {
        'in_tomb': in_tomb, 'guan_wx': guan_wx, 'tomb_zhi': tomb_zhi,
        'tomb_open': tomb_open, 'laoyu_signal': laoyu_signal, 'details': details,
    }


# ───────────────────── 聚合 ─────────────────────

def analyze_laoyu(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
) -> Dict:
    """牢狱综合：五法 + 附加犯罪特征 + 劫煞亡神/魁罡/官杀入墓 聚合。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'laoyu_zi': {...}, 'shui_duo_jin_chen': {...}, 'xiao_duo_shi': {...},
          'jieshang_guansha': {...}, 'fanju_chen_chou': {...},
          'shaqie_zhi': {...}, 'xiaotou': {...},
          'jiesha_wangshen': {...}, 'kuigang': {...}, 'guansha_rumu': {...},
          'hit_count': int, 'methods': [str], 'risk': '高'|'中'|'低'|'无',
          'summary': str,
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
        return {'hit_count': 0, 'methods': [], 'risk': '无',
                'summary': '四柱不全，无法判定牢狱'}

    r_zi = detect_laoyu_zi(day_gan, gans, zhis, relations)
    r_shui = detect_shui_duo_jin_chen(day_gan, gans, zhis)
    r_xiao = detect_xiao_duo_shi(day_gan, gans, zhis)
    r_jie = detect_jieshang_guansha(day_gan, gans, zhis)
    r_fanju = detect_fanju_chen_chou(day_gan, gans, zhis, relations)
    r_sha = detect_shaqie_zhi(day_gan, gans, zhis)
    r_xt = detect_xiaotou(day_gan, gans, zhis)
    r_jsws = detect_jiesha_wangshen(day_gan, gans, zhis, relations)
    r_kg = detect_kuigang(day_gan, gans, zhis, relations)
    r_gshm = detect_guansha_rumu(day_gan, gans, zhis, relations)

    methods: List[str] = []
    if r_zi.get('yin_mie_yang'):
        methods.append('牢狱字(阴灭阳)')
    if r_shui.get('shui_duo_jin_chen'):
        methods.append('水多金沉')
    if r_xiao.get('xiao_duo_shi'):
        methods.append('枭神夺食')
    if r_jie.get('duikang'):
        methods.append('劫伤抗官')
    if r_fanju.get('laoyu'):
        methods.append('反局+辰丑')
    if r_sha.get('sha_wu_zhi') or r_sha.get('sha_jia_ke'):
        methods.append('七杀无制/夹克')
    if r_xt.get('xiaotou'):
        methods.append('小偷象')
    if r_jsws.get('laoyu_signal'):
        methods.append('劫煞亡神')
    if r_kg.get('laoyu_signal'):
        methods.append('魁罡逢冲官')
    if r_gshm.get('laoyu_signal'):
        methods.append('官杀入墓')

    hit_count = len(methods)
    # 段氏「占其一即有象，多者灾重」：1法=低，2法=中，3+法=高
    risk = '无'
    if hit_count >= 3:
        risk = '高'
    elif hit_count == 2:
        risk = '中'
    elif hit_count == 1:
        risk = '低' if r_zi.get('yang_zhi_yin') else '低'
    else:
        # 仅有牢狱字无阴灭阳，且阳制阴 -> 无；否则低
        if r_zi.get('laoyu_zi') and not r_zi.get('yang_zhi_yin'):
            risk = '低'
        else:
            risk = '无'

    summary = f'牢狱风险{risk}'
    if methods:
        summary += f'；命中{hit_count}法（{"、".join(methods)}）'

    return {
        'laoyu_zi': r_zi,
        'shui_duo_jin_chen': r_shui,
        'xiao_duo_shi': r_xiao,
        'jieshang_guansha': r_jie,
        'fanju_chen_chou': r_fanju,
        'shaqie_zhi': r_sha,
        'xiaotou': r_xt,
        'jiesha_wangshen': r_jsws,
        'kuigang': r_kg,
        'guansha_rumu': r_gshm,
        'hit_count': hit_count,
        'methods': methods,
        'risk': risk,
        'summary': summary,
    }


__all__ = [
    'detect_laoyu_zi',
    'detect_shui_duo_jin_chen',
    'detect_xiao_duo_shi',
    'detect_jieshang_guansha',
    'detect_fanju_chen_chou',
    'detect_shaqie_zhi',
    'detect_xiaotou',
    'detect_jiesha_wangshen',
    'detect_kuigang',
    'detect_guansha_rumu',
    'analyze_laoyu',
]
