"""
yunfan — 岁运反局（大运/流年引动反局）·主观层

理论来源：段建业《盲派高级命理学》3.3「大运、流年引发的反局应事」
          + 第十二/十三章 岁运精微
          （源文件 mangpai/docs/duan-books/mangpai-gaoji-ocr.txt 3505-3820 行）

核心精义：原局为体、运岁为用。原局本为正局/清纯，行至特定运岁，其干支以
合/冲/刑/穿/墓等方式破坏原局功神、改变做功方式(冲变合/合变冲)、或引发伏吟
三刑自我冲突，引动原局潜在矛盾 → 反局灾祸。「静体待动，动则生变；变而反局，
灾祸立现」。

大运反局三大类型（源文 3541-3707）：
  类型一·破坏原局功神：运干支合绊/穿害/冲散核心功神，或生扶被制忌神 → 功不施。
  类型二·改变做功方式：原局喜冲怕逢合(运来合→闭)、喜合怕逢冲(运来冲→破)，
          冲合互变，能量路径反转。
  类型三·伏吟/三刑：运与原局某柱伏吟(重复)，或组三刑/自刑 → 内部矛盾激化。

流年反局两大类型（源文 3712-3819）：
  类型一·流年单独引动：流年干支单独作用原局，引动忌神/破坏功神/改做功方式。
  类型二·岁运联动(最凶)：流年与大运天合地合(天地合)、或组三刑/双冲，锁住或
          激烈冲击原局 → 大灾（岁运并临/岁运互动）。

心法：
  - 冲合 vs 合冲：原局喜冲怕逢合(合变冲为闭库)、喜合怕逢冲(冲开合为破局)。
  - 阴阳逆转：本护身之禄刃被冲反戈攻身、忌神得运生助反客为主。

依赖（统一消费）：
  objective.constants（冲合穿刑破表）+ zuogong_confirm（原局做功/功神废神）
  + zhengfan（原局正反局基线）+ dayun/liunian（运岁互动数据）。
依赖方向单向：subjective -> objective + subjective（zuogong_confirm/zhengfan/dayun/liunian），
  本模块不反向依赖。
置信度：中（运岁引动判据为结构启发式，应期精细须结合领域应期模块）。
"""
from typing import Dict, List, Optional, Any, Tuple

from mangpai.objective.constants import (
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI, LIU_PO, XING_PAIRS, AN_HE,
    GAN_WX, ZHI_WX, WX_SHENG, WX_KE, PILLAR_KEYS, TOMB_MAP, LU,
)
from mangpai.subjective.zuogong_confirm import analyze_zuogong
from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.yongshen import classify_strength, classify_cong_target

# ── 三刑组（寅巳申 / 丑戌未 / 子卯互刑；辰午酉亥自刑）──
_SANXING_GROUPS = [frozenset('寅巳申'), frozenset('丑戌未'), frozenset('子卯')]
_ZIXING = ('辰', '午', '酉', '亥')

_HE_TYPES = {'天干合', '合', '暗合'}       # 合家族（用于冲变合判定）
_CHONG_TYPES = {'冲'}                       # 冲家族（用于合变冲判定）
_HARM_TYPES = {'天干合', '冲', '合', '穿', '破', '暗合'}  # 破坏功神的合绊/穿害/冲散


def _pos_elem(pos: str, gans: List[str], zhis: List[str]) -> str:
    """pos -> 对应干/支字符。"""
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    if p not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(p)
    return gans[idx] if t == 'gan' else (zhis[idx] if idx < len(zhis) else '')


def _pair_hit(a: str, b: str, pairs) -> bool:
    return (a, b) in pairs or (b, a) in pairs


def _op_interactions(
    op_gan: str, op_zhi: str,
    natal_gans: List[str], natal_zhis: List[str],
) -> List[Dict]:
    """运岁干支 vs 原局四柱的 冲/合/穿/刑/破/暗合 关系。

    Returns: [{type, target_pos, target_elem, desc}, ...]
    """
    out: List[Dict] = []
    # 天干合
    if op_gan:
        for i, ng in enumerate(natal_gans):
            if ng and TIAN_GAN_HE.get(op_gan) == ng:
                out.append({'type': '天干合', 'target_pos': f'{PILLAR_KEYS[i]}_gan',
                            'target_elem': ng,
                            'desc': f'{op_gan}合{PILLAR_KEYS[i]}干{ng}'})
    # 地支六关系
    if op_zhi:
        tbls = (('冲', LIU_CHONG), ('合', LIU_HE), ('穿', LIU_HAI), ('破', LIU_PO))
        for i, nz in enumerate(natal_zhis):
            if not nz:
                continue
            pos = f'{PILLAR_KEYS[i]}_zhi'
            for tname, tbl in tbls:
                if _pair_hit(op_zhi, nz, tbl):
                    out.append({'type': tname, 'target_pos': pos, 'target_elem': nz,
                                'desc': f'{op_zhi}{tname}{PILLAR_KEYS[i]}支{nz}'})
            # 刑（XING_PAIRS 含自刑，对称判定关系存在）
            if _pair_hit(op_zhi, nz, XING_PAIRS):
                out.append({'type': '刑', 'target_pos': pos, 'target_elem': nz,
                            'desc': f'{op_zhi}刑{PILLAR_KEYS[i]}支{nz}'})
            # 暗合
            if AN_HE.get(op_zhi) == nz or AN_HE.get(nz) == op_zhi:
                out.append({'type': '暗合', 'target_pos': pos, 'target_elem': nz,
                            'desc': f'{op_zhi}暗合{PILLAR_KEYS[i]}支{nz}'})
    return out


