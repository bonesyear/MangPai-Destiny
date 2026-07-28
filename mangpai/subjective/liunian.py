"""
liunian - 盲派流年分析·主观判断层（subjective）

理论来源：段建业《段氏理象学》流年篇、高级篇 ch12（流年应期）/ch13（岁运关系）
核心思想：
  流年为君，大运为臣。流年定应期，大运定方向。
  1. 流年干支与命局发生冲合穿刑破克生等关系
  2. 流年与大运的互动--大运定基调，流年触发事件
  3. 流年引动墓库开闭
  4. 流年激活废神
  5. 流年到禄刃位->应期
  6. 流年带十神->看发生什么事

K5（高级篇 ch12 法则一/二 + ch13 分看统看）：
  冲/合关系从「触发/未触发」二分升级为九种语义：
    冲五种：冲动（旺神逢冲主变迁）/冲开（冲开墓库事发扬）/冲去（衰神逢冲主
            离去）/冲破（极衰无救主死亡）/冲旺（激起旺神，喜忌定吉凶）
    合四种：合留（合入得到，多主婚缘）/合动（引动发动）/合去（衰神逢合离去
            消失）/合绊（相贴牵制难发挥）
  判别口径（书诀「流年冲字须辨旺，旺者冲动衰者伤」）：所冲/合之字的旺衰
  由根气评分定（同气+1/生扶+1/克-1/空亡-1，月令双倍）；极衰<= -2、衰<0、
  旺>=2。流年冲大运另从 ch13 断法：正行干运为冲动（提前引动）、正行支运为
  冲去（运支当令怕冲崩）。大运分看/统看：干支同气或流年与大运刑冲合则
  十年统看，否则干管前五年、支管后五年。

分层说明（objective/subjective 重构）：
  流年单柱检测+吉凶信号复用 subjective.dayun._analyze_pillar_with_signals
  （其底层检测在 objective.dayun）。本模块在其结果上叠加「流年-大运互动」的
  吉凶调整（冲喜神反凶/冲忌神反吉等），并汇总为 analyze_liunian_mangpai。
  依赖方向单向：subjective -> objective（经 subjective.dayun 间接依赖）。
置信度：中
"""
from typing import Dict, List, Optional, Any

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG,
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI,
    XING_PAIRS, AN_HE, LU, PILLAR_KEYS,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.subjective.dayun import _analyze_pillar_with_signals

_YANG_GANS = set('甲丙戊庚壬')

# 刃位单一事实源在 objective.shensha（_YANG_REN 主刃位 / _YANG_REN_FULL 段氏
# 全刃位，戊取午未双刃）；此处仅别名兼容，不再自带副本（M2 口径统一）。
from mangpai.objective.shensha import _YANG_REN, _YANG_REN_FULL  # noqa: F401


