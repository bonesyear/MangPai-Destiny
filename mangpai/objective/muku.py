"""
muku — 盲派墓库规则

理论来源：《渊海子平》墓库篇 + 盲师口传墓库体系
核心思想：墓库是盲派重要的做功手段。
  木墓在未, 火墓在戌, 金墓在丑, 水墓在辰, 土墓在辰（盲派）
  开库：墓库逢冲或刑则开（段氏「不冲不刑是墓（死的）」），开则可用
  闭库：墓库逢合则闭，闭则不可用
  多而入墓：同类多则入墓
  透干引拔：墓库透干则引出
  坐墓不墓：自坐墓库不入墓
已知争议：土墓在辰有争议，部分流派认为土无墓或土墓在戌
⚠ 设计决策：己土墓位双轨并存——
  · changsheng.py 用火土同宫（己长生寅 → 墓在戌），管长生效率折扣
  · muku.py 用《五行精纪》戊寄戌己寄辰（己墓在辰），管天干入墓
  · 两套体系各司其职，不是 bug，详见 CHANGELOG「己土墓位分歧」
置信度：中
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    DI_ZHI, WU_XING_DZ, TOMB_MAP, LIU_CHONG, LIU_HE, XING_PAIRS,
    ZHI_WX, GAN_WX, SI_SHENG, SI_ZHENG, is_pillars,
)

_PILLAR_NAMES = ['年柱', '月柱', '日柱', '时柱']


def _is_chong(a: str, b: str) -> bool:
    return (a, b) in LIU_CHONG or (b, a) in LIU_CHONG


def _is_he(a: str, b: str) -> bool:
    return (a, b) in LIU_HE or (b, a) in LIU_HE


def _is_xing(a: str, b: str) -> bool:
    # XING_PAIRS 三刑已含寅巳申/丑戌未环向三组，唯子卯单列单向，故双向判定。
    return (a, b) in XING_PAIRS or (b, a) in XING_PAIRS


def _is_tomb_opened(tomb_zhi: str, all_zhis: List[str]) -> bool:
    """墓库是否被他支冲或刑开（段氏「不冲不刑是墓（死的）」，冲/刑皆开库）。

    仅判地支层面冲/刑，不涉透干引拔--透干引拔管"开库之物是否引出可用"，
    由 analyze_muku 据天干透出另判开/闭；本函数只判墓库是否被冲/刑触动而开。
    合闭（墓库逢合而闭）不在本函数判定，由调用方处理（如 zuogong 闭库不收纳）。

    Args:
        tomb_zhi: 墓库地支
        all_zhis: 四柱全部地支

    Returns:
        墓库是否被他支冲或刑开
    """
    for z in all_zhis:
        if z and z != tomb_zhi and (_is_chong(z, tomb_zhi) or _is_xing(z, tomb_zhi)):
            return True
    return False


# ── 天干入墓墓地支 ──
# 天干坐于自身墓库地支谓之"天干入墓"（天干层面，区别于地支入地支墓的 is_entomb）。
# 盲派墓位：《渊海子平》土墓在辰；土墓又有"火土同长生（墓戌）"与"水土同长生（墓辰）"
# 之争。《五行精纪》折中为"戊寄戌、己寄辰"——阳土戊随火土同长生（墓戌），
# 阴土己随水土同长生（墓辰），严格区分戊/己墓位。其余八干（甲乙丙丁庚辛壬癸）
# 墓位与十二长生"墓"位重合（八干重合区）。
# 置信度：中（土墓流派争议，本表采《五行精纪》戊/己分用）
GAN_TOMB_ZHI: Dict[str, str] = {
    '甲': '未', '乙': '未',   # 木墓在未
    '丙': '戌', '丁': '戌',   # 火墓在戌
    '戊': '戌',               # 戊墓在戌（《五行精纪》戊寄戌，火土同长生）
    '己': '辰',               # 己墓在辰（《五行精纪》己寄辰，水土同长生）
    '庚': '丑', '辛': '丑',   # 金墓在丑
    '壬': '辰', '癸': '辰',   # 水墓在辰
}


def gan_tomb_zhi(gan: str) -> str:
    """天干入墓的墓地支（天干坐此支即入墓）。

    依《五行精纪》戊寄戌、己寄辰，严格区分戊/己墓位；其余八干墓位与十二长生
    "墓"位重合。返回空串表示无对应墓库（无效天干）。

    Args:
        gan: 天干

    Returns:
        该天干的墓地支；无效天干返回空字符串
    """
    return GAN_TOMB_ZHI.get(gan, '')


def is_gan_entombed(gan: str, zhi: str) -> bool:
    """天干是否坐于自身墓库地支（天干入墓）。

    天干入墓属天干层面，与地支入地支墓（is_entomb）相区别：天干坐于自身墓库
    地支时，该天干做事能力受限（盲派做功 M4 折扣）。

    Args:
        gan: 天干
        zhi: 天干所坐地支

    Returns:
        天干是否入墓（所坐地支恰为该天干的墓地支）
    """
    if not gan or not zhi:
        return False
    return GAN_TOMB_ZHI.get(gan, '') == zhi


def _tou_gan_elements(elements: List[str], gans: List[str]) -> List[str]:
    """墓库所收五行中，已有天干透出（透干引拔）的五行。

    盲师口传墓库体系："墓库透干引拔方为真开"。墓库逢冲须天干透出所收五行，
    方把库中之物引出可用；无透干则虽冲亦闭。对应关系：
      辰为水/土库 → 壬癸（水）或 戊己（土）透
      戌为火库   → 丙丁透
      丑为金库   → 庚辛透
      未为木库   → 甲乙透

    Args:
        elements: 墓库所收五行列表（TOMB_MAP[z]）
        gans: 四柱天干列表

    Returns:
        elements 中已有天干透出的五行子集（保持原顺序）
    """
    if not gans:
        return []
    gan_wx_present = {GAN_WX.get(g, '') for g in gans if g}
    return [e for e in elements if e in gan_wx_present]


def is_entomb(tombed_zhi: str, tomb_zhi: str, all_zhis: List[str]) -> bool:
    """盲派入墓判定（段建业《段氏理象学》墓库篇）。

    规则：
      - 基础条件：tombed_zhi 的五行须为 tomb_zhi 所收之五行（TOMB_MAP）
      - 生位（四生 寅申巳亥）见墓库 → 入墓
      - 旺位（四正 子午卯酉）不入墓，作半合/拱局看；
        除非"多而入墓"——除墓库外同五行地支 ≥ 2 时方入墓（如两酉见丑）
      - 墓位（四库 辰戌丑未）本身即墓库，与四正同走"多而入墓"，
        不无条件入墓（段氏：四库为墓，唯"多"方收）
      - 天干坐墓不入墓（如辛丑柱，辛不入丑墓）：本函数只判地支入地支墓，
        天干坐墓由调用方另行处理，此处不涉及
      - 戌论冲开不入墓（段氏两书）：戌为火库，被冲/刑开时循冲开论（释火不入
        墓）；未开（无辰戌冲、未遭丑戌未刑）时火支巳午正常入戌墓（《理象学》
        :3058 两午见戌以入墓看、《理象学研究》:6200 蒋介石例巳午同入戌墓加一
        层功）。戌作入墓方入辰墓仍依上述四库"多而入墓"规则

    "多而入墓"计数排除墓库自身：墓库为容器而非被收之物。四正之墓库五行
    （土）恒异于入墓方五行，排除与否同值；四库之墓库五行（土）与入墓方
    （土）相同，须排除方不误判（如辰戌同土，戌入辰不应仅因辰在盘即入墓）。

    Args:
        tombed_zhi: 被收入墓的地支
        tomb_zhi: 墓库地支
        all_zhis: 四柱全部地支（用于"多而入墓"计数）

    Returns:
        是否入墓
    """
    if not tombed_zhi or not tomb_zhi:
        return False
    if tomb_zhi not in TOMB_MAP:
        return False
    # 戌论冲开不入墓（段氏两书）：戌为火库，被冲/刑开时循冲开论（释火不入墓，
    # 《理象学研究》:12311「未运刑开戌中之火使巳火不入戌」）；未开（无辰戌冲、
    # 未遭丑戌未刑）时火支巳午正常入戌墓（《理象学》:3058「两午并见见戌便以入
    # 墓看」、《理象学研究》:6200 蒋介石例「主位巳、午同入戌墓，墓加一层功」）。
    # 戌作入墓方入辰墓仍依下述四库"多而入墓"规则（戌作 tombed 不经此分支）。
    if tomb_zhi == '戌' and _is_tomb_opened('戌', all_zhis):
        return False
    tombed_wx = ZHI_WX.get(tombed_zhi, '')
    if not tombed_wx or tombed_wx not in TOMB_MAP[tomb_zhi]:
        return False
    # 生位（四生）见墓库 → 入墓
    if tombed_zhi in SI_SHENG:
        return True
    # 旺位（四正）/ 墓位（四库）：多而入墓——除墓库自身外同五行地支 ≥ 2
    same_wx_count = sum(
        1 for z in all_zhis
        if z and z != tomb_zhi and ZHI_WX.get(z, '') == tombed_wx
    )
    return same_wx_count >= 2


def analyze_muku(zhis: List[str], gans: Optional[List[str]] = None) -> Dict:
    """分析四柱中的墓库关系。

    支持两种签名：旧位置参数（四柱地支列表），或首个参数为 Pillars 对象。
    gans 用于"透干引拔"判定——墓库逢冲须天干透出所收五行方为真开，
    无透干则虽冲亦闭（盲师口传墓库体系）。传 Pillars 对象时自动取其 gans。

    Args:
        zhis: 四柱地支列表 [year_zhi, month_zhi, day_zhi, hour_zhi]
            （或 Pillars 对象）
        gans: 四柱天干列表（可选）；缺省时不做透干引拔判定，
            逢冲即开（兼容旧调用方）

    Returns:
        墓库分析结果，含 tombs/tomb_relations/open_tombs/closed_tombs
    """
    if is_pillars(zhis):
        if gans is None:
            gans = zhis.gans
        zhis = zhis.zhis
    # gans 为 None：调用方未提供天干，无法判透干引拔，逢冲即开（兼容旧签名）；
    # gans 非 None（含空列表）：按透干引拔严格判定，无透干则虽冲亦闭。
    tou_gan_available = gans is not None

    tombs: List[Dict] = []
    tomb_relations: List[Dict] = []

    for i, z in enumerate(zhis):
        if z in TOMB_MAP:
            elements = TOMB_MAP[z]
            status = '墓库'
            desc = f'{z}为{"、".join(elements)}之墓库'

            # 先收集所有冲、刑、合关系，再按优先级判定（冲/刑开 > 合闭）
            chong_parts: List[str] = []
            xing_parts: List[str] = []
            he_parts: List[str] = []
            for j, z2 in enumerate(zhis):
                if i == j:
                    continue
                if _is_chong(z, z2):
                    chong_parts.append(z2)
                if _is_xing(z, z2):
                    xing_parts.append(z2)
                if _is_he(z, z2):
                    he_parts.append(z2)

            # 开库触发：冲、刑皆可开库（段氏「不冲不刑是墓（死的）」）。
            # 同一对可能既冲又刑（如丑未），合并去重后统一描述。
            open_parts = list(chong_parts)
            for z2 in xing_parts:
                if z2 not in open_parts:
                    open_parts.append(z2)
            open_kinds = []
            if chong_parts:
                open_kinds.append('冲')
            if xing_parts:
                open_kinds.append('刑')
            open_kind_str = '、'.join(open_kinds)  # '冲' | '刑' | '冲、刑'

            # 透干引拔：墓库逢冲/刑须天干透出所收五行方为真开；无透干则虽冲/刑亦闭
            # （盲师口传：开库须引拔，闭库虽冲/刑不开）。合而闭优先级最低。
            if open_parts and tou_gan_available:
                touched = _tou_gan_elements(elements, gans)
                if touched:
                    status = '开库'
                    desc = f'{z}墓库逢{"、".join(open_parts)}{open_kind_str}，{"、".join(touched)}透干引拔而开'
                else:
                    status = '闭库'
                    desc = f'{z}墓库逢{"、".join(open_parts)}{open_kind_str}，无透干引拔，闭而不开'
            elif open_parts:
                status = '开库'
                desc = f'{z}墓库逢{"、".join(open_parts)}{open_kind_str}而开'
            elif he_parts:
                status = '闭库'
                desc = f'{z}墓库逢{"、".join(he_parts)}合而闭'

            tombs.append({
                'zhi': z,
                'element_tombed': elements,
                'pillar': _PILLAR_NAMES[i],
                'status': status,
                'desc': desc,
            })

    # tomb_relations: 检测哪些地支入了哪些墓库
    # 单遍历上三角，双向检查（z1入z2墓 或 z2入z1墓）
    # 入墓判定遵循盲派规则：四正不入墓（除非多而入墓），四生入墓
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            wx1 = WU_XING_DZ[DI_ZHI.index(z1)] if z1 in DI_ZHI else ''
            wx2 = WU_XING_DZ[DI_ZHI.index(z2)] if z2 in DI_ZHI else ''

            if is_entomb(z1, z2, zhis):
                tomb_relations.append({
                    'from': {'zhi': z1, 'pillar': _PILLAR_NAMES[i]},
                    'to': {'zhi': z2, 'pillar': _PILLAR_NAMES[j]},
                    'relation': f'{z1}({wx1})入{z2}墓',
                })
            if is_entomb(z2, z1, zhis):
                tomb_relations.append({
                    'from': {'zhi': z2, 'pillar': _PILLAR_NAMES[j]},
                    'to': {'zhi': z1, 'pillar': _PILLAR_NAMES[i]},
                    'relation': f'{z2}({wx2})入{z1}墓',
                })

    return {
        'tombs': tombs,
        'tomb_relations': tomb_relations,
        'open_tombs': [t for t in tombs if t['status'] == '开库'],
        'closed_tombs': [t for t in tombs if t['status'] == '闭库'],
    }