def _detect_fuyin(
    op_gan: str, op_zhi: str,
    natal_gans: List[str], natal_zhis: List[str],
) -> List[str]:
    """运岁与原局某柱伏吟（干/支重复）。"""
    out: List[str] = []
    for i, pk in enumerate(PILLAR_KEYS):
        if i >= len(natal_gans):
            continue
        if op_gan and natal_gans[i] == op_gan:
            out.append(f'{op_gan}伏吟{pk}干')
        if i < len(natal_zhis) and op_zhi and natal_zhis[i] == op_zhi:
            out.append(f'{op_zhi}伏吟{pk}支')
    return out


def _detect_sanxing(op_zhi: str, natal_zhis: List[str]) -> List[str]:
    """运支加入后是否与原局构成完整三刑/自刑（须运支参与、且原局原本不完整）。"""
    if not op_zhi:
        return []
    out: List[str] = []
    natal_set = set(z for z in natal_zhis if z)
    pool = natal_set | {op_zhi}
    for g in _SANXING_GROUPS:
        # 须运支在此刑组内，且原局原本未齐全（运支补全方为「组成」三刑）
        if op_zhi in g and g <= pool and not g <= natal_set:
            out.append(''.join(sorted(g)) + '三刑')
    for z in _ZIXING:
        if op_zhi == z and z in natal_set:
            out.append(z + '自刑')
    return out


def _detect_sanxing_dayun(op_zhi: str, natal_zhis: List[str]) -> List[str]:
    """大运支与原局组成完整三刑（A14 大运口径：不含自刑——大运自刑二本例
    皆假阳：煤矿-2 壬午运午午自刑、经理-4 甲辰运辰辰自刑，书皆判该运发财）。"""
    if not op_zhi:
        return []
    natal_set = set(z for z in natal_zhis if z)
    pool = natal_set | {op_zhi}
    return [''.join(sorted(g)) + '三刑'
            for g in _SANXING_GROUPS
            if op_zhi in g and g <= pool and not g <= natal_set]


def _detect_fuyin_jihua_dayun(op_zhi: str, natal_zhis: List[str]) -> List[str]:
    """大运支伏吟且激化原局已有刑对（A14 大运口径）。

    伏吟=该字到位，单字伏吟不即反局（发财运多为该字五行应期——294例批3
    十一发财运中煤矿戌运/包工头卯运/复例四申运/经理-2戌运皆假阳）；须
    伏吟支与原局已有刑对相互激化方为「自我冲突激化」（巨富丑运丙子运：
    子伏吟日支、激化原局卯子刑，书明文该运入狱=真阳锚）。刑合并见以合
    解（复例四原局巳申刑合并见，庚申运发财）；刑涉墓库=刑开库应期，豁免
    （煤矿戌运刑开丑财库、书明文发财十几亿锚）。干伏吟归伤官见官等原局
    凶向链（案例五乙伏吟年干实与伤官见官纠缠），不入大运 T3。
    """
    if not op_zhi or op_zhi not in natal_zhis:
        return []
    partners = sorted({
        nz for nz in natal_zhis if nz and nz != op_zhi
        and _pair_hit(op_zhi, nz, XING_PAIRS)
        and not _pair_hit(op_zhi, nz, LIU_HE)  # 刑合并见，以合解
    })
    if not partners:
        return []
    if op_zhi in TOMB_MAP or any(p in TOMB_MAP for p in partners):
        return []  # 刑涉墓库=刑开库应期（吉），非自我冲突
    return [f'{op_zhi}伏吟激化原局{op_zhi}{"、".join(partners)}刑']


def _detect_jishen_fufu(
    op_gan: str, op_zhi: str,
    natal_gans: List[str], natal_zhis: List[str],
    fei_shen: List[str],
) -> List[str]:
    """忌神反客为主：运岁五行生扶废神（被制忌神）五行。"""
    fei_wxs = set()
    for pos in (fei_shen or []):
        e = _pos_elem(pos, natal_gans, natal_zhis)
        w = GAN_WX.get(e) or ZHI_WX.get(e)
        if w:
            fei_wxs.add(w)
    out: List[str] = []
    for ow in (GAN_WX.get(op_gan, ''), ZHI_WX.get(op_zhi, '')):
        if not ow:
            continue
        for fw in sorted(fei_wxs):  # sorted：out 文本列表定序，复跑确定
            if WX_SHENG.get(ow) == fw:
                out.append(f'运{ow}生废神{fw}——忌神得运生助，反客为主')
    return out


def _detect_lu_ren_fangg(
    op_zhi: str, day_gan: str, natal_zhis: List[str],
) -> Optional[str]:
    """阴阳逆转：禄/刃被冲反戈攻身。"""
    if not op_zhi or not day_gan:
        return None
    targets: List[str] = []
    lu = LU.get(day_gan, '')
    if lu and _pair_hit(op_zhi, lu, LIU_CHONG):
        targets.append(f'禄({lu})被冲')
    # 羊刃（阳干刃位，段氏全刃表：戊取午、未双刃）被冲
    from mangpai.objective.shensha import _YANG_REN_FULL as _YR
    for yr in _YR.get(day_gan, []):
        if yr and _pair_hit(op_zhi, yr, LIU_CHONG):
            targets.append(f'羊刃({yr})被冲')
    if targets:
        return '、'.join(targets) + '——本护身之禄刃反戈攻身（阴阳逆转）'
    return None