def _analyze_liunian_dayun_interaction(
    ln_gan: str,
    ln_zhi: str,
    dy_gan: str,
    dy_zhi: str,
) -> List[Dict]:
    """分析流年与大运的互动。

    大运为臣（背景），流年为君（触发）。流年与大运的关系决定：
    - 流年冲大运->运局动荡
    - 流年合大运->运局稳定/绊住
    - 流年生大运->顺应运局
    - 流年克大运->逆运局
    """
    interactions: List[Dict] = []
    ln_gan_wx = GAN_WX.get(ln_gan, '')
    dy_gan_wx = GAN_WX.get(dy_gan, '')
    ln_zhi_wx = ZHI_WX.get(ln_zhi, '')
    dy_zhi_wx = ZHI_WX.get(dy_zhi, '')

    if TIAN_GAN_HE.get(ln_gan) == dy_gan:
        interactions.append({
            'type': '天干合',
            'desc': f'流年{ln_gan}合大运{dy_gan}--运局被流年绊住',
        })

    if ln_gan_wx and dy_gan_wx:
        if WX_KE.get(ln_gan_wx) == dy_gan_wx and TIAN_GAN_HE.get(ln_gan) != dy_gan:
            interactions.append({
                'type': '天干克',
                'desc': f'流年{ln_gan}克大运{dy_gan}--流年逆运',
            })
        if WX_KE.get(dy_gan_wx) == ln_gan_wx and TIAN_GAN_HE.get(ln_gan) != dy_gan:
            interactions.append({
                'type': '天干被克',
                'desc': f'大运{dy_gan}克流年{ln_gan}--运压流年',
            })

    def _check_pair(a, b, pairs):
        return (a, b) in pairs or (b, a) in pairs

    if _check_pair(ln_zhi, dy_zhi, LIU_CHONG):
        interactions.append({
            'type': '冲',
            'desc': f'流年{ln_zhi}冲大运{dy_zhi}--运局动荡，应期将至',
        })

    if _check_pair(ln_zhi, dy_zhi, LIU_HE):
        interactions.append({
            'type': '六合',
            'desc': f'流年{ln_zhi}合大运{dy_zhi}--运局稳定',
        })

    if _check_pair(ln_zhi, dy_zhi, LIU_HAI):
        interactions.append({
            'type': '穿',
            'desc': f'流年{ln_zhi}穿大运{dy_zhi}--暗中损耗',
        })

    if _check_pair(ln_zhi, dy_zhi, XING_PAIRS):
        interactions.append({
            'type': '刑',
            'desc': f'流年{ln_zhi}刑大运{dy_zhi}--是非纠纷',
        })

    if AN_HE.get(ln_zhi) == dy_zhi:
        interactions.append({
            'type': '暗合',
            'desc': f'流年{ln_zhi}暗合大运{dy_zhi}--私下勾连',
        })

    if ln_zhi_wx and dy_zhi_wx:
        if WX_KE.get(ln_zhi_wx) == dy_zhi_wx:
            interactions.append({
                'type': '克',
                'desc': f'流年{ln_zhi}({ln_zhi_wx})克大运{dy_zhi}({dy_zhi_wx})',
            })
        if WX_SHENG.get(ln_zhi_wx) == dy_zhi_wx:
            interactions.append({
                'type': '生',
                'desc': f'流年{ln_zhi}({ln_zhi_wx})生大运{dy_zhi}({dy_zhi_wx})--顺应运局',
            })

    return interactions


def _judge_xiji(
    day_gan: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    wx: str,
) -> str:
    """判定某五行对日主的喜忌方向（扶抑框架，方向总线统一口径）。

    段氏《段氏理象学》：「冲忌神反吉，冲喜神反凶」。喜忌定向复用
    yongshen.classify_strength（扶抑身强弱）：
      身强/从强（印比党众）-> 忌体（印比），喜用（财官食伤）
      身弱/从弱（印比党寡）-> 喜体（印比），忌用（财官食伤）
    中和/不明则喜忌不明，返回空串，调用方按中性处理。

    Returns: '喜' / '忌' / ''（无法判定）
    """
    from mangpai.subjective.yongshen import classify_strength
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx or not wx:
        return ''

    # 印五行（生我）
    yin_wx = ''
    for _w, _gen in WX_SHENG.items():
        if _gen == day_wx:
            yin_wx = _w
            break

    strength = classify_strength(day_gan, natal_gans, natal_zhis)
    if strength in ('中和', '不明'):
        return ''  # 党势均衡/数据不足，喜忌不明
    is_ti = (wx == day_wx) or (wx == yin_wx)
    if strength in ('身强', '从强'):
        # 身强忌体喜用
        return '忌' if is_ti else '喜'
    # 身弱/从弱喜体忌用
    return '喜' if is_ti else '忌'


def _judge_chong_xiji(
    day_gan: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    clashed_zhi: str,
) -> str:
    """判定所冲之支对日主的喜忌（_judge_xiji 的地支封装，A3 沿用）。"""
    return _judge_xiji(day_gan, natal_gans, natal_zhis, ZHI_WX.get(clashed_zhi, ''))


# ──────────────────────────────────────────────────────────────────────────
# K5: 冲五种 / 合四种 九种语义 + 大运分看统看（高级篇 ch12 法则一/二、ch13）
# ──────────────────────────────────────────────────────────────────────────

