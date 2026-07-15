"""
liuqin - 盲派六亲专辑·主观层（subjective）

理论来源：段建业《盲派命理高级内容篇》第十章「六亲专题」（源文 13474-14817 行）
核心思想：六亲论断以「星宫同参」为纲——星定六亲之有无吉凶，宫定六亲之
          位置与缘分离合。父母、子女、兄弟姐妹三组各有定位变法与存亡克损
          之机。高级篇在中级「星宫同参」基础上补齐三套变法：

四组判定（高级篇第十章）：
  1. 父母星定位变法（10.1）：父星正法=财/官杀，变法=印当父（财克印/印盖头
     财，多主弃养）；母星正法=印，变法=食伤/禄/比劫当母（无印时）。并判
     早逝（财临库地/患父患母/三刑夹刑/宫星同坏无救助）、多婚（双合/伏吟）、
     弃养（年月食伤入墓/财印被坏/年柱偏财/日时见合迎新主）。
  2. 子息有无与性别换象（10.2）：子息星定位（男官杀、女食伤，无则互寻），
     无子五标志（星入墓不开/宫空亡穿破/原神被坏/枭神夺食/满盘比劫伤官）；
     性别换象——先现之子息星被刑冲穿合，则头胎性别与先现之星所示相反
     （源文 14156）。换象判据消费 xiangfa_ops.huanxiang（制尽则换，象意层
     互证：子息星之制尽换象为性别翻转之强证）。
  3. 兄弟姐妹时辰定数法（10.3）：以时支定基数（子午卯酉≈4/寅申巳亥2-3/
     辰戌丑未1），月令旺加数、冲提纲减数、比劫透干加减、满盘比劫物极必反。

消费关系：
  - objective.constants（五行生克/藏干/禄/刑冲穿破）
  - objective.canggan.get_canggan_mangpai（藏干，星定位用）
  - objective.zuogong_detect.detect_relations（刑冲穿合，换象/克损用）
  - objective.shensha.compute_shensha_ext（孤辰寡宿华盖，独子/克损辅证）
  - objective.muku.analyze_muku（墓库开闭，星入墓用）
  - subjective.xiangfa_ops.huanxiang（制尽换象，子息性别转换互证）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：时辰定数法为盲师口传启发式（口诀量化，非精确计数）；性别换象
          阈值为「刑冲穿合任一即换」段氏主流口径；父母变法各师口传有细微差异。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    TIAN_GAN_HE, LU, CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN,
    is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext
from mangpai.objective.muku import analyze_muku
from mangpai.objective.zuogong_detect import detect_relations

_YANG_GANS = set('甲丙戊庚壬')


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
    """十神大类。"""
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


def _wx_cat(day_gan: str, wx: str) -> str:
    """五行 → 对日主十神大类。"""
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


def _pillar_has_cat(day_gan: str, gan: str, zhi: str, cat: str) -> bool:
    """某柱是否含某十神大类（天干透或地支本/中气藏）。"""
    if _cat(_compute_shishen(day_gan, gan)) == cat:
        return True
    if ZHI_WX.get(zhi) and _wx_cat(day_gan, ZHI_WX.get(zhi)) == cat:
        return True
    for idx, (cg, _) in enumerate(get_canggan_mangpai(zhi)):
        if idx <= 1 and _cat(_compute_shishen(day_gan, cg)) == cat:
            return True
    return False


def _pillar_cats(day_gan: str, gan: str, zhi: str) -> Set[str]:
    """某柱所含十神大类集合（透干+地支本/中气）。"""
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


def _attacked_kinds_on_pillar(wa: List[Dict], pillar_idx: int) -> List[str]:
    """某柱地支被刑/冲/穿/破/合的动作类型列表。"""
    pk = PILLAR_KEYS[pillar_idx]
    target = f'{pk}_zhi'
    kinds: List[str] = []
    for a in wa:
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if target not in (fp, tp):
            continue
        t = a.get('type', '')
        if t in ('刑', '冲', '穿', '破', '地支合', '半合', '三合局', '暗合'):
            if t not in kinds:
                kinds.append(t)
    return kinds


# ───────────────────── 1. 父母星定位变法 + 早逝/多婚/弃养 ─────────────────────

def classify_parent_star(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """父母星定位（正法+变法）。

    父星正法=财（偏财为主，正财亦可为父，尤阳日干正财合身）；无财看官杀。
    父星变法=印当父（财克印/印盖头财），多主弃养之象。
    母星正法=印；无印看食伤（食伤为女性、生我之物）；禄为养命之根亦可当母
    （尤禄在年月）；比劫特殊情况下作母。

    Returns:
        {
          'father_normal': str,   # 正法父星大类（财/官杀）
          'father_variant': str,  # 变法父星大类（印，若触发）
          'father_variant_reason': str,
          'mother_normal': str,   # 正法母星大类（印）
          'mother_variant': str,  # 变法母星大类（食伤/禄/比劫，若触发）
          'mother_variant_reason': str,
          'desc': str,
        }
    """
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')     # 财五行=我克
    guan_wx = WX_KE_ME.get(day_wx, '')  # 官五行=克我
    yin_wx = WX_SHENG.get(day_wx, '')   # 印五行=生我（反过来：生我者为印）
    # 注：WX_SHENG[day_wx]=我生者(食伤)；生我者须反查
    sheng_me_wx = ''
    for w, child in WX_SHENG.items():
        if child == day_wx:
            sheng_me_wx = w  # 印五行
            break

    all_cats: List[Set[str]] = [_pillar_cats(day_gan, gans[i], zhis[i]) for i in range(4)]
    flat = set().union(*all_cats) if all_cats else set()

    # ── 父星 ──
    father_normal = '财' if '财' in flat else ('官杀' if '官杀' in flat else '财')
    father_variant = ''
    father_reason = ''
    # 变法：财克印（财坏印）→ 印当父（弃养象）。判据：命局有印且印被财克坏。
    if '印' in flat and '财' in flat:
        # 印五行被财五行克（财五行=我克=WX_KE[day_wx]；印五行=生我者）
        # 财克印须五行成立：WX_KE[财五行]==印五行
        if WX_KE.get(cai_wx) == sheng_me_wx:
            father_variant = '印'
            father_reason = '财克印（财坏印），印当父，多主弃养之象'

    # ── 母星 ──
    mother_normal = '印' if '印' in flat else ''
    mother_variant = ''
    mother_reason = ''
    if not mother_normal:
        # 无印看食伤
        if '食伤' in flat:
            mother_variant = '食伤'
            mother_reason = '无印，以食伤为母（食伤为女性、生我之物）'
        else:
            # 禄为养命之根当母（禄在年月尤佳）
            lu_zhi = LU.get(day_gan, '')
            lu_in_year_month = lu_zhi and (lu_zhi in (zhis[0], zhis[1]))
            if lu_in_year_month:
                mother_variant = '禄'
                mother_reason = f'无印无食伤，禄（{lu_zhi}）在年月，当母看'
            elif '比劫' in flat:
                mother_variant = '比劫'
                mother_reason = '无印无食伤无禄在年月，比劫特殊作母'

    desc = f'父星正法：{father_normal or "无（待运岁出现）"}'
    if father_variant:
        desc += f'；变法：{father_variant}（{father_reason}）'
    desc += f'；母星正法：{mother_normal or "无"}'
    if mother_variant:
        desc += f'；变法：{mother_variant}（{mother_reason}）'

    return {
        'father_normal': father_normal,
        'father_variant': father_variant,
        'father_variant_reason': father_reason,
        'mother_normal': mother_normal,
        'mother_variant': mother_variant,
        'mother_variant_reason': mother_reason,
        'desc': desc,
    }


def detect_parent_zaoshi(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """父母早逝标志（口诀二）。

    四标志：
      1. 财临库地：父星（财/官杀）坐墓库且墓库被刑冲开或父星无原神。
      2. 患父患母：父母星多现杂现（正偏同透/官杀混杂）。
      3. 三刑夹刑：父母星或父母宫（年月）犯三刑或夹刑。
      4. 宫星同坏无救助：父母星在年月宫位受冲克穿破、无原神生助。

    Returns:
        {'is_zaoshi': bool, 'markers': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    markers: List[str] = []

    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    parent_wxs = {cai_wx, guan_wx}
    # 父母宫=年月柱
    parent_palace_idx = [0, 1]

    # 1. 财临库地：父星坐墓库
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    tombs = muku.get('tombs') or []
    for i in (0, 1, 2, 3):
        z = zhis[i]
        # 父星坐墓库（天干父星坐墓）
        g = gans[i]
        if g and GAN_WX.get(g) in parent_wxs:
            for tb in tombs:
                if tb.get('zhi') == z:
                    markers.append(f'父星{g}坐{z}墓库（财临库地）')
                    break

    # 2. 患父患母：父母星多现杂现
    def _count_parent_stars() -> int:
        cnt = 0
        for i in range(4):
            if _pillar_has_cat(day_gan, gans[i], zhis[i], '财') or \
               _pillar_has_cat(day_gan, gans[i], zhis[i], '官杀'):
                cnt += 1
        return cnt
    if _count_parent_stars() >= 3:
        markers.append('父母星多现杂现（患父患母）')

    # 3. 三刑夹刑：年月宫犯三刑
    year_month_zhis = [zhis[0], zhis[1]]
    xing_hits = [t for t in wa if t.get('type') == '刑'
                 and (t.get('from_pos', '').split('_')[0] in ('year', 'month')
                      or t.get('to_pos', '').split('_')[0] in ('year', 'month'))]
    if xing_hits:
        markers.append('父母宫（年月）犯三刑夹刑')

    # 4. 宫星同坏无救助：父母星在年月受冲克穿破
    attack_kinds: List[str] = []
    for i in parent_palace_idx:
        for k in _attacked_kinds_on_pillar(wa, i):
            if k in ('冲', '穿', '破') and k not in attack_kinds:
                attack_kinds.append(k)
    if attack_kinds:
        markers.append(f'父母宫受{"、".join(attack_kinds)}（宫星同坏）')

    is_zaoshi = len(markers) >= 1
    return {
        'is_zaoshi': is_zaoshi,
        'markers': markers,
        'desc': '；'.join(markers) if markers else '无明显父母早逝标志',
    }


def detect_parent_duohun(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """父母多婚标志（口诀三）：父星/母星伏吟或双合。

    Returns:
        {'is_duohun': bool, 'markers': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    markers: List[str] = []

    # 父星=财/官杀，母星=印
    # 伏吟：同一天干/地支现两柱
    gan_counts: Dict[str, int] = {}
    for g in gans:
        if g:
            gan_counts[g] = gan_counts.get(g, 0) + 1
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    yin_wx = ''
    for w, child in WX_SHENG.items():
        if child == day_wx:
            yin_wx = w
            break

    # 父星天干伏吟
    for g, c in gan_counts.items():
        if c >= 2 and GAN_WX.get(g) in (cai_wx, guan_wx):
            markers.append(f'父星{g}伏吟（双透）')
    # 母星天干伏吟
    for g, c in gan_counts.items():
        if c >= 2 and GAN_WX.get(g) == yin_wx:
            markers.append(f'母星{g}伏吟（双透）')

    # 双合：父母星与他干相合（非日主）
    for a in wa:
        if a.get('type') not in ('天干合', '地支合', '半合', '三合局', '暗合'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        # 排除日主自合
        if 'day_gan' in (fp, tp) or 'day_zhi' in (fp, tp):
            continue
        # 涉及父母星柱（年月）
        if any(p.split('_')[0] in ('year', 'month') for p in (fp, tp)):
            markers.append('父母星双合（非日主）')
            break

    is_duohun = bool(markers)
    return {
        'is_duohun': is_duohun,
        'markers': markers,
        'desc': '；'.join(markers) if markers else '无明显父母多婚标志',
    }


def detect_parent_qiyang(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """父母弃养标志（口诀四）。

    四标志：
      1. 年月食伤入墓：食伤在年月入墓或被合绊。
      2. 财印被坏：年月财星/印星被破坏（家境赤贫）。
      3. 年柱偏财：年柱干支皆偏财（养子象）。
      4. 日时见合迎新主：日时柱见天干五合（丁壬/乙庚等）。

    Returns:
        {'is_qiyang': bool, 'markers': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    markers: List[str] = []

    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    tombs_zhis = {tb.get('zhi') for tb in (muku.get('tombs') or [])}

    # 1. 年月食伤入墓
    for i in (0, 1):
        if _pillar_has_cat(day_gan, gans[i], zhis[i], '食伤'):
            if zhis[i] in tombs_zhis:
                markers.append(f'年月食伤入{zhis[i]}墓（父母无力抚养）')
                break
    # 食伤被合绊（年月食伤柱受合）
    for i in (0, 1):
        if _pillar_has_cat(day_gan, gans[i], zhis[i], '食伤'):
            if any(k in ('地支合', '半合', '三合局') for k in _attacked_kinds_on_pillar(wa, i)):
                if not any('食伤入' in m for m in markers):
                    markers.append('年月食伤被合绊')
                    break

    # 2. 财印被坏：年月财/印受冲穿破
    for i in (0, 1):
        if _pillar_has_cat(day_gan, gans[i], zhis[i], '财') or \
           _pillar_has_cat(day_gan, gans[i], zhis[i], '印'):
            kinds = [k for k in _attacked_kinds_on_pillar(wa, i) if k in ('冲', '穿', '破')]
            if kinds:
                markers.append(f'年月财/印被{"、".join(kinds)}（家境赤贫）')
                break

    # 3. 年柱偏财：年柱干支皆偏财
    year_gan_ss = _compute_shishen(day_gan, gans[0])
    year_zhi_cats = _pillar_cats(day_gan, '', zhis[0])
    if year_gan_ss == '偏财' and '财' in year_zhi_cats:
        markers.append('年柱干支皆偏财（养子之象）')

    # 4. 日时见合迎新主
    for a in wa:
        if a.get('type') != '天干合':
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if any(p.split('_')[0] in ('day', 'hour') for p in (fp, tp)):
            markers.append('日时见天干合（迎新主、换门楼）')
            break

    is_qiyang = bool(markers)
    return {
        'is_qiyang': is_qiyang,
        'markers': markers,
        'desc': '；'.join(markers) if markers else '无明显弃养标志',
    }


# ───────────────────── 2. 子息有无 + 性别换象 ─────────────────────

def _child_star_cat(day_gan: str, gans: List[str], zhis: List[str], gender: str) -> str:
    """子息星大类：男命=官杀（无则食伤），女命=食伤（无则财）。"""
    flat = set().union(*[_pillar_cats(day_gan, gans[i], zhis[i]) for i in range(4)]) \
        if len(gans) == 4 else set()
    primary = '官杀' if gender == '男' else '食伤'
    if primary in flat:
        return primary
    fallback = '食伤' if gender == '男' else '财'
    return fallback if fallback in flat else primary


def _child_star_gender(gender: str, day_gan: str, star_ss: str) -> str:
    """单颗子息星所示头胎性别（'男'/'女'）。

    口诀二（源文 14132-14137）：「男命杀儿官女郎；女命伤儿食女相」。
      男命：七杀=儿，正官=女；无官杀则 食神=儿，伤官=女。
      女命：伤官=儿，食神=女（口诀统一口径，由案例五「戊女命酉伤官被戌穿
            →换象→头胎生女」互证：伤官示儿，穿则翻转得女）。
    财星统看（无官杀/食伤时）：偏财=儿，正财=女（同性原则近似）。
    已知争议：源文另有「阴阳日干要端详」一句，部分口传按日干阴阳分食伤性别，
              与案例五矛盾；本模块取口诀统一口径 + 案例互证。
    """
    if gender == '男':
        mapping = {
            '七杀': '男', '正官': '女',
            '食神': '男', '伤官': '女',
            '偏财': '男', '正财': '女',
        }
        return mapping.get(star_ss, '')
    else:
        mapping = {
            '伤官': '男', '食神': '女',
            '偏财': '男', '正财': '女',
        }
        # 女命官杀为夫非子息，仅食伤/财论子息
        return mapping.get(star_ss, '') if star_ss in ('伤官', '食神', '偏财', '正财') else ''


def _first_child_star_pillar(
    day_gan: str, gans: List[str], zhis: List[str], gender: str, cat: str,
) -> Optional[int]:
    """先现子息星所在柱索引。男命年→时扫，女命时→年扫。"""
    order = [0, 1, 2, 3] if gender == '男' else [3, 2, 1, 0]
    for i in order:
        if _pillar_has_cat(day_gan, gans[i], zhis[i], cat):
            return i
    return None


def detect_zixi_youwu(
    day_gan: str, gans: List[str], zhis: List[str], gender: str = '男',
    relations: Optional[Dict] = None,
) -> Dict:
    """子息有无（口诀一）。

    无子五标志：
      1. 子息星入墓库不开。
      2. 子息宫（时柱）空亡或受穿破刑冲。
      3. 子息星原神被坏（官杀原神=财，食伤原神=比劫）。
      4. 枭神夺食（女命印太旺克食伤）。
      5. 满盘比劫（男）/伤官（女）克子。

    Returns:
        {'has_zixi': bool, 'markers': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    kong_wang_zhis = set(rel.get('kong_wang_zhis') or [])
    markers: List[str] = []

    cat = _child_star_cat(day_gan, gans, zhis, gender)
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    tombs = muku.get('tombs') or []
    open_tombs = {t.get('zhi') for t in (muku.get('open_tombs') or [])}
    closed_tombs = {t.get('zhi') for t in (muku.get('closed_tombs') or [])}

    # 1. 子息星入墓库不开
    child_wx = ''
    day_wx = GAN_WX.get(day_gan, '')
    if cat == '官杀':
        child_wx = WX_KE_ME.get(day_wx, '')
    elif cat == '食伤':
        child_wx = WX_SHENG.get(day_wx, '')
    elif cat == '财':
        child_wx = WX_KE.get(day_wx, '')
    for tb in tombs:
        z = tb.get('zhi')
        # 该墓库收的五行含子息五行，且墓库未开
        stored = []
        for w in ('木', '火', '土', '金', '水'):
            if z in _tomb_zhis_of_wx(w):
                stored.append(w)
        if child_wx in stored and z in closed_tombs:
            markers.append(f'子息星（{child_wx}）入{z}墓不开')
            break

    # 2. 子息宫（时柱）空亡或受穿破刑冲
    hour_kinds = _attacked_kinds_on_pillar(wa, 3)
    if zhis[3] in kong_wang_zhis:
        markers.append('子息宫（时支）空亡')
    bad_kinds = [k for k in hour_kinds if k in ('穿', '破', '刑', '冲')]
    if bad_kinds:
        markers.append(f'子息宫受{"、".join(bad_kinds)}')

    # 3. 子息星原神被坏：官杀原神=财，食伤原神=比劫
    yuan_cat = '财' if cat == '官杀' else ('比劫' if cat == '食伤' else '比劫')
    # 原神柱受冲穿破
    for i in range(4):
        if _pillar_has_cat(day_gan, gans[i], zhis[i], yuan_cat):
            kinds = [k for k in _attacked_kinds_on_pillar(wa, i) if k in ('冲', '穿', '破')]
            if kinds:
                markers.append(f'子息原神（{yuan_cat}）被{"、".join(kinds)}')
                break

    # 4. 枭神夺食（女命印太旺克食伤）
    if gender == '女' and cat == '食伤':
        yin_count = sum(1 for i in range(4) if _pillar_has_cat(day_gan, gans[i], zhis[i], '印'))
        shi_count = sum(1 for i in range(4) if _pillar_has_cat(day_gan, gans[i], zhis[i], '食伤'))
        if yin_count >= 2 and yin_count > shi_count:
            markers.append('枭神夺食（印旺克食伤，损子）')

    # 5. 满盘比劫（男）/伤官（女）
    if gender == '男':
        bijie_count = sum(1 for i in range(4) if _pillar_has_cat(day_gan, gans[i], zhis[i], '比劫'))
        if bijie_count >= 3:
            markers.append('满盘比劫克财（不利子息）')
    else:
        sg_count = sum(1 for i in range(4) if _pillar_has_cat(day_gan, gans[i], zhis[i], '食伤'))
        if sg_count >= 3:
            markers.append('满盘伤官克官（不利子息）')

    has_zixi = not markers
    return {
        'has_zixi': has_zixi,
        'child_star_cat': cat,
        'markers': markers,
        'desc': '有子息之象' if has_zixi else '；'.join(markers),
    }


_TOMB_WX_ZHIS = {
    '木': {'未'}, '火': {'戌'}, '金': {'丑'}, '水': {'辰'}, '土': {'辰'},
}


def _tomb_zhis_of_wx(wx: str) -> Set[str]:
    return _TOMB_WX_ZHIS.get(wx, set())


def detect_zixi_xingbie(
    day_gan: str, gans: List[str], zhis: List[str], gender: str = '男',
    relations: Optional[Dict] = None,
) -> Dict:
    """子息头胎性别 + 换象（口诀二）。

    基本法：先现子息星所示性别为头胎性别。
    换象法（源文 14156）：先现子息星被刑/冲/穿/合 → 头胎性别翻转。
    互证：消费 xiangfa_ops.huanxiang —— 若该子息星之五行被制尽换象（huanxiang
    返回 domain 命中子息大类），为性别翻转之强证。

    Returns:
        {
          'child_star_cat': str,
          'first_pillar': str,        # 先现子息星柱位
          'base_gender': str,         # 先现星所示性别
          'huanxiang': bool,          # 是否换象（翻转）
          'huanxiang_trigger': [str], # 触发动作（刑/冲/穿/合）
          'corroborated': bool,       # huanxiang() 制尽换象互证
          'final_gender': str,        # 头胎性别
          'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    cat = _child_star_cat(day_gan, gans, zhis, gender)
    first = _first_child_star_pillar(day_gan, gans, zhis, gender, cat)

    if first is None:
        return {
            'child_star_cat': cat, 'first_pillar': '', 'base_gender': '',
            'huanxiang': False, 'huanxiang_trigger': [], 'corroborated': False,
            'final_gender': '', 'desc': '原局无子息星，性别待运岁出现再论',
        }

    # 先现星的具体十神（取该柱透干或本/中气藏干中属子息大类者）
    first_ss = ''
    g, z = gans[first], zhis[first]
    if _cat(_compute_shishen(day_gan, g)) == cat:
        first_ss = _compute_shishen(day_gan, g)
    else:
        for idx, (cg, src) in enumerate(get_canggan_mangpai(z)):
            if idx <= 1 and _cat(_compute_shishen(day_gan, cg)) == cat:
                first_ss = _compute_shishen(day_gan, cg)
                break
    base_gender = _child_star_gender(gender, day_gan, first_ss)

    # 换象触发：先现子息星柱被刑/冲/穿/合
    kinds = _attacked_kinds_on_pillar(wa, first)
    swap_kinds = [k for k in kinds if k in ('刑', '冲', '穿', '地支合', '半合', '三合局', '暗合')]
    # 亦看天干合涉该柱
    for a in wa:
        if a.get('type') == '天干合':
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            if f'{PILLAR_KEYS[first]}_gan' in (fp, tp) and '合' not in swap_kinds:
                swap_kinds.append('合')
    huanxiang = bool(swap_kinds)

    # 互证：xiangfa_ops.huanxiang 制尽换象
    corroborated = False
    try:
        from mangpai.subjective.xiangfa_ops import huanxiang as _huanxiang
        hx = _huanxiang(day_gan, gans, zhis, rel)
        for f in hx:
            if f.get('domain') == cat or cat in (f.get('domain') or ''):
                corroborated = True
                break
    except Exception:
        corroborated = False

    final_gender = ''
    if base_gender:
        if huanxiang:
            final_gender = '女' if base_gender == '男' else '男'
        else:
            final_gender = base_gender

    desc = (f'先现子息星（{cat}）在{PILLAR_NAMES_CN[first]}柱，所示头胎'
            f'{base_gender or "未明"}')
    if huanxiang:
        desc += f'；被{"、".join(swap_kinds)}触发换象，头胎反为{final_gender}'
        if corroborated:
            desc += '（制尽换象互证）'
    elif final_gender:
        desc += f'；头胎{final_gender}'

    return {
        'child_star_cat': cat,
        'first_pillar': PILLAR_KEYS[first],
        'base_gender': base_gender,
        'huanxiang': huanxiang,
        'huanxiang_trigger': swap_kinds,
        'corroborated': corroborated,
        'final_gender': final_gender,
        'desc': desc,
    }


# ───────────────────── 3. 兄弟姐妹时辰定数法 ─────────────────────

_HOUR_BASE_COUNT = {
    # 子午卯酉：~4（"不够五个够二双"）
    '子': 4, '午': 4, '卯': 4, '酉': 4,
    # 寅申巳亥：2-3
    '寅': 3, '申': 3, '巳': 3, '亥': 3,
    # 辰戌丑未：1（独子）
    '辰': 1, '戌': 1, '丑': 1, '未': 1,
}


def classify_xiongdi_shuliang(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """兄弟姐妹数量（时辰定数法，口诀一）。

    基数（时支）：子午卯酉≈4 / 寅申巳亥≈3 / 辰戌丑未≈1。
    修正：
      + 月令为比劫旺地 → +1（"月令旺相再加倍"）。
      - 冲提纲（月支被冲）→ -1（"冲了提纲不挨肩"，间隔大、减数）。
      + 比劫透干每见一个 +1（"比劫透干须加数"）。
      - 月透七杀/伤官 → -1（"官杀伤官损手足"）。
      物极必反：满盘比劫（≥3柱）→ 反主独子/一个（"物极必反是真途"）。

    Returns:
        {
          'hour_zhi': str, 'base': int, 'adjust': int, 'estimate': int,
          'factors': [str], 'wuji_bi fan': bool, 'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    hour_zhi = zhis[3] if len(zhis) == 4 else ''
    base = _HOUR_BASE_COUNT.get(hour_zhi, 0)
    factors: List[str] = []
    adjust = 0

    # 物极必反：满盘比劫
    bijie_pillars = sum(1 for i in range(4) if _pillar_has_cat(day_gan, gans[i], zhis[i], '比劫'))
    wuji = bijie_pillars >= 3
    if wuji:
        # 物极必反：独子
        return {
            'hour_zhi': hour_zhi, 'base': base, 'adjust': 0, 'estimate': 1,
            'factors': ['满盘比劫物极必反（反主独子）'],
            'wuji_bifan': True,
            'desc': '满盘比劫物极必反，兄弟姐妹只一个（或独子）',
        }

    # 月令为比劫旺地 → +1
    month_zhi = zhis[1] if len(zhis) == 4 else ''
    if _pillar_has_cat(day_gan, gans[1], month_zhi, '比劫'):
        adjust += 1
        factors.append('月令比劫旺地 +1')

    # 冲提纲（月支被冲）→ -1
    month_attacked = any(
        a.get('type') == '冲' and (
            a.get('from_pos') == 'month_zhi' or a.get('to_pos') == 'month_zhi')
        for a in wa
    )
    if month_attacked:
        adjust -= 1
        factors.append('冲提纲 -1（间隔大、不挨肩）')

    # 比劫透干每见 +1（天干比劫，排除日干本身）
    bijie_gan_count = sum(1 for i in range(4) if i != 2 and gans[i]
                          and _cat(_compute_shishen(day_gan, gans[i])) == '比劫')
    if bijie_gan_count:
        adjust += bijie_gan_count
        factors.append(f'比劫透干{bijie_gan_count}个 +{bijie_gan_count}')

    # 月透七杀/伤官 → -1
    month_gan_ss = _compute_shishen(day_gan, gans[1]) if gans[1] else ''
    if month_gan_ss in ('七杀', '伤官'):
        adjust -= 1
        factors.append(f'月透{month_gan_ss} -1（损手足）')

    estimate = max(1, base + adjust)
    desc = f'时支{hour_zhi}基数{base}；' + '；'.join(factors) if factors \
        else f'时支{hour_zhi}基数{base}（无修正）'
    desc += f'；估算约{estimate}个'

    return {
        'hour_zhi': hour_zhi, 'base': base, 'adjust': adjust,
        'estimate': estimate, 'factors': factors, 'wuji_bifan': False,
        'desc': desc,
    }


def detect_xiongdi_keshun(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """兄弟姐妹克损标志（口诀三）。

    标志：月令七杀伤官透、比劫坐墓逢冲、三刑夹刑损兄弟、羊刃逢冲、
    比劫入空亡/遭合化。

    Returns:
        {'has_keshun': bool, 'markers': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    kong_wang_zhis = set(rel.get('kong_wang_zhis') or [])
    markers: List[str] = []

    # 月令七杀伤官透
    month_gan_ss = _compute_shishen(day_gan, gans[1]) if gans[1] else ''
    if month_gan_ss in ('七杀', '伤官'):
        markers.append(f'月透{month_gan_ss}（兄弟有损）')

    # 比劫坐墓逢冲
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    tombs_zhis = {tb.get('zhi') for tb in (muku.get('tombs') or [])}
    for i in range(4):
        if _pillar_has_cat(day_gan, gans[i], zhis[i], '比劫') and zhis[i] in tombs_zhis:
            if any(a.get('type') == '冲' and (a.get('from_pos') == f'{PILLAR_KEYS[i]}_zhi'
                   or a.get('to_pos') == f'{PILLAR_KEYS[i]}_zhi') for a in wa):
                markers.append(f'比劫坐{zhis[i]}墓逢冲（手足早夭）')
                break

    # 三刑损兄弟
    if any(a.get('type') == '刑' for a in wa):
        markers.append('三刑夹刑（损兄弟）')

    # 羊刃逢冲
    try:
        ss = compute_shensha_ext(day_gan, zhis)
        yr = (ss.get('羊刃') or {}).get('zhi', '')
        if yr and yr in zhis:
            yr_pillar = zhis.index(yr)
            if any(a.get('type') == '冲' and (a.get('from_pos') == f'{PILLAR_KEYS[yr_pillar]}_zhi'
                   or a.get('to_pos') == f'{PILLAR_KEYS[yr_pillar]}_zhi') for a in wa):
                markers.append('羊刃逢冲（必应凶）')
    except Exception:
        pass

    # 比劫入空亡
    for i in range(4):
        if i == 2:
            continue
        if _pillar_has_cat(day_gan, gans[i], zhis[i], '比劫') and zhis[i] in kong_wang_zhis:
            markers.append('比劫入空亡（独雁孤飞）')
            break

    has_keshun = bool(markers)
    return {
        'has_keshun': has_keshun,
        'markers': markers,
        'desc': '；'.join(markers) if markers else '无明显兄弟克损标志',
    }


# ───────────────────── 聚合 ─────────────────────

def analyze_liuqin(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    gender: str = '男',
    *,
    relations: Optional[Dict] = None,
) -> Dict:
    """六亲综合：父母定位/早逝/多婚/弃养 + 子息有无/性别 + 兄弟姐妹数量/克损。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'parent_star': {...}, 'parent_zaoshi': {...}, 'parent_duohun': {...},
          'parent_qiyang': {...},
          'zixi_youwu': {...}, 'zixi_xingbie': {...},
          'xiongdi_shuliang': {...}, 'xiongdi_keshun': {...},
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
        return {'summary': '四柱不全，无法判定六亲'}

    pstar = classify_parent_star(day_gan, gans, zhis)
    pzs = detect_parent_zaoshi(day_gan, gans, zhis, relations)
    pdh = detect_parent_duohun(day_gan, gans, zhis, relations)
    pqy = detect_parent_qiyang(day_gan, gans, zhis, relations)
    zx_yw = detect_zixi_youwu(day_gan, gans, zhis, gender, relations)
    zx_xb = detect_zixi_xingbie(day_gan, gans, zhis, gender, relations)
    xd_sl = classify_xiongdi_shuliang(day_gan, gans, zhis, relations)
    xd_ks = detect_xiongdi_keshun(day_gan, gans, zhis, relations)

    parts = ['六亲论断']
    if pzs.get('is_zaoshi'):
        parts.append('父母早逝之象')
    if pdh.get('is_duohun'):
        parts.append('父母多婚之象')
    if pqy.get('is_qiyang'):
        parts.append('父母弃养之象')
    if not zx_yw.get('has_zixi'):
        parts.append('子息有阻')
    if zx_xb.get('final_gender'):
        parts.append(f'头胎{zx_xb["final_gender"]}')
    if xd_ks.get('has_keshun'):
        parts.append('兄弟有克损')
    parts.append(f'兄弟约{xd_sl.get("estimate", 0)}个')

    return {
        'parent_star': pstar,
        'parent_zaoshi': pzs,
        'parent_duohun': pdh,
        'parent_qiyang': pqy,
        'zixi_youwu': zx_yw,
        'zixi_xingbie': zx_xb,
        'xiongdi_shuliang': xd_sl,
        'xiongdi_keshun': xd_ks,
        'summary': '；'.join(parts),
    }


__all__ = [
    'classify_parent_star',
    'detect_parent_zaoshi',
    'detect_parent_duohun',
    'detect_parent_qiyang',
    'detect_zixi_youwu',
    'detect_zixi_xingbie',
    'classify_xiongdi_shuliang',
    'detect_xiongdi_keshun',
    'analyze_liuqin',
]