def _detect_po_cong(
    op_gan: str, op_zhi: str,
    day_gan: str,
    natal_gans: List[str], natal_zhis: List[str],
    strength: str, cong_label: str,
    is_liunian: bool,
) -> Tuple[List[Dict], List[Dict]]:
    """破从反局 + 异党合去吉向（G5：22期从格行运规则 + 12期有错必纠）。

    从强侧（自党成势，异党=忌神）：
      - 破从·忌神通根（凶）：运岁支五行为异党，且原局该五行之干**虚透无本气
        根**——「八字中原有凶神无制化，在大运中得根主大凶」（12期；qi02
        从强火局行亥运，癸水忌神通根，家业破尽而亡）。原局无该异党透干者
        不触发（忌神不现，运支自成气候非「通根」；从格行异党支运为常事，
        防过火）。
      - 异党合去（吉向标注，不入凶链）：运岁干为异党而原局有明现干五合之
        （合去忌神=得忌喜——ans32 丙财忌神被辛合去主得财；li141 癸被戊合
        去，癸亥运为顶峰）；运岁支六合原局异党支（两忌神合绊主吉，ans32
        卯戌合绊）同为吉向标注。
    从弱侧（日主无依托，从其所从）：
      - 破从·日主得根（凶）：运岁支藏干含日主五行（日主得根有所依而不肯
        从——22期例6 从官格行戌运丙火得墓库余气根，一生最差）。
      - 破从·合去日主（凶，仅流年）：流年干与日主五合（22期例8 丙子年丙
        辛合，辛金被合去，「日主没有了，如何从」，财从他党而破财）。

    Returns: (fans, jis) — fans 入反局凶链，jis 仅吉向标注（suiyun_ji）。
    """
    fans: List[Dict] = []
    jis: List[Dict] = []
    if strength not in ('从强', '从弱'):
        return fans, jis
    dw = GAN_WX.get(day_gan, '')
    if not dw:
        return fans, jis
    yin_wx = ''
    for w, c in WX_SHENG.items():
        if c == dw:
            yin_wx = w
            break
    op_name = '流年' if is_liunian else '大运'
    op_gz = f'{op_gan}{op_zhi}'

    if strength == '从强':
        yidang = [w for w in ('金', '木', '水', '火', '土') if w not in (dw, yin_wx)]
        # 破从·忌神通根：运岁支=异党五行 + 原局该五行干虚透且无本气根
        op_zw = ZHI_WX.get(op_zhi, '')
        if op_zw and op_zw in yidang:
            tou_gan = any(GAN_WX.get(g, '') == op_zw for g in natal_gans if g)
            rooted = any(ZHI_WX.get(z, '') == op_zw for z in natal_zhis if z)
            if tou_gan and not rooted:
                fans.append({
                    'fan_type': f'{op_name}反局·破从(忌神通根)',
                    'severity': '重',
                    'reason': f'{op_gz}运岁支{op_zhi}为异党（忌神）之根，原局{op_zw}干'
                              f'虚透无根今得通根——从强格「凶神无制化，大运中得根主大凶」'
                              f'（12期；qi02 亥运癸水通根家业破尽）',
                })
        # 异党合去（吉向标注）：运岁干为异党 + 原局明现干五合之（合去忌神）
        op_gw = GAN_WX.get(op_gan, '')
        if op_gw and op_gw in yidang:
            he_partner = TIAN_GAN_HE.get(op_gan, '')
            if he_partner and any(g == he_partner for g in natal_gans if g):
                jis.append({
                    'ji_type': f'{op_name}吉向·合去忌神',
                    'reason': f'{op_gz}运干{op_gan}为异党（忌神），原局{he_partner}合去之'
                              f'——去忌得忌喜（ans32 丙被辛合去主得财）',
                })
        # 运岁支六合原局异党支（两忌神合绊主吉）
        if op_zhi:
            for i, nz in enumerate(natal_zhis):
                if nz and _pair_hit(op_zhi, nz, LIU_HE) \
                        and ZHI_WX.get(nz, '') in yidang:
                    jis.append({
                        'ji_type': f'{op_name}吉向·合绊忌神',
                        'reason': f'{op_gz}运支{op_zhi}合{PILLAR_KEYS[i]}支{nz}（异党忌神）'
                                  f'——两忌神合绊主吉（ans32 卯戌合绊）',
                    })
                    break
    else:  # 从弱
        # 破从·日主得根：运岁支藏干（含余气，22期例6 戌中丁火墓库余气根）含日主五行
        if op_zhi:
            from mangpai.objective.canggan import get_canggan_mangpai
            # 得根合化豁免（K3-294批6 G5）：运岁支与原局支六合、或运支补全
            # 三合局（原局已有另两支）者，运支被原局合走/合化，所藏日主之根
            # 随合化而不立——日主实未得根，不破从。
            #   锚：yx-经理-4 甲辰运（辰与局申、子三合水局化财势，书明文「行
            #   甲辰大运，发财数亿」）、yx-富发财数千万 壬辰运（辰合到主位酉，
            #   书明文「幸行壬辰大运…辰合到主位酉，发财数千万」）；22期例6
            #   戌运（原局无合戌之支）破从不动。
            gen_he_hua = any(nz and _pair_hit(op_zhi, nz, LIU_HE)
                             for nz in natal_zhis)
            if not gen_he_hua:
                from mangpai.objective.constants import SAN_HE as _SANHE
                for _he, _wx in _SANHE.items():
                    if op_zhi in _he \
                            and all(p == op_zhi or p in natal_zhis for p in _he):
                        gen_he_hua = True
                        break
            for cg, _q in get_canggan_mangpai(op_zhi):
                if GAN_WX.get(cg, '') == dw and not gen_he_hua:
                    fans.append({
                        'fan_type': f'{op_name}反局·破从(日主得根)',
                        'severity': '重',
                        'reason': f'{op_gz}运岁支{op_zhi}藏{cg}为日主之根，日主得根有所依'
                                  f'而不肯从——破从（22期例6 从官格戌运丙火得根最差）',
                    })
                    break
        # 破从·合去日主（仅流年）：流年干五合日主，日主被合去
        if is_liunian and op_gan and TIAN_GAN_HE.get(op_gan) == day_gan:
            fans.append({
                'fan_type': '流年反局·破从(合去日主)',
                'severity': '重',
                'reason': f'流年干{op_gan}合日主{day_gan}——从格日主被合去，「日主没有了，'
                          f'如何从」，所从之财从他党（22期例8 丙子年丙辛合破财）',
            })
    return fans, jis