_MU_KU = {'辰', '戌', '丑', '未'}
_ZAO_TU = {'戌', '未'}  # 燥土：不生金反脆金（段氏中级·燥土脆金）
# 六穿（根被穿坏判定用）
_LIU_CHUAN = [('子', '未'), ('丑', '午'), ('寅', '巳'),
              ('卯', '辰'), ('申', '亥'), ('酉', '戌')]


def _kong_zhis(kong_wang: Any) -> List[str]:
    """空亡支列表（兼容 list / dict 两种入参形态）。"""
    if not kong_wang:
        return []
    if isinstance(kong_wang, list):
        return kong_wang
    if isinstance(kong_wang, dict):
        return kong_wang.get('zhi', kong_wang.get('zhis', [])) or []
    return []


def _sheng_wx_of(wx: str) -> str:
    """生我五行。"""
    for _w, _gen in WX_SHENG.items():
        if _gen == wx:
            return _w
    return ''


def _zhi_strength(
    zhi: str,
    context_zhis: List[str],
    kong_wang: Any = None,
    month_zhi: str = '',
    natal_gans: Optional[List[str]] = None,
) -> int:
    """地支（原局/大运字，被冲合之 target）旺衰评分。

    口径（书例回校）：同气支 +1、生我支 +1、克我支 -1；燥土（戌未）不生金
    反脆金（金见燥土按克计）；月令双倍；当令（target 即月令）+2；天干
    同气/生/克各 ±1（盖头截脚计入，书「满局火克」例）；空亡 -1；
    被评字自身不计帮扶。评分 >=2 为旺，<= -2 为极衰，<0 为衰。
    """
    wx = ZHI_WX.get(zhi, '')
    if not wx:
        return 0
    sheng_wx = _sheng_wx_of(wx)
    ke_me_wx = WX_KE_ME.get(wx, '')
    score = 0
    self_seen = False
    for c in context_zhis:
        if not c:
            continue
        if c == zhi and not self_seen:
            self_seen = True
            continue  # 被评字自身不计帮扶
        cwx = ZHI_WX.get(c, '')
        w = 2 if c == month_zhi else 1
        if cwx == wx:
            score += w
        elif cwx == sheng_wx:
            if wx == '金' and c in _ZAO_TU:
                score -= w  # 燥土脆金
            else:
                score += w
        elif cwx == ke_me_wx:
            score -= w
    if zhi == month_zhi:
        score += 2  # 当令
    for g in (natal_gans or []):
        gwx = GAN_WX.get(g, '')
        if gwx == wx:
            score += 1
        elif gwx == sheng_wx:
            score += 1
        elif gwx == ke_me_wx:
            score -= 1
    if zhi in _kong_zhis(kong_wang):
        score -= 1
    return score


def _liunian_strength(ln_zhi: str, context_zhis: List[str], month_zhi: str = '') -> int:
    """流年支自身旺衰（衰神冲旺神判别用）。

    书例口径（壬申例「申金衰，在局中无强根」）：只看地支根气——
    同气支（强根）+2、生我支 +1、克我支 -1；不计天干（书以「无强根」
    论衰，天干同气不作根）。<=0 为衰。
    """
    wx = ZHI_WX.get(ln_zhi, '')
    if not wx:
        return 0
    sheng_wx = _sheng_wx_of(wx)
    ke_me_wx = WX_KE_ME.get(wx, '')
    score = 0
    for c in context_zhis:
        if not c:
            continue
        cwx = ZHI_WX.get(c, '')
        if cwx == wx:
            score += 2
        elif cwx == sheng_wx:
            score += 1
        elif cwx == ke_me_wx:
            score -= 1
    return score


def _gan_strength(gan: str, natal_gans: List[str], natal_zhis: List[str]) -> int:
    """天干旺衰：本气通根数 + 同干帮扶。根支被他支冲/穿则根坏不计
    （书「根坏则虚」口径）；0 为虚透（衰，逢合为合去）。"""
    wx = GAN_WX.get(gan, '')
    if not wx:
        return 0
    score = sum(1 for g in natal_gans if g and GAN_WX.get(g) == wx and g != gan)
    for i, z in enumerate(natal_zhis):
        if ZHI_WX.get(z) != wx:
            continue
        damaged = False
        for j, o in enumerate(natal_zhis):
            if i == j or not o:
                continue
            if (z, o) in LIU_CHONG or (o, z) in LIU_CHONG:
                damaged = True
                break
            if (z, o) in _LIU_CHUAN or (o, z) in _LIU_CHUAN:
                damaged = True
                break
        if not damaged:
            score += 1
    return score


