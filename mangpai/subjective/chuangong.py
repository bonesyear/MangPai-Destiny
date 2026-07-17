"""
chuangong — 串宫压运（同一地支多柱串联 + 岁运压入互动）·主观层

理论来源：段建业《段氏理象学》岁运篇、盲师口传体系。
  （需求文档：mangpai/docs/chuangong-spec.md）

核心思想：
  串宫：同一地支出现于命局两个或以上柱位（年月日时），该地支主题在人生的
        多领域串联。2 次为弱串（两个领域关联）、3 次为强串（贯穿大半个命局）、
        4 次为全串（覆盖一生所有阶段，极强信号）。
  压运：大运或流年地支压入命局，与已有串宫链或命局地支互动：
        - 压入支命中已有串宫链（命局 ≥2 次）→ 增强，该主题被岁运放大
        - 压入支在命局仅 1 次 → 触发新串宫（原支 + 运支形成 2 支串联）
        - 压入支在命局 0 次 → 纯新增主题（压运引入）
        - 与已有串宫地支相冲 → 冲散串宫；六合 → 合化串宫；三合半合 → 会局增强

分层说明：
  本模块为纯结构检测（出现次数 + 冲合会关系），不做吉凶判断。
  按第三期规划置于 subjective/（objective←subjective 单向依赖，引擎接线
  属后续期次；本模块独立可用，不改任何核心判定逻辑）。
置信度：高（检测规则确定性）。
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    DI_ZHI, LIU_CHONG, LIU_HE, SAN_HE, BAN_HE, PILLAR_KEYS,
)

__all__ = ['analyze_chuangong']

_PILLAR_LABELS = ['年柱', '月柱', '日柱', '时柱']
_PILLAR_SHORT = ['年', '月', '日', '时']

# ── 地支主题映射（chuangong-spec.md 第 4 节）──
ZHI_THEME: Dict[str, str] = {
    '子': '水智/暗流', '丑': '土库/蓄藏', '寅': '木生/开创', '卯': '木秀/文采',
    '辰': '水库/变局', '巳': '火变/转折', '午': '火明/巅峰', '未': '木库/收藏',
    '申': '金革/更替', '酉': '金精/结果', '戌': '火库/终结', '亥': '水藏/孕育',
}

_LEVEL_BY_COUNT = {2: '弱串', 3: '强串', 4: '全串'}


def _in_pairs(a: str, b: str, pairs) -> bool:
    """a-b 是否命中关系对（无序）。"""
    return (a, b) in pairs or (b, a) in pairs


def _sanhe_banhe(a: str, b: str) -> bool:
    """a-b 是否同属某三合局/半合组合（会局）。"""
    for trio in SAN_HE:
        if a in trio and b in trio:
            return True
    for duo in BAN_HE:
        if a in duo and b in duo:
            return True
    return False


def _extract_zhi(gz: str) -> str:
    """从干支字符串提取地支（第二位）。非法输入返回 ''。"""
    if isinstance(gz, str) and len(gz) >= 2 and gz[1] in DI_ZHI:
        return gz[1]
    return ''


def _detect_chains(natal_zhis: List[str]) -> Dict[str, Dict]:
    """统计串宫链：同一地支出现 ≥2 次。natal_zhis 已剔除空亡。"""
    chains: Dict[str, Dict] = {}
    for idx, zhi in enumerate(natal_zhis):
        if not zhi:
            continue
        chain = chains.setdefault(zhi, {'count': 0, '_idx': []})
        chain['count'] += 1
        chain['_idx'].append(idx)
    result: Dict[str, Dict] = {}
    for zhi, chain in chains.items():
        if chain['count'] < 2:
            continue
        idxs = chain['_idx']
        result[zhi] = {
            'count': chain['count'],
            'level': _LEVEL_BY_COUNT.get(chain['count'], '全串'),
            'positions': [_PILLAR_LABELS[i] for i in idxs],
            'theme': ZHI_THEME.get(zhi, ''),
            'pillars': [PILLAR_KEYS[i] for i in idxs],
        }
    return result


def _yayun_hit(zhi: str, gz: str, index: int, natal_zhis: List[str],
               chains: Dict[str, Dict], prefix: str) -> Optional[Dict]:
    """单步运/年压入分析。prefix='dayun'|'liunian'，决定返回键名。"""
    if not zhi:
        return None
    natal_count = natal_zhis.count(zhi)
    if natal_count >= 2:
        hit_type = '增强'
        pos = '-'.join(_PILLAR_SHORT[i] for i, z in enumerate(natal_zhis) if z == zhi)
        detail = f'压入{zhi}支增强{pos}串宫链'
    elif natal_count == 1:
        hit_type = '触发'
        pos = _PILLAR_SHORT[natal_zhis.index(zhi)]
        detail = f'压入{zhi}支触发新串宫（原{pos}位+运位）'
    else:
        hit_type = '引入'
        detail = f'压入{zhi}支引入新主题（{ZHI_THEME.get(zhi, "")}）'

    # 与已有串宫链地支的冲/合/会关系（跳过与自身同支的链）
    conflict: Dict[str, str] = {}
    notes: List[str] = []
    for chain_zhi in chains:
        if chain_zhi == zhi:
            continue
        if _in_pairs(zhi, chain_zhi, LIU_CHONG):
            conflict['冲'] = chain_zhi
            notes.append(f'冲散{chain_zhi}串宫')
        elif _in_pairs(zhi, chain_zhi, LIU_HE):
            conflict['合'] = chain_zhi
            notes.append(f'合化{chain_zhi}串宫')
        elif _sanhe_banhe(zhi, chain_zhi):
            conflict['会'] = chain_zhi
            notes.append(f'会局增强{chain_zhi}串宫')
    if notes:
        detail += '；' + '，'.join(notes)

    return {
        f'{prefix}_index': index,
        f'{prefix}_gz': gz,
        'zhi': zhi,
        'type': hit_type,
        'detail': detail,
        'conflict': conflict or None,
    }


def analyze_chuangong(
    year_zhi: str,
    month_zhi: str,
    day_zhi: str,
    hour_zhi: str,
    dayun_list: Optional[List[Dict]] = None,
    liunian_list: Optional[List[Dict]] = None,
    kong_wang: Optional[List[str]] = None,
) -> Dict:
    """串宫压运分析。

    参数：
      year/month/day/hour_zhi — 四柱地支（如 '子'）
      dayun_list — 大运列表，每项 {'gz': '甲子', ...}；None 则仅串宫不压运
      liunian_list — 流年列表，同构；None 则不分析流年
      kong_wang — 空亡地支列表，串宫统计中排除

    返回：见 docs/chuangong-spec.md「返回结构」节。
    """
    kw = set(kong_wang or [])
    natal_zhis = [z for z in (year_zhi, month_zhi, day_zhi, hour_zhi)
                  if z in DI_ZHI and z not in kw]

    chains = _detect_chains(natal_zhis)

    yayun_hits: List[Dict] = []
    for i, dy in enumerate(dayun_list or []):
        gz = (dy or {}).get('gz', '')
        hit = _yayun_hit(_extract_zhi(gz), gz, i, natal_zhis, chains, 'dayun')
        if hit:
            yayun_hits.append(hit)

    yayun_liunian: List[Dict] = []
    for i, ln in enumerate(liunian_list or []):
        gz = (ln or {}).get('gz', '')
        hit = _yayun_hit(_extract_zhi(gz), gz, i, natal_zhis, chains, 'liunian')
        if hit:
            yayun_liunian.append(hit)

    # ── summary（中文简洁）──
    parts: List[str] = []
    if chains:
        chain_desc = '，'.join(
            f"{zhi}({c['level']},{'/'.join(_PILLAR_SHORT[PILLAR_KEYS.index(p)] for p in c['pillars'])})"
            for zhi, c in chains.items()
        )
        parts.append(f'命局串宫：{chain_desc}')
    else:
        parts.append('命局无串宫')
    for hit in yayun_hits:
        parts.append(f"大运{hit['dayun_gz']}{hit['type']}{hit['zhi']}支")
    for hit in yayun_liunian:
        parts.append(f"流年{hit['liunian_gz']}{hit['type']}{hit['zhi']}支")

    return {
        'chuangong_chains': chains,
        'yayun_hits': yayun_hits,
        'yayun_liunian': yayun_liunian,
        'summary': '；'.join(parts),
        'chuangong_count': len(chains),
        'has_severe_chuangong': any(c['count'] >= 3 for c in chains.values()),
    }