def _work_mode(work_actions: List[Dict], work_types: List[str], natal_zhis: List[str]) -> Dict:
    """原局做功方式：是否以冲为主、以合为主。

    zuogong 的 work_actions/work_types 漏检原局地支间的冲/合结构（如丑未冲做功
    未必标为「冲」action），故辅以原局地支两两六冲/六合检测兜底。
    """
    has_chong = any(wa.get('type') == '冲' and not wa.get('auxiliary') for wa in work_actions) \
        or any('冲' in (wt or '') for wt in (work_types or []))
    he_set = {'天干合', '地支合', '暗合', '半合'}
    has_he = any(wa.get('type') in he_set and not wa.get('auxiliary') for wa in work_actions) \
        or any('合' in (wt or '') for wt in (work_types or []))
    # 原局地支两两冲/合兜底
    nz = [z for z in (natal_zhis or []) if z]
    for i in range(len(nz)):
        for j in range(i + 1, len(nz)):
            if _pair_hit(nz[i], nz[j], LIU_CHONG):
                has_chong = True
            if _pair_hit(nz[i], nz[j], LIU_HE):
                has_he = True
    return {'has_chong': has_chong, 'has_he': has_he}


def _detect_dayun_fan(
    op_gan: str, op_zhi: str,
    natal_gans: List[str], natal_zhis: List[str],
    gshen: List[str], fei_shen: List[str],
    work_actions: List[Dict], work_types: List[str],
    day_gan: str,
    strength: str = '',
) -> List[Dict]:
    """单步大运反局检测（三大类型）。"""
    fans: List[Dict] = []
    inter = _op_interactions(op_gan, op_zhi, natal_gans, natal_zhis)
    gong_pos = set(gshen or [])

    # ── 类型一：破坏原局功神 ──
    # A14 收窄（294例批3）：类型一原文「穿害冲散功神位」——冲/穿毁功神方入
    # 反局（薄一波造辰穿卯锚；破财工程酉运酉冲卯=书明文强拆赔钱真阳锚）。
    # 运「合」功神多为做功应期（合到主位=得：十一发财运运合功神全假阳，
    # 如庚申运财合日支巳、壬辰运辰合日支酉）；「破」不在原文三式（破力最轻，
    # 非毁功主式）。例外守真阳：运破日主禄/刃=破护身体（阴阳逆转心法，
    # 巨富丑运丙子运子破酉刃、书明文该运入狱锚）。
    hits_gong = [x for x in inter
                 if x['target_pos'] in gong_pos and x['type'] in ('冲', '穿')]
    if op_zhi and day_gan:
        from mangpai.objective.shensha import _YANG_REN_FULL as _YR
        lr_chars = {LU.get(day_gan, '')} | set(_YR.get(day_gan, []))
        lr_chars.discard('')
        hits_gong += [x for x in inter
                      if x['type'] == '破' and x['target_pos'] in gong_pos
                      and x['target_elem'] in lr_chars]
    if hits_gong:
        fans.append({
            'fan_type': '大运反局·类型一(破坏功神)',
            'severity': '重',
            'reason': '；'.join(h['desc'] for h in hits_gong)
                      + '——运岁穿害/冲散核心功神，原局之功无法施展',
        })
    # 杀临攻身（身弱忌神临旺，b67 复例二锚：「丙子运子水忌神旺」戊寅己卯
    # 庚辰年破财）：身弱（非从格——从格行运由破从规则另管）+ 运支为官杀
    # 五行 + 原局官杀明现透干 → 虚杀逢根临旺攻身。杀不透干者不论（原局
    # 无杀，运杀自成气候非「逢根」）。判别面：全库仅 b67 一例（身弱杀运
    # 为制杀应期者皆身强或杀不透，不命中）。
    if strength == '身弱' and op_zhi and day_gan:
        _dw = GAN_WX.get(day_gan, '')
        _sha_wx = next((w for w, c in WX_KE.items() if c == _dw), '')
        if _sha_wx and ZHI_WX.get(op_zhi, '') == _sha_wx \
                and any(GAN_WX.get(g, '') == _sha_wx for g in natal_gans if g):
            fans.append({
                'fan_type': '大运反局·类型一(杀临攻身)',
                'severity': '重',
                'reason': f'身弱，运支{op_zhi}为官杀（{_sha_wx}）临旺之地，原局'
                          f'官杀明现透干虚杀逢根——忌神临旺攻身（b67 丙子运'
                          f'子水忌神旺破财锚）',
            })
    # 忌神反客（大运侧移除，A14）：原文「忌神得运来生助，反客为主」依赖
    # zuogong 废神判据，实证不可复现——案例一书锚机制为辰支生申（申=被制
    # 忌神），而本引擎 zuogong 判申为功神，原实现实靠丙干生戊偶合命中；
    # 判别集 4 例全假阳（经理-2 戌生庚、老师 午生己、煤矿-2 壬生乙、经理-4
    # 甲生丙，书皆明文该运发财），零真阳（巨富丑运丙子真阳由破刃+伏吟激刑
    # 承载）。流年侧「引动忌神」保留。

    # ── 类型二：改变做功方式（冲合互变）──
    mode = _work_mode(work_actions, work_types, natal_zhis)
    if mode['has_chong']:
        # A14 收窄：运合须合住「原局冲做功参与字」方为变冲为合——冲对之字，
        # 或入墓于冲对之库的原局字（案例三卯合申：申入丑墓、参与丑未冲功锚）；
        # 任意运合即判为泛触（资本运营酉合辰/经理-2丙合辛皆假阳）。合主位
        # （日/时）之字=护体解冲（合能解冲），豁免（医师卯运卯暗合日支申，
        # 书明文伤官生财年入百万=吉运锚）。
        _nz = [z for z in natal_zhis if z]
        chong_chars: set = set()
        for _i in range(len(_nz)):
            for _j in range(_i + 1, len(_nz)):
                if _pair_hit(_nz[_i], _nz[_j], LIU_CHONG):
                    chong_chars.update((_nz[_i], _nz[_j]))
        _tombs = {c for c in chong_chars if c in TOMB_MAP}
        if _tombs:
            for _e, _w in ([(e, GAN_WX.get(e, '')) for e in natal_gans if e]
                           + [(z, ZHI_WX.get(z, '')) for z in _nz]):
                if _w and any(_w in TOMB_MAP.get(t, []) for t in _tombs):
                    chong_chars.add(_e)
        he_hits = [x for x in inter if x['type'] in _HE_TYPES
                   and x['target_elem'] in chong_chars
                   and not x['target_pos'].startswith(('day_', 'hour_'))]
        if he_hits:
            fans.append({
                'fan_type': '大运反局·类型二(冲变合)',
                'severity': '中',
                'reason': '原局以冲做功，运来'
                          + '；'.join(h['desc'] for h in he_hits)
                          + '——合住冲局，做功方式反转（喜冲怕逢合）',
            })
    if mode['has_he']:
        # 原局喜合怕逢冲：运来冲合做功之字 → 合变冲（破）
        chong_hits = [x for x in inter if x['type'] in _CHONG_TYPES]
        if chong_hits:
            fans.append({
                'fan_type': '大运反局·类型二(合变冲)',
                'severity': '中',
                'reason': '原局以合做功，运来'
                          + '；'.join(h['desc'] for h in chong_hits)
                          + '——冲开合局，做功方式反转（喜合怕逢冲）',
            })
    # 闭库/开库：运合原局墓库位 → 闭库（合变冲闭库反局）
    # A14 收窄：须原局有冲开该库之冲（原局赖冲开库做功，合闭之方为反局
    # ——案例四子合丑，原局丑未冲开财库锚）；库未被冲开做功者运合之非闭库
    # （资本运营酉合辰/老师午合未皆假阳）。
    if op_zhi:
        for i, nz in enumerate(natal_zhis):
            if nz in TOMB_MAP and _pair_hit(op_zhi, nz, LIU_HE) \
                    and any(oz and oz != nz and _pair_hit(nz, oz, LIU_CHONG)
                            for oz in natal_zhis):
                fans.append({
                    'fan_type': '大运反局·类型二(合闭墓库)',
                    'severity': '中',
                    'reason': f'运{op_zhi}合{PILLAR_KEYS[i]}支{nz}墓库——闭库，'
                              f'墓中之物被困，原局墓用做功失效',
                })
                break

    # ── 类型三：伏吟/三刑（A14 大运口径：单字伏吟/自刑不即反局，见函数注）──
    fy = _detect_fuyin_jihua_dayun(op_zhi, natal_zhis)
    # 伏吟干被克坏（案例五锚：乙酉运乙伏吟年干、被原局辛金克坏——乙为辰墓
    # 之透，克乙=坏辰墓功神，此运大凶坐牢没收财产）：运干伏吟原局非日主
    # 之干，且原局有干克（非合）之。日主伏吟不论（体非功，煤矿-2 壬午运
    # 壬伏吟日干、书明文发财十亿锚）。
    if op_gan and op_gan != day_gan and op_gan in (g for g in natal_gans if g):
        _ow = GAN_WX.get(op_gan, '')
        _ke = next((g for g in natal_gans
                    if g and g != op_gan
                    and WX_KE.get(GAN_WX.get(g, ''), '') == _ow
                    and TIAN_GAN_HE.get(g) != op_gan), '')
        if _ke:
            fy.append(f'{op_gan}伏吟被原局{_ke}克坏')
    sx = _detect_sanxing_dayun(op_zhi, natal_zhis)
    if fy or sx:
        fans.append({
            'fan_type': '大运反局·类型三(伏吟三刑)',
            'severity': '中',
            'reason': ('；'.join(fy + sx))
                      + '——运岁伏吟激刑/三刑激化原局内部矛盾，反复动荡',
        })

    return fans