def _zhi_benqi_shishen(day_gan: str, zhi: str) -> str:
    """地支本气十神（配偶星判别用）。"""
    from mangpai.subjective.yongshen import _shishen_full
    cg = get_canggan_mangpai(zhi)
    if not cg:
        return ''
    return _shishen_full(day_gan, cg[0][0])


def _is_spouse_star(shishen: str, gender: Optional[str]) -> bool:
    """配偶星判别：男命财星、女命官星（gender 缺省不误判）。"""
    if gender == '男':
        return shishen in ('正财', '偏财')
    if gender == '女':
        return shishen in ('正官', '七杀')
    return False


def classify_chong_semantic(
    ln_zhi: str,
    target_zhi: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    dayun_zhi: str = '',
    kong_wang: Any = None,
    target_location: str = 'natal',
    phase_active: str = '',
) -> Dict:
    """冲之五种语义（高级篇 ch12 法则二、ch13 天克地冲断法）。

    判别顺序（书诀「旺者冲动衰者伤；冲开墓库事发扬；冲去衰神主离去；
    冲破无救主死亡；冲旺用神反为吉，冲凶忌神祸难当」）：
      1. 所冲极衰无救（评分<= -2）            -> 冲破（主死亡/终结，大凶）
      2. 所冲为墓库（辰戌丑未）               -> 冲开（库藏释放，事发扬）
      3. 所冲衰（评分<0）                     -> 冲去（主离去/失去）
      4. 流年支衰而所冲旺（衰神冲旺神）        -> 冲去（流年字自去，书例姐远嫁）
      5. 流年冲大运：正行干运 -> 冲动（提前引动）；正行支运 -> 冲去（运支当令怕冲崩）
      6. 所冲旺（>=2）且喜忌可判               -> 冲旺（激起：用神吉放大/忌神凶放大）
      7. 其余（旺而喜忌不明/力量相当）          -> 冲动（主变迁/调动）
    """
    month_zhi = natal_zhis[1] if len(natal_zhis) > 1 else ''
    ctx = list(natal_zhis) + ([dayun_zhi] if dayun_zhi else [])
    s_t = _zhi_strength(target_zhi, ctx, kong_wang, month_zhi,
                        natal_gans=natal_gans)
    s_l = _liunian_strength(ln_zhi, ctx, month_zhi)

    chong_type = '冲动'
    desc_tail = '旺神逢冲，主变迁/调动'
    if s_t <= -2:
        chong_type = '冲破'
        desc_tail = '所冲极衰无救，冲破主终结/死亡，大凶'
    elif target_zhi in _MU_KU:
        chong_type = '冲开'
        desc_tail = '冲开墓库，库藏释放，事发扬'
    elif s_t < 0:
        chong_type = '冲去'
        desc_tail = '衰神逢冲而去，主离去/失去'
    elif s_l <= 0 and s_t >= 2:
        chong_type = '冲去'
        desc_tail = '流年衰神冲旺神，流年字自去（主离去）'
    elif target_location == 'dayun' and phase_active == '干':
        chong_type = '冲动'
        desc_tail = '正行天干运，流年冲运为冲动，提前引动该运之事'
    elif target_location == 'dayun' and phase_active == '支':
        chong_type = '冲去'
        desc_tail = '运支当令怕冲崩，流年冲运为冲去，运支力量暂弱'
    elif s_t >= 2:
        xiji = _judge_chong_xiji(day_gan, natal_gans, natal_zhis, target_zhi)
        if xiji == '喜':
            chong_type = '冲旺'
            desc_tail = '冲旺用神，激起更旺，反为吉'
        elif xiji == '忌':
            chong_type = '冲旺'
            desc_tail = '冲旺忌神，激起发凶，祸难当'

    return {
        'chong_type': chong_type,
        'target_strength': s_t,
        'liunian_strength': s_l,
        'desc': f'{ln_zhi}冲{target_zhi}：{chong_type}（{desc_tail}）',
    }


