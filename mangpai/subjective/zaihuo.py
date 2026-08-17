"""
zaihuo - 盲派灾祸专辑·主观层（subjective）

理论来源：段建业《盲派命理高级内容篇》第十一章「灾祸专题」（源文 14818-16567 行）
核心思想：灾祸非偶然，命局必有凶险组合潜伏待发。三类灾祸合一论断，各有其象：

三类判定（高级篇第十一章，11.1 牢狱归 laoyu 模块，本模块论 11.2-11.4）：
  1. 疾病（11.2）：穿害破刑 → 五行病机。六穿各主其脏（子未穿脾胃/丑午穿心/
     寅巳穿胆神经/卯辰穿肝腹/申亥穿胫足肾/酉戌穿肺眼）；六破（卯午破血管、
     子酉破精血）；三刑（寅巳申神经肝胆筋骨、丑未戌脾胃皮肤、子卯肝肾泌尿）。
     五行病机：金=肺呼吸、木=肝胆、水=肾泌尿血、火=心血、土=脾胃。特殊病：
     糖尿=土浊水、白血=火克金（金主骨髓）、尿毒=亥子绝寅、精神=酉戌穿/双丁、
     癌=阴阳战+穿破带墓。
  2. 车祸（11.3）：车象（辰丑申酉子，辰丑=车身/申酉=金属车/子=轮转）+ 盲派
     多马星（三合局对冲方及墓库方皆马）+ 穿冲触发（酉戌穿/寅巳穿/卯酉冲/子午
     冲/辰戌冲）。应期：禄身被冲穿、凶神汇聚。
  3. 死亡（11.4）：寿元星三级（第一食神、第二印、第三日主/禄）+ 墓绝空亡。
     寿星遭刑破穿害克绝、禄神被冲穿破入墓、羊刃逢冲、寿星入墓墓被冲开、
     寿星/禄见绝地、寿元落空亡+运岁冲实。三者合见「神仙难救」。

消费关系：
  - objective.constants（五行生克/穿破刑冲/禄/墓库）
  - objective.canggan.get_canggan_mangpai（藏干，寿元星定位）
  - objective.zuogong_detect.detect_relations（穿破刑冲合，疾病/车祸/死亡触发）
  - objective.shensha.compute_shensha_ext（凶性三煞：亡神/劫煞/灾煞；多马星；羊刃）
  - objective.muku.analyze_muku（墓库开闭，寿星入墓/官杀入墓）
  - objective.changsheng.get_changsheng_mangpai（绝地，寿星见绝）
  - subjective.yunfan.analyze_yunfan（岁运反局联动，灾祸急性触发：天地合/三刑/双冲）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：五行病机/穿害主脏为盲师口传归纳（非精确解剖映射）；死亡判定高度
          敏感，本模块给风险标志不给断言；寿元星三级取用顺序各师有先后分歧。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    LU, LIU_HAI, LIU_PO, XING_PAIRS, LIU_CHONG, LIU_HE,
    CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, DI_ZHI, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext, resolve_shensha
from mangpai.objective.muku import analyze_muku
from mangpai.objective.changsheng import get_changsheng_mangpai
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.yongshen import assess_direction_signals, direction_brief

_YANG_GANS = set('甲丙戊庚壬')
_YANG_GAN_OF_WX = {'木': '甲', '火': '丙', '土': '戊', '金': '庚', '水': '壬'}

# 五行 → 脏腑/部位
_WX_ORGAN = {
    '金': '肺/呼吸/大肠/齿',
    '木': '肝胆/筋/神经',
    '水': '肾/泌尿/血/耳',
    '火': '心/血/眼/舌',
    '土': '脾/胃/肌肉/皮肤',
}

# 六穿 → 主病（源文 15404-15413）
_HAI_DISEASE = {
    frozenset({'子', '未'}): '脾胃/腹疾',
    frozenset({'丑', '午'}): '心脏/心慌/妇科/肾',
    frozenset({'寅', '巳'}): '胆/神经/面齿',
    frozenset({'卯', '辰'}): '肝/腹/腰肠',
    frozenset({'申', '亥'}): '胫足/肾阴',
    frozenset({'酉', '戌'}): '肺/眼/心包/神经',
}

# 六破 → 主病（源文 15468-15471）
_PO_DISEASE = {
    frozenset({'子', '酉'}): '精血/肺/泌尿',
    frozenset({'丑', '辰'}): '脾/皮肤/湿',
    frozenset({'寅', '亥'}): '肝/风湿',
    frozenset({'卯', '午'}): '血管/心出血/脑溢',
    frozenset({'巳', '申'}): '神经/筋骨',
    frozenset({'未', '戌'}): '胃/命门/燥',
}

# 三刑 → 主病（源文 15221-15223）
_XING_DISEASE = {
    frozenset({'寅', '巳', '申'}): '神经/肝胆/筋骨',
    frozenset({'丑', '未', '戌'}): '脾胃/皮肤/肌肉顽疾',
    frozenset({'子', '卯'}): '肝肾/泌尿/生殖',
}

# 车象地支（源文 15785-15787）
_CHE_ZHIS = {'辰', '丑', '申', '酉', '子'}


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


def _wx_counts(day_gan: str, gans: List[str], zhis: List[str]) -> Dict[str, int]:
    """四柱五行计数（天干+地支本/中气藏干）。"""
    cnt: Dict[str, int] = {w: 0 for w in _WX_ORGAN}
    for g in gans:
        w = GAN_WX.get(g, '')
        if w:
            cnt[w] = cnt.get(w, 0) + 1
    for z in zhis:
        w = ZHI_WX.get(z, '')
        if w:
            cnt[w] = cnt.get(w, 0) + 1
        for idx, (cg, _) in enumerate(get_canggan_mangpai(z)):
            if idx <= 1:
                cw = GAN_WX.get(cg, '')
                if cw:
                    cnt[cw] = cnt.get(cw, 0) + 1
    return cnt


def _jue_zhis_of_wx(wx: str) -> Set[str]:
    """某五行的绝地地支（取该五行阳干的十二长生绝位）。"""
    ag = _YANG_GAN_OF_WX.get(wx)
    if not ag:
        return set()
    return {z for z in DI_ZHI if get_changsheng_mangpai(ag, z) == '绝'}


def _tomb_zhis_of_wx(wx: str) -> Set[str]:
    """收某五行的墓库地支。"""
    m = {'木': {'未'}, '火': {'戌'}, '金': {'丑'}, '水': {'辰'}, '土': {'辰'}}
    return m.get(wx, set())


# ───────────────────── 1. 疾病 ─────────────────────

def classify_jibing(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """疾病论断（11.2）：穿害破刑 + 五行病机 + 特殊病。

    Returns:
        {
          'chuan_hai': [str],   # 穿害主病
          'po': [str],          # 破主病
          'xing': [str],        # 刑主病
          'wx_bingji': [str],   # 五行病机
          'special': [str],     # 特殊病（糖尿/白血/尿毒/精神/癌）
          'organs': [str],      # 易病脏腑汇总
          'risk': '高'|'中'|'低'|'无',
          'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    zhi_set = [z for z in zhis if z]

    chuan_hai: List[str] = []
    po: List[str] = []
    xing: List[str] = []

    # 穿害
    for a in wa:
        if a.get('type') != '穿':
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        fz = zhis[PILLAR_KEYS.index(fp.split('_')[0])] if fp.split('_')[0] in PILLAR_KEYS else ''
        tz = zhis[PILLAR_KEYS.index(tp.split('_')[0])] if tp.split('_')[0] in PILLAR_KEYS else ''
        if fz and tz:
            d = _HAI_DISEASE.get(frozenset({fz, tz}))
            if d and d not in chuan_hai:
                chuan_hai.append(d)

    # 破
    for a in wa:
        if a.get('type') != '破':
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        fz = zhis[PILLAR_KEYS.index(fp.split('_')[0])] if fp.split('_')[0] in PILLAR_KEYS else ''
        tz = zhis[PILLAR_KEYS.index(tp.split('_')[0])] if tp.split('_')[0] in PILLAR_KEYS else ''
        if fz and tz:
            d = _PO_DISEASE.get(frozenset({fz, tz}))
            if d and d not in po:
                po.append(d)

    # 刑
    present = set(zhi_set)
    for pair, d in _XING_DISEASE.items():
        if pair <= present:
            xing.append(d)

    # 五行病机
    cnt = _wx_counts(day_gan, gans, zhis)
    wx_bingji: List[str] = []
    for w, organ in _WX_ORGAN.items():
        ke_me = WX_KE_ME.get(w, '')  # 克我者
        if cnt.get(ke_me, 0) >= 2 and cnt.get(w, 0) >= 1:
            wx_bingji.append(f'{ke_me}旺克{w}（{organ}疾）')
        elif cnt.get(w, 0) >= 4:
            wx_bingji.append(f'{w}过旺（{organ}亢盛）')

    # 特殊病
    special: List[str] = []
    # 糖尿病：土浊水（土旺克水）
    if cnt.get('土', 0) >= 2 and cnt.get('土', 0) > cnt.get('水', 0) and cnt.get('水', 0) >= 1:
        special.append('糖尿病（土浊水）')
    # 白血病：火克金（金主骨髓）
    if cnt.get('火', 0) >= 2 and cnt.get('金', 0) >= 1 and WX_KE.get('火') == '金':
        special.append('血病（火克金，金主骨髓）')
    # 尿毒：亥子水绝寅木
    if {'亥', '子'} & present and '寅' in present and cnt.get('水', 0) >= 2:
        special.append('尿毒（亥子水绝寅木）')
    # 精神病：酉戌穿 或 双丁透干
    # F1 批拆 for-in-[0] 死壳（any(X for _ in [0])≡X，批7 审计）。
    if frozenset({'酉', '戌'}) <= {zhis[i] for i in range(4)}:
        if frozenset({'酉', '戌'}) <= present and any(a.get('type') == '穿' for a in wa):
            special.append('精神病（酉戌穿）')
    if sum(1 for g in gans if g == '丁') >= 2:
        special.append('精神病（双丁透干神经乱）')
    # 癌：阴阳战 + 穿破带墓
    all_yang = all((g in _YANG_GANS if g else True) for g in gans) and \
               all((z in set('子寅辰午申戌') if z else True) for z in zhis)
    all_yin = all((g not in _YANG_GANS if g else True) for g in gans) and \
              all((z in set('丑卯巳未酉亥') if z else True) for z in zhis)
    has_chuan_po = any(a.get('type') in ('穿', '破') for a in wa)
    try:
        muku = analyze_muku(zhis, gans)
        has_mu = bool(muku.get('tombs'))
    except Exception:
        has_mu = False
    if (all_yang or all_yin) and has_chuan_po and has_mu:
        special.append('癌症（阴阳战+穿破带墓）')

    # 脏腑汇总
    organs = list(dict.fromkeys(chuan_hai + po + xing +
                                [s.split('（')[0] for s in wx_bingji]))

    n = len(chuan_hai + po + xing) + len(special)
    risk = '高' if n >= 3 else ('中' if n == 2 else ('低' if n == 1 else '无'))

    parts = []
    if chuan_hai:
        parts.append('穿害：' + '、'.join(chuan_hai))
    if po:
        parts.append('破：' + '、'.join(po))
    if xing:
        parts.append('刑：' + '、'.join(xing))
    if wx_bingji:
        parts.append('、'.join(wx_bingji))
    if special:
        parts.append('特殊病：' + '、'.join(special))

    return {
        'chuan_hai': chuan_hai, 'po': po, 'xing': xing,
        'wx_bingji': wx_bingji, 'special': special, 'organs': organs,
        'risk': risk,
        'desc': '；'.join(parts) if parts else '无明显疾病标志',
    }


# ───────────────────── 2. 车祸 ─────────────────────

def detect_chehuo(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """车祸论断（11.3）：车象 + 多马星 + 穿冲触发。

    车象五支：辰丑申酉子。盲派多马星（compute_shensha_ext 马星在局马数，
    F13 起消费 in_pillars 而非并集 count）。
    触发：穿（酉戌/寅巳/丑午）冲（卯酉/子午/寅申/辰戌）落于车象或马星支；
    禄身受损（日主禄被冲穿）；凶神汇聚（七杀/羊刃/劫煞/亡神+车象）。

    Returns:
        {
          'che_xiang': [str], 'ma_count': int, 'triggers': [str],
          'lu_damaged': bool, 'xiong_shen': [str],
          'risk': '高'|'中'|'低'|'无', 'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    # 车象
    che_xiang = [z for z in zhis if z in _CHE_ZHIS]

    # 多马星——F13 改消费在局马数（in_pillars）：供给层 'count'=并集马支数
    # 恒≥3（批8 实锤死判据），在局马数（马支实际落柱）才有判别力。
    try:
        ss = resolve_shensha(day_gan, zhis, shensha_result)
        ma_count = len((ss.get('马星') or {}).get('in_pillars') or [])
    except Exception:
        ss = {}
        ma_count = 0

    # 触发：穿/冲 涉车象支
    triggers: List[str] = []
    che_set = set(che_xiang)
    for a in wa:
        t = a.get('type', '')
        if t not in ('穿', '冲'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        fkey = fp.split('_')[0]
        tkey = tp.split('_')[0]
        if fkey in PILLAR_KEYS and tkey in PILLAR_KEYS:
            fz = zhis[PILLAR_KEYS.index(fkey)]
            tz = zhis[PILLAR_KEYS.index(tkey)]
            if fz in che_set or tz in che_set:
                label = f'{fz}{tz}{t}'
                if label not in triggers:
                    triggers.append(label)

    # 禄身受损
    lu_zhi = LU.get(day_gan, '')
    lu_damaged = False
    if lu_zhi and lu_zhi in zhis:
        li = zhis.index(lu_zhi)
        for a in wa:
            if a.get('type') in ('冲', '穿', '破') and \
               (a.get('from_pos') == f'{PILLAR_KEYS[li]}_zhi' or
                a.get('to_pos') == f'{PILLAR_KEYS[li]}_zhi'):
                lu_damaged = True
                break

    # 凶神汇聚
    xiong_shen: List[str] = []
    if any(_cat(_compute_shishen(day_gan, g)) == '官杀' for g in gans if g):
        xiong_shen.append('七杀')
    # F13：羊刃用全刃表口径（in_pillars 已按 _YANG_REN_FULL 检出，
    # 戊日刃在未盘旧 zhi 单值 '午' 漏检——理象学:2086 戊刃在午、未）
    if ss and (ss.get('羊刃') or {}).get('in_pillars'):
        xiong_shen.append('羊刃')
    for key in ('劫煞', '亡神'):
        v = ss.get(key) if ss else None
        if v and (v.get('in_pillars') or
                  (isinstance(v.get('day_ref'), dict) and v['day_ref'].get('in_pillars'))):
            xiong_shen.append(key)

    score = 0
    if len(che_xiang) >= 2:
        score += 1
    if ma_count >= 1:
        score += 1
    if triggers:
        score += 1
    if lu_damaged:
        score += 1
    if xiong_shen:
        score += 1
    risk = '高' if score >= 4 else ('中' if score == 3 else ('低' if score >= 1 else '无'))

    parts = []
    if che_xiang:
        parts.append(f'车象{"、".join(che_xiang)}({len(che_xiang)}字)')
    if ma_count:
        parts.append(f'马星{ma_count}颗')
    if triggers:
        parts.append('触发：' + '、'.join(triggers))
    if lu_damaged:
        parts.append('禄身被冲穿')
    if xiong_shen:
        parts.append('凶神：' + '、'.join(xiong_shen))

    return {
        'che_xiang': che_xiang, 'ma_count': ma_count, 'triggers': triggers,
        'lu_damaged': lu_damaged, 'xiong_shen': xiong_shen, 'risk': risk,
        'desc': '；'.join(parts) if parts else '无明显车祸标志',
    }


# ───────────────────── 3. 死亡 ─────────────────────

def _find_star_pillars(day_gan: str, gans: List[str], zhis: List[str], cat: str) -> List[int]:
    """某十神大类所在柱索引。"""
    out: List[int] = []
    for i in range(4):
        hit = _cat(_compute_shishen(day_gan, gans[i])) == cat
        if not hit:
            zw = ZHI_WX.get(zhis[i], '')
            if zw and _wx_cat(day_gan, zw) == cat:
                hit = True
            else:
                for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                    if idx <= 1 and _cat(_compute_shishen(day_gan, cg)) == cat:
                        hit = True
                        break
        if hit:
            out.append(i)
    return out


def _star_wx(day_gan: str, cat: str) -> str:
    day_wx = GAN_WX.get(day_gan, '')
    if cat == '食伤':
        return WX_SHENG.get(day_wx, '')
    if cat == '印':
        for w, child in WX_SHENG.items():
            if child == day_wx:
                return w
    if cat == '比劫':
        return day_wx
    return ''


def detect_siwang(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """死亡风险论断（11.4）：寿元星三级 + 墓绝空亡 + 凶性三煞 + 禄刃损伤。

    寿元星三级（源文 16154-16160）：第一食神、第二印、第三日主/禄。
    按命局所现之星取最高级为寿元星，判其刑破穿害/入墓/见绝/空亡。
    墓绝空亡三者合见为最凶。凶性三煞（亡神/劫煞/灾煞）并空亡为凶兆。
    yunfan_result（岁运反局联动：天地合/三刑/双冲）为急性触发。

    Returns:
        {
          'shouyuan_cat': str, 'shouyuan_tier': int,
          'markers': [str], 'mu_jue_kong': [str],
          'xiong_sha': [str], 'yunfan_trigger': bool,
          'risk': '高'|'中'|'低'|'无', 'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    kong_wang_zhis = set(rel.get('kong_wang_zhis') or [])

    # 寿元星三级
    tiers = [('食伤', 1), ('印', 2), ('比劫', 3)]
    shouyuan_cat = ''
    shouyuan_tier = 0
    shouyuan_pillars: List[int] = []
    for cat, tier in tiers:
        ps = _find_star_pillars(day_gan, gans, zhis, cat)
        if ps:
            shouyuan_cat = cat
            shouyuan_tier = tier
            shouyuan_pillars = ps
            break
    # 禄（第三级辅助）
    lu_zhi = LU.get(day_gan, '')
    lu_pillar = zhis.index(lu_zhi) if lu_zhi and lu_zhi in zhis else -1

    markers: List[str] = []
    mu_jue_kong: List[str] = []

    if not shouyuan_cat:
        markers.append('原局无食伤/印/比劫寿元星（寿元待运岁）')
    else:
        swx = _star_wx(day_gan, shouyuan_cat)
        # 1. 寿元星遭刑破穿害
        for i in shouyuan_pillars:
            kinds = []
            for a in wa:
                t = a.get('type', '')
                if t in ('刑', '破', '穿', '冲') and \
                   (a.get('from_pos') == f'{PILLAR_KEYS[i]}_zhi' or
                    a.get('to_pos') == f'{PILLAR_KEYS[i]}_zhi' or
                    a.get('from_pos') == f'{PILLAR_KEYS[i]}_gan' or
                    a.get('to_pos') == f'{PILLAR_KEYS[i]}_gan'):
                    if t not in kinds:
                        kinds.append(t)
            if kinds:
                markers.append(f'寿元星（{shouyuan_cat}）{PILLAR_NAMES_CN[i]}柱遭{"、".join(kinds)}')

        # 2. 寿元星入墓 / 墓被冲开
        try:
            muku = analyze_muku(zhis, gans)
        except Exception:
            muku = {}
        tombs = muku.get('tombs') or []
        open_tombs = {t.get('zhi') for t in (muku.get('open_tombs') or [])}
        closed_tombs = {t.get('zhi') for t in (muku.get('closed_tombs') or [])}
        star_tombs = _tomb_zhis_of_wx(swx) if swx else set()
        for z in star_tombs:
            if z in closed_tombs:
                mu_jue_kong.append(f'寿元星（{swx}）入{z}墓不开')
            if z in open_tombs:
                mu_jue_kong.append(f'寿元星（{swx}）入{z}墓被冲开（寿终之兆）')

        # 3. 寿元星见绝地
        jue_zhis = _jue_zhis_of_wx(swx) if swx else set()
        present = set(z for z in zhis if z)
        if jue_zhis & present:
            mu_jue_kong.append(f'寿元星（{swx}）见绝地{"".join(sorted(jue_zhis & present))}')

        # 4. 寿元星/禄落空亡
        for i in shouyuan_pillars:
            if zhis[i] in kong_wang_zhis:
                mu_jue_kong.append(f'寿元星{PILLAR_NAMES_CN[i]}支落空亡')

    # 禄刃损伤
    if lu_pillar >= 0:
        for a in wa:
            t = a.get('type', '')
            if t in ('冲', '穿', '破') and \
               (a.get('from_pos') == f'{PILLAR_KEYS[lu_pillar]}_zhi' or
                a.get('to_pos') == f'{PILLAR_KEYS[lu_pillar]}_zhi'):
                markers.append(f'禄神（{lu_zhi}）遭{t}')
                break
        # 禄入墓
        try:
            muku2 = analyze_muku(zhis, gans)
            lu_wx = GAN_WX.get(day_gan, '')
            for z in _tomb_zhis_of_wx(lu_wx):
                if z in {t.get('zhi') for t in (muku2.get('open_tombs') or [])} and lu_zhi in zhis:
                    markers.append(f'禄神入{z}墓被冲开')
        except Exception:
            pass

    # 凶性三煞（亡神/劫煞/灾煞）并空亡
    try:
        ss = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        ss = {}
    xiong_sha: List[str] = []
    for key in ('亡神', '劫煞', '灾煞'):
        v = ss.get(key)
        if not v:
            continue
        in_p = v.get('in_pillars') or []
        if isinstance(v.get('day_ref'), dict):
            in_p = in_p + v['day_ref'].get('in_pillars', [])
        if in_p:
            xiong_sha.append(key)
    if xiong_sha and kong_wang_zhis:
        markers.append(f'凶性三煞（{"、".join(xiong_sha)}）并空亡')

    # yunfan 岁运联动急性触发
    yunfan_trigger = False
    if yunfan_result:
        ld = yunfan_result.get('sui_yun_liandong') or []
        if ld:
            yunfan_trigger = True
            markers.append(f'岁运反局联动{len(ld)}处（天地合/三刑/双冲，急性触发）')

    # 风险：墓绝空亡合见为最高
    risk = '无'
    if (mu_jue_kong and any('墓被冲开' in m or '见绝' in m or '空亡' in m for m in mu_jue_kong)
            and len(mu_jue_kong) >= 2):
        risk = '高'
    elif len(mu_jue_kong) >= 1 or yunfan_trigger or (xiong_sha and kong_wang_zhis):
        risk = '中'
    elif markers:
        risk = '低'

    parts = []
    if shouyuan_cat:
        parts.append(f'寿元星：{shouyuan_cat}（第{shouyuan_tier}级）')
    parts.extend(markers)
    parts.extend(mu_jue_kong)

    return {
        'shouyuan_cat': shouyuan_cat, 'shouyuan_tier': shouyuan_tier,
        'markers': markers, 'mu_jue_kong': mu_jue_kong,
        'xiong_sha': xiong_sha, 'yunfan_trigger': yunfan_trigger,
        'risk': risk,
        'desc': '；'.join(parts) if parts else '无明显寿元损伤标志',
    }


# ───────────────────── 聚合 ─────────────────────

def analyze_zaihuo(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    direction_result: Optional[Dict] = None,
) -> Dict:
    """灾祸综合：疾病 + 车祸 + 死亡。
    A3：接入 yongshen 方向总线（direction_result 缺省自调，只读信号不改判定）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'jibing': {...}, 'chehuo': {...}, 'siwang': {...},
          'max_risk': '高'|'中'|'低'|'无', 'summary': str,
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
        return {'max_risk': '无', 'summary': '四柱不全，无法判定灾祸'}

    # 神煞：优先用 engine 透传值，缺省才就地重算（凶性三煞/多马星/羊刃）
    ss = resolve_shensha(day_gan, zhis, shensha_result)

    jb = classify_jibing(day_gan, gans, zhis, relations)
    ch = detect_chehuo(day_gan, gans, zhis, relations, shensha_result=ss)
    sw = detect_siwang(day_gan, gans, zhis, relations, yunfan_result,
                       shensha_result=ss)

    # A3：方向总线信号（缺省自调；zaihuo 已自有 yunfan 切片，透传一致口径）
    if direction_result is None:
        try:
            direction_result = assess_direction_signals(
                day_gan, gans, zhis, relations=relations,
                yunfan_result=yunfan_result)
        except Exception:
            direction_result = {}

    order = {'高': 3, '中': 2, '低': 1, '无': 0}
    max_risk = max([jb['risk'], ch['risk'], sw['risk']], key=lambda r: order.get(r, 0))

    parts = [f'灾祸总风险{max_risk}']
    if jb['risk'] != '无':
        parts.append(f'疾病{jb["risk"]}({jb["desc"][:20]})')
    if ch['risk'] != '无':
        parts.append(f'车祸{ch["risk"]}')
    if sw['risk'] != '无':
        parts.append(f'死亡{sw["risk"]}')

    return {
        'jibing': jb,
        'chehuo': ch,
        'siwang': sw,
        'max_risk': max_risk,
        'direction_signals': direction_brief(direction_result),
        'summary': '；'.join(parts),
    }


__all__ = [
    'classify_jibing',
    'detect_chehuo',
    'detect_siwang',
    'analyze_zaihuo',
]