def _detect_liunian_fan(
    op_gan: str, op_zhi: str,
    natal_gans: List[str], natal_zhis: List[str],
    gshen: List[str], fei_shen: List[str],
    work_actions: List[Dict], work_types: List[str],
    day_gan: str,
    dy_gan: str, dy_zhi: str,
) -> Tuple[List[Dict], List[Dict]]:
    """单流年反局检测（两大类型）。返回 (流年反局, 岁运联动)。"""
    fans: List[Dict] = []
    liandong: List[Dict] = []
    inter = _op_interactions(op_gan, op_zhi, natal_gans, natal_zhis)
    gong_pos = set(gshen or [])

    # ── 类型一：流年单独引动忌神/破坏功神/改做功方式 ──
    hits_gong = [x for x in inter
                 if x['target_pos'] in gong_pos and x['type'] in _HARM_TYPES]
    if hits_gong:
        fans.append({
            'fan_type': '流年反局·类型一(破坏功神)',
            'severity': '重',
            'reason': '；'.join(h['desc'] for h in hits_gong)
                      + '——流年冲合刑穿功神处，当年必有是非',
        })
    js = _detect_jishen_fufu(op_gan, op_zhi, natal_gans, natal_zhis, fei_shen)
    if js:
        fans.append({
            'fan_type': '流年反局·类型一(引动忌神)',
            'severity': '中',
            'reason': '；'.join(js),
        })
    lr = _detect_lu_ren_fangg(op_zhi, day_gan, natal_zhis)
    if lr:
        fans.append({
            'fan_type': '流年反局·类型一(禄刃倒戈)',
            'severity': '重',
            'reason': lr,
        })
    # 冲合互变（流年改做功方式）
    mode = _work_mode(work_actions, work_types, natal_zhis)
    if mode['has_chong'] and any(x['type'] in _HE_TYPES for x in inter):
        fans.append({
            'fan_type': '流年反局·类型一(冲变合)',
            'severity': '中',
            'reason': '原局以冲做功，流年来合——做功方式被改，事与愿违',
        })
    if mode['has_he'] and any(x['type'] in _CHONG_TYPES for x in inter):
        fans.append({
            'fan_type': '流年反局·类型一(合变冲)',
            'severity': '中',
            'reason': '原局以合做功，流年来冲——做功方式被改，事与愿违',
        })
    # 流年引动伏吟/三刑（流年+原局组成三刑，或伏吟原局柱）
    fy = _detect_fuyin(op_gan, op_zhi, natal_gans, natal_zhis)
    sx = _detect_sanxing(op_zhi, natal_zhis)
    if fy or sx:
        fans.append({
            'fan_type': '流年反局·类型一(伏吟三刑)',
            'severity': '中',
            'reason': ('；'.join(fy + sx))
                      + '——流年伏吟/三刑搅局，破坏原局单一做功，是非突发',
        })

    # ── 类型二：岁运联动（天地合/三刑/双冲，最凶）──
    sui_fans: List[Dict] = []
    if dy_gan and dy_zhi:
        # 天地合：流年干合大运干 + 流年支合大运支
        tian_he = TIAN_GAN_HE.get(op_gan) == dy_gan
        di_he = _pair_hit(op_zhi, dy_zhi, LIU_HE)
        if tian_he and di_he:
            sui_fans.append({
                'fan_type': '岁运联动·天地合',
                'severity': '极重',
                'reason': f'流年{op_gan}{op_zhi}与大运{dy_gan}{dy_zhi}天合地合'
                          f'——锁住原局用神/功神，祸难移（岁运反局最凶者）',
            })
        # 双冲：流年干克大运干 + 流年支冲大运支
        ln_gw, dy_gw = GAN_WX.get(op_gan, ''), GAN_WX.get(dy_gan, '')
        gan_ke = (ln_gw and dy_gw and
                  (WX_KE.get(ln_gw) == dy_gw or WX_KE.get(dy_gw) == ln_gw)
                  and TIAN_GAN_HE.get(op_gan) != dy_gan)
        zhi_chong = _pair_hit(op_zhi, dy_zhi, LIU_CHONG)
        if gan_ke and zhi_chong:
            sui_fans.append({
                'fan_type': '岁运联动·双冲',
                'severity': '极重',
                'reason': f'流年{op_gan}{op_zhi}与大运{dy_gan}{dy_zhi}干克支冲'
                          f'——激烈冲击原局，伤残死别在须臾',
            })
        # 三刑：流年支+大运支+原局构成完整三刑
        pool = set(z for z in natal_zhis if z) | {op_zhi, dy_zhi}
        for g in _SANXING_GROUPS:
            if g <= pool:
                sui_fans.append({
                    'fan_type': '岁运联动·三刑',
                    'severity': '极重',
                    'reason': f'流年{op_zhi}+大运{dy_zhi}+原局构成'
                              f'{''.join(sorted(g))}三刑——搅局破原局单一做功，无事生非',
                })
                break
        # 流年支刑大运支（二支刑，次凶）
        if _pair_hit(op_zhi, dy_zhi, XING_PAIRS) and not sui_fans:
            sui_fans.append({
                'fan_type': '岁运联动·相刑',
                'severity': '重',
                'reason': f'流年{op_zhi}刑大运{dy_zhi}——是非纠纷，搅动运局',
            })
    fans.extend(sui_fans)
    liandong = sui_fans  # 岁运联动单列

    return fans, liandong