def classify_he_semantic(
    kind: str,
    target: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    dayun_zhi: str = '',
    kong_wang: Any = None,
    target_location: str = 'natal',
    gender: Optional[str] = None,
    target_idx: int = -1,
) -> Dict:
    """合之四种语义（高级篇 ch12 法则一：合留/合动/合去/合绊）。

    书诀：「流年合八字为动，合留合去合绊情。配偶星宫逢流合，多为婚期
    喜事临。原局旺神逢岁合，合动做事事必成。衰神逢合为合去，离去消失
    不见形。两字相贴逢岁合，合绊牵制难发挥。」
      - 合大运字：配偶星 -> 合留（得到，主婚缘）；余 -> 合动（引动大运所主）
      - 合命局字：衰 -> 合去（离去/失去）；原局已与他字相贴合 -> 合绊（牵制
        难发挥）；配偶星/喜用 -> 合留（合入得到）；余（旺）-> 合动（发动）
    kind: '天干合'（target 为干）或 '六合'/'暗合'（target 为支）。
    """
    is_gan = kind == '天干合'
    month_zhi = natal_zhis[1] if len(natal_zhis) > 1 else ''
    ctx = list(natal_zhis) + ([dayun_zhi] if dayun_zhi else [])
    if is_gan:
        s_t = _gan_strength(target, natal_gans, natal_zhis)
        from mangpai.subjective.yongshen import _shishen_full
        shishen = _shishen_full(day_gan, target)
    else:
        s_t = _zhi_strength(target, ctx, kong_wang, month_zhi,
                            natal_gans=natal_gans)
        shishen = _zhi_benqi_shishen(day_gan, target)

    # 原局相贴合（target 与邻位支本有六合，再逢岁合为争合牵制）
    adjacent_he = False
    if not is_gan and target_location == 'natal' and 0 <= target_idx < len(natal_zhis):
        for j in (target_idx - 1, target_idx + 1):
            if 0 <= j < len(natal_zhis) and natal_zhis[j]:
                pair = (target, natal_zhis[j])
                if pair in LIU_HE or (pair[1], pair[0]) in LIU_HE:
                    adjacent_he = True
                    break

    spouse = _is_spouse_star(shishen, gender)
    if target_location == 'dayun':
        if spouse:
            he_type, tail = '合留', '流年合住大运配偶星，得到/留住，主婚缘'
        else:
            he_type, tail = '合动', '流年合大运为合动，引动大运所主吉凶'
    elif adjacent_he:
        # 相贴优先于衰：书例二（子丑贴，丁丑年合绊用神）target 丑虽偏弱仍论
        # 合绊不论合去；书例三合去（丧母）target 辛无贴合，虚透方论合去
        he_type, tail = '合绊', '两字相贴逢岁合，合绊牵制难发挥'
    elif s_t < 0 or (is_gan and s_t == 0):
        he_type, tail = '合去', '衰神逢合为合去，离去消失，主失去'
    elif spouse:
        he_type, tail = '合留', '配偶星逢岁合，合入得到，多主婚缘喜事'
    else:
        xiji = _judge_xiji(day_gan, natal_gans, natal_zhis,
                           GAN_WX.get(target, '') if is_gan else ZHI_WX.get(target, ''))
        if xiji == '喜':
            he_type, tail = '合留', '喜用逢岁合，合入得到'
        else:
            he_type, tail = '合动', '旺神逢岁合，合动做事，引动发动'

    return {
        'he_type': he_type,
        'target_strength': s_t,
        'target_shishen': shishen,
        'desc': f'{kind}{target}：{he_type}（{tail}）',
    }