def analyze_yunfan(
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    dayun_list: Optional[List[Dict]] = None,
    liunian_list: Optional[List[Dict]] = None,
    current_dayun: Optional[Dict] = None,
    natal_work_actions: Optional[List[Dict]] = None,
    natal_gong_shen: Optional[List[str]] = None,
    natal_fei_shen: Optional[List[str]] = None,
    natal_work_types: Optional[List[str]] = None,
    day_he_type: Optional[str] = None,
    kong_wang: Any = None,
) -> Dict:
    """岁运反局分析：大运反局 / 流年反局 / 岁运联动 三位一体。

    统一消费 zuogong_confirm（原局做功/功神废神）+ zhengfan（原局正反局基线）
    + dayun/liunian（运岁互动）。原局做功数据缺省时本函数自调 analyze_zuogong。

    Args:
        natal_gans/natal_zhis: 原局四柱天干/地支 [year,month,day,hour]。
        day_gan: 日干。
        dayun_list: 大运柱列表，每项 {gz|gan+zhi, start_age, end_age, order}。
        liunian_list: 流年柱列表，每项 {gz|gan+zhi, year}。
        current_dayun: 流年所处大运柱 {gz|gan+zhi}（岁运联动判定所需）。
        natal_work_actions/gong_shen/fei_shen/work_types: 原局做功数据（缺省自调）。
        day_he_type: 日干合类型（合财/合官，透传 zhengfan）。
        kong_wang: 空亡数据（透传 zuogong）。

    Returns:
        {
          'natal_zhengfan': {...},          # 原局正反局基线
          'dayun_fan': [大运反局...],      # 每步大运的反局类型
          'liunian_fan': [流年反局...],    # 每流年的反局类型
          'sui_yun_liandong': [岁运联动...], # 天地合/三刑/双冲（最凶，单列）
          'summary': str,
        }
    """
    natal_gans = natal_gans or []
    natal_zhis = natal_zhis or []

    # ── 原局做功数据（缺省自调 analyze_zuogong）──
    if natal_work_actions is None or natal_gong_shen is None or natal_fei_shen is None:
        try:
            zg = analyze_zuogong(
                day_gan, natal_zhis[PILLAR_KEYS.index('day')] if len(natal_zhis) == 4 else '',
                natal_gans[0] if len(natal_gans) > 0 else '', natal_zhis[0] if len(natal_zhis) > 0 else '',
                natal_gans[1] if len(natal_gans) > 1 else '', natal_zhis[1] if len(natal_zhis) > 1 else '',
                natal_gans[3] if len(natal_gans) > 3 else '', natal_zhis[3] if len(natal_zhis) > 3 else '',
                kong_wang=kong_wang,
            ) if len(natal_gans) == 4 and len(natal_zhis) == 4 else {}
        except Exception:
            zg = {}
        work_actions = natal_work_actions if natal_work_actions is not None else (zg.get('work_actions') or [])
        gshen = natal_gong_shen if natal_gong_shen is not None else (zg.get('gong_shen') or [])
        fei = natal_fei_shen if natal_fei_shen is not None else (zg.get('fei_shen') or [])
        wtypes = natal_work_types if natal_work_types is not None else (zg.get('work_types') or [])
    else:
        work_actions = natal_work_actions
        gshen = natal_gong_shen
        fei = natal_fei_shen
        wtypes = natal_work_types or []

    # ── 原局正反局基线（zhengfan）──
    try:
        natal_zf = analyze_zhengfan(work_actions, day_he_type, natal_gans, natal_zhis)
    except Exception:
        natal_zf = {'configuration': '基线判定失败', 'type': 'neutral'}

    dayun_fan: List[Dict] = []
    dayun_ji: List[Dict] = []
    # G5：从格行运规则（破从/合去忌神）——strength/所从 全运岁共用，一次判得
    try:
        _strength = classify_strength(day_gan, natal_gans, natal_zhis)
        _cong_label = classify_cong_target(
            day_gan, natal_gans, natal_zhis, _strength).get('label', '')
    except Exception:
        _strength, _cong_label = '', ''
    for entry in (dayun_list or []):
        gz = entry.get('gz', '')
        if gz and len(gz) >= 2:
            gan, zhi = gz[0], gz[1]
        else:
            gan, zhi = entry.get('gan', ''), entry.get('zhi', '')
        if not (gan or zhi):
            continue
        fans = _detect_dayun_fan(
            gan, zhi, natal_gans, natal_zhis, gshen, fei, work_actions, wtypes,
            day_gan, strength=_strength)
        # G5 破从/合去（大运级）
        pc_fans, pc_jis = _detect_po_cong(
            gan, zhi, day_gan, natal_gans, natal_zhis, _strength, _cong_label,
            is_liunian=False)
        fans.extend(pc_fans)
        if fans:
            dayun_fan.append({
                'order': entry.get('order', len(dayun_fan) + 1),
                'gz': f'{gan}{zhi}',
                'start_age': entry.get('start_age', 0),
                'end_age': entry.get('end_age', 0),
                'fans': fans,
            })
        if pc_jis:
            dayun_ji.append({
                'order': entry.get('order', len(dayun_ji) + 1),
                'gz': f'{gan}{zhi}',
                'start_age': entry.get('start_age', 0),
                'end_age': entry.get('end_age', 0),
                'jis': pc_jis,
            })

    # ── 当前大运干支（流年岁运联动所需）──
    dy_gan, dy_zhi = '', ''
    if current_dayun:
        gz = current_dayun.get('gz', '')
        if gz and len(gz) >= 2:
            dy_gan, dy_zhi = gz[0], gz[1]
        else:
            dy_gan, dy_zhi = current_dayun.get('gan', ''), current_dayun.get('zhi', '')

    liunian_fan: List[Dict] = []
    liunian_ji: List[Dict] = []
    sui_yun_liandong: List[Dict] = []
    for entry in (liunian_list or []):
        gz = entry.get('gz', '')
        if gz and len(gz) >= 2:
            gan, zhi = gz[0], gz[1]
        else:
            gan, zhi = entry.get('gan', ''), entry.get('zhi', '')
        if not (gan or zhi):
            continue
        fans, liandong = _detect_liunian_fan(
            gan, zhi, natal_gans, natal_zhis, gshen, fei,
            work_actions, wtypes, day_gan, dy_gan, dy_zhi)
        # G5 破从/合去（流年级：含合去日主）
        pc_fans, pc_jis = _detect_po_cong(
            gan, zhi, day_gan, natal_gans, natal_zhis, _strength, _cong_label,
            is_liunian=True)
        fans.extend(pc_fans)
        if fans:
            liunian_fan.append({
                'year': entry.get('year', 0),
                'gz': f'{gan}{zhi}',
                'dayun_gz': f'{dy_gan}{dy_zhi}' if dy_gan and dy_zhi else '',
                'fans': fans,
            })
        if pc_jis:
            liunian_ji.append({
                'year': entry.get('year', 0),
                'gz': f'{gan}{zhi}',
                'dayun_gz': f'{dy_gan}{dy_zhi}' if dy_gan and dy_zhi else '',
                'jis': pc_jis,
            })
        if liandong:
            sui_yun_liandong.append({
                'year': entry.get('year', 0),
                'gz': f'{gan}{zhi}',
                'dayun_gz': f'{dy_gan}{dy_zhi}' if dy_gan and dy_zhi else '',
                'liandong': liandong,
            })

    # ── 摘要 ──
    parts = [f'原局{natal_zf.get("configuration","")}({natal_zf.get("type","")})']
    if dayun_fan:
        parts.append(f'{len(dayun_fan)}步大运反局')
    if liunian_fan:
        parts.append(f'{len(liunian_fan)}流年反局')
    if sui_yun_liandong:
        parts.append(f'{len(sui_yun_liandong)}岁运联动(最凶)')
    if dayun_ji or liunian_ji:
        parts.append(f'{len(dayun_ji) + len(liunian_ji)}运岁合去忌神(吉向)')

    return {
        'natal_zhengfan': natal_zf,
        'dayun_fan': dayun_fan,
        'liunian_fan': liunian_fan,
        'sui_yun_liandong': sui_yun_liandong,
        'dayun_ji': dayun_ji,      # G5 大运吉向（合去/合绊忌神，标注不入凶链）
        'liunian_ji': liunian_ji,  # G5 流年吉向（同上）
        'summary': '；'.join(parts),
    }