def determine_dayun_phase(
    dy_gan: str,
    dy_zhi: str,
    liunian_list: List[Dict],
    birth_year: Optional[int] = None,
    dayun_start_age: Optional[int] = None,
) -> Dict:
    """大运分看/统看判定（高级篇 ch13 法则二·大运分统诀）。

    「常理上下五年分，干管五载支五春。流年若不刑冲合，各司其职莫混沦。
      倘若流年冲合运，十年统看气连筋。」
    统看触发（口诀原文）：任一流年与大运发生天干五合/地支冲/刑/六合。
    否则分看：大运第 1-5 年干主事、第 6-10 年支主事（起运年 ≈ 出生年 +
    起运年龄，无法定位时 active 为空串）。
    干支同气（如丙午）书例多一气呵成统看，但甲寅例干支作用相反仍分看——
    须作用级分析，超出机械判别；同气时附 same_qi/note 提示，不自动统看。
    """
    def _ln_gz(entry: Dict) -> str:
        gz = entry.get('gz', '')
        if gz and len(gz) >= 2:
            return gz
        return f"{entry.get('gan', '')}{entry.get('zhi', '')}"

    def _check_pair(a, b, pairs):
        return (a, b) in pairs or (b, a) in pairs

    reason = ''
    phase = '分看'
    same_qi = bool(dy_gan and dy_zhi and GAN_WX.get(dy_gan) == ZHI_WX.get(dy_zhi))
    for entry in liunian_list:
        gz = _ln_gz(entry)
        if len(gz) < 2:
            continue
        lg, lz = gz[0], gz[1]
        hit = ''
        if TIAN_GAN_HE.get(lg) == dy_gan:
            hit = f'天干五合（{lg}{dy_gan}合）'
        elif _check_pair(lz, dy_zhi, LIU_CHONG):
            hit = f'地支相冲（{lz}{dy_zhi}冲）'
        elif _check_pair(lz, dy_zhi, XING_PAIRS):
            hit = f'地支相刑（{lz}{dy_zhi}刑）'
        elif _check_pair(lz, dy_zhi, LIU_HE):
            hit = f'地支六合（{lz}{dy_zhi}合）'
        if hit:
            phase = '统看'
            reason = f'流年{gz}与大运{dy_gan}{dy_zhi}{hit}，十年统看气连筋'
            break

    per_year: Dict[Any, Dict] = {}
    if phase == '分看' and birth_year and dayun_start_age is not None:
        start_year = int(birth_year) + int(dayun_start_age)
        for entry in liunian_list:
            y = entry.get('year')
            if not y:
                continue
            pos = int(y) - start_year + 1
            if 1 <= pos <= 5:
                active = '干'
            elif 6 <= pos <= 10:
                active = '支'
            else:
                active = ''
            per_year[y] = {'position': pos, 'active': active}
        if not reason:
            reason = '流年未与大运刑冲合，干管前五年、支管后五年，各司其职'
    elif not reason:
        reason = '流年未与大运刑冲合，分看（起运锚点缺失，主事干支不定）'

    note = ''
    if same_qi and phase == '分看':
        note = (f'大运{dy_gan}{dy_zhi}干支同气：书例多一气呵成统看（参丙午例），'
                '惟干支作用相反者仍宜分看（参甲寅例），此处按口诀从分看，请人工酌定')

    return {
        'phase': phase,
        'reason': reason,
        'active': '干支' if phase == '统看' else '',
        'per_year': per_year,
        'same_qi': same_qi,
        'note': note,
    }


def analyze_liunian_mangpai(
    liunian_list: List[Dict],
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    current_dayun: Optional[Dict] = None,
    natal_fei_shen: Optional[List[str]] = None,
    kong_wang: Any = None,
    gender: Optional[str] = None,
    birth_year: Optional[int] = None,
) -> Dict:
    """分析流年与本命的互动（盲派视角）。

    盲派流年分析核心：
    1. 流年为君，定应期
    2. 流年与命局的冲合穿刑破克生（K5：冲/合升级为九种语义，
       见 classify_chong_semantic / classify_he_semantic）
    3. 流年与大运的互动（大运为背景；K5：附分看/统看 phase，
       见 determine_dayun_phase）
    4. 流年引动墓库开闭
    5. 流年激活废神
    6. 流年到禄刃位->应期
    7. 流年带十神->看发生什么事

    Args:
        liunian_list: 流年柱列表，每项含 gz（如'甲子'）或 gan/zhi，
                      以及 year（可选；K5 分看定位用）
        natal_gans: 四柱天干
        natal_zhis: 四柱地支
        day_gan: 日干
        current_dayun: 当前大运柱 {gan, zhi} 或 {gz}（可选；可带
                      start_age/end_age，供分看统看定位）
        natal_fei_shen: 本命废神位置列表
        kong_wang: 空亡数据
        gender: 性别（可选；合留配偶星判别用，缺省不误判）
        birth_year: 出生年（可选；分看大运第几年定位用）

    Returns:
        {'liunian': [per-year analysis...], 'summary': '...',
         'dayun_phase': {phase, reason, active, per_year}（有大运时）}
    """
    dy_gan = ''
    dy_zhi = ''
    dy_start_age: Optional[int] = None
    if current_dayun:
        gz = current_dayun.get('gz', '')
        if gz and len(gz) >= 2:
            dy_gan, dy_zhi = gz[0], gz[1]
        else:
            dy_gan = current_dayun.get('gan', '')
            dy_zhi = current_dayun.get('zhi', '')
        sa = current_dayun.get('start_age')
        if sa is not None:
            try:
                dy_start_age = int(sa)
            except (TypeError, ValueError):
                dy_start_age = None

    # K5: 大运分看/统看（有大运即判定；per_year 需 birth_year + start_age）
    dayun_phase: Optional[Dict] = None
    if dy_gan and dy_zhi:
        dayun_phase = determine_dayun_phase(
            dy_gan, dy_zhi, liunian_list,
            birth_year=birth_year, dayun_start_age=dy_start_age,
        )

    analyses: List[Dict] = []

    for entry in liunian_list:
        gz = entry.get('gz', '')
        if gz and len(gz) >= 2:
            gan, zhi = gz[0], gz[1]
        else:
            gan = entry.get('gan', '')
            zhi = entry.get('zhi', '')

        if not gan or not zhi:
            continue

        result = _analyze_pillar_with_signals(
            gan, zhi, natal_gans, natal_zhis, day_gan,
            natal_fei_shen=natal_fei_shen,
            kong_wang=kong_wang,
            tomb_extra_gans=[gan],  # 流年干纳入墓库透干引拔（段氏墓库篇）
        )
        result['year'] = entry.get('year', 0)

        # K5: 流年-命局 冲/合关系升级为九种语义（additive：relations 附
        # chong_semantic / he_semantic 字段，不改原 type/desc）
        year_phase_active = ''
        if dayun_phase and dayun_phase['phase'] == '统看':
            year_phase_active = '干支'
        elif dayun_phase:
            year_phase_active = dayun_phase['per_year'].get(
                entry.get('year'), {}).get('active', '')

        for r in result.get('zhi_relations', []):
            tgt = r.get('target', '')
            if not tgt:
                continue
            if r['type'] == '冲':
                r['chong_semantic'] = classify_chong_semantic(
                    zhi, tgt, natal_gans, natal_zhis, day_gan,
                    dayun_zhi=dy_zhi, kong_wang=kong_wang,
                    target_location='natal',
                )
            elif r['type'] in ('六合', '暗合'):
                t_idx = -1
                pos = r.get('target_pos', '')
                if pos.endswith('_zhi') and pos[:-4] in PILLAR_KEYS:
                    t_idx = PILLAR_KEYS.index(pos[:-4])
                r['he_semantic'] = classify_he_semantic(
                    r['type'], tgt, natal_gans, natal_zhis, day_gan,
                    dayun_zhi=dy_zhi, kong_wang=kong_wang,
                    target_location='natal', gender=gender,
                    target_idx=t_idx,
                )
        for r in result.get('gan_relations', []):
            tgt = r.get('target', '')
            if r['type'] == '天干合' and tgt:
                r['he_semantic'] = classify_he_semantic(
                    '天干合', tgt, natal_gans, natal_zhis, day_gan,
                    dayun_zhi=dy_zhi, kong_wang=kong_wang,
                    target_location='natal', gender=gender,
                )

        # K5: 强语义叠信号（保守：只补最凶两端，中性变迁不碰 overall）
        for r in result.get('zhi_relations', []):
            cs = r.get('chong_semantic')
            if cs and cs['chong_type'] == '冲破':
                note = f'流年{zhi}冲破{r.get("target", "")}（极衰无救，主终结）'
                if note not in result['negative_signals']:
                    result['negative_signals'].append(note)
                if result['overall'] == '吉':
                    result['overall'] = '吉凶参半'
        for r in result.get('zhi_relations', []) + result.get('gan_relations', []):
            hs = r.get('he_semantic')
            if hs and hs['he_type'] == '合去':
                note = f'流年合去{r.get("target", "")}（衰神合去，主失去）'
                if note not in result['negative_signals']:
                    result['negative_signals'].append(note)

        dy_interactions: List[Dict] = []
        if dy_gan and dy_zhi:
            dy_interactions = _analyze_liunian_dayun_interaction(
                gan, zhi, dy_gan, dy_zhi,
            )
            # K5: 流年-大运 冲/合 附九种语义（target_location='dayun'，
            # 冲之冲动/冲去按分看统看主事干支定向）
            for inter in dy_interactions:
                if inter['type'] == '冲':
                    inter['chong_semantic'] = classify_chong_semantic(
                        zhi, dy_zhi, natal_gans, natal_zhis, day_gan,
                        dayun_zhi=dy_zhi, kong_wang=kong_wang,
                        target_location='dayun',
                        phase_active=year_phase_active,
                    )
                elif inter['type'] == '六合':
                    inter['he_semantic'] = classify_he_semantic(
                        '六合', dy_zhi, natal_gans, natal_zhis, day_gan,
                        dayun_zhi=dy_zhi, kong_wang=kong_wang,
                        target_location='dayun', gender=gender,
                    )
                elif inter['type'] == '天干合':
                    inter['he_semantic'] = classify_he_semantic(
                        '天干合', dy_gan, natal_gans, natal_zhis, day_gan,
                        dayun_zhi=dy_zhi, kong_wang=kong_wang,
                        target_location='dayun', gender=gender,
                    )
            result['dayun_interaction'] = dy_interactions
            if dayun_phase:
                result['dayun_phase_active'] = year_phase_active

            dy_chong = any(i['type'] == '冲' for i in dy_interactions)
            dy_he = any(i['type'] in ('六合', '天干合') for i in dy_interactions)

            if dy_chong:
                # 段氏「冲忌神反吉，冲喜神反凶」：按所冲大运支对日主的喜忌定向判断，
                # 不再机械降级（旧「冲即降级」与冲忌神反吉相悖）。
                chong_xiji = _judge_chong_xiji(day_gan, natal_gans, natal_zhis, dy_zhi)
                if chong_xiji == '忌':
                    result['positive_signals'].append(
                        f'流年冲大运{dy_zhi}，冲去忌神反吉')
                elif chong_xiji == '喜':
                    result['negative_signals'].append(
                        f'流年冲大运{dy_zhi}，冲去喜神反凶')
                    if result['overall'] == '吉':
                        result['overall'] = '吉凶参半'
                    elif result['overall'] == '平':
                        result['overall'] = '凶'
                else:
                    result['negative_signals'].append('流年冲大运，运局动荡')
            if dy_he:
                result['positive_signals'].append('流年合大运，运局稳定')

            dy_desc = '；'.join(i['desc'] for i in dy_interactions) if dy_interactions else ''
            if dy_desc:
                result['desc'] += f'；大运互动：{dy_desc}'

        analyses.append(result)

    ji_count = sum(1 for a in analyses if a['overall'] == '吉')
    xiong_count = sum(1 for a in analyses if a['overall'] == '凶')

    summary_parts: List[str] = []
    summary_parts.append(f'共{len(analyses)}年')
    if ji_count:
        summary_parts.append(f'吉年{ji_count}年')
    if xiong_count:
        summary_parts.append(f'凶年{xiong_count}年')

    out = {
        'liunian': analyses,
        'ji_count': ji_count,
        'xiong_count': xiong_count,
        'summary': '；'.join(summary_parts),
    }
    if dayun_phase:
        out['dayun_phase'] = dayun_phase
    return out


__all__ = [
    'analyze_liunian_mangpai',
    'classify_chong_semantic',
    'classify_he_semantic',
    'determine_dayun_phase',
]