def current_fan_slice(
    yunfan_result: Optional[Dict],
    current_dayun_gz: str = '',
    *,
    include_dayun: bool = True,
    include_liunian: bool = True,
) -> Dict:
    """从 analyze_yunfan 全量结果抽取「当前运岁」反局切片，供方向否决链消费。

    大运反局只保留当前大运柱（gz 匹配 current_dayun_gz；空串=调用方已确认
    传入列表即当前运，全保留）；流年反局/岁运联动按 include_liunian 取全量
    （调用方喂入的流年即所断之岁，不再按公历年过滤）。

    设计约束（A1）：切片仅供 caiming/guanming/zhiye 的方向否决链
    （yongshen.assess_direction_signals）消费；engine 仅在运岁为显式输入时
    构造切片——自动构造的流年（_auto_liunian_list）仅作「当下」展示锚点，
    其三岁窗口启发式命中率高，入否决会污染终身财命/官命口径，故不入链。
    """
    yf = yunfan_result or {}
    dayun_fan = list(yf.get('dayun_fan') or [])
    dayun_ji = list(yf.get('dayun_ji') or [])
    if include_dayun and current_dayun_gz:
        dayun_fan = [d for d in dayun_fan if d.get('gz') == current_dayun_gz]
        dayun_ji = [d for d in dayun_ji if d.get('gz') == current_dayun_gz]
    if not include_dayun:
        dayun_fan = []
        dayun_ji = []
    liunian_fan = list(yf.get('liunian_fan') or []) if include_liunian else []
    liandong = list(yf.get('sui_yun_liandong') or []) if include_liunian else []
    liunian_ji = list(yf.get('liunian_ji') or []) if include_liunian else []
    return {
        'dayun_fan': dayun_fan,
        'liunian_fan': liunian_fan,
        'sui_yun_liandong': liandong,
        'dayun_ji': dayun_ji,      # G5 吉向切片（合去/合绊忌神，标注）
        'liunian_ji': liunian_ji,
    }


__all__ = ['analyze_yunfan', 'current_fan_slice']
