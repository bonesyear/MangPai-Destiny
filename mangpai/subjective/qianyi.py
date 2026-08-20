# -*- coding: utf-8 -*-
"""
qianyi - 盲派迁移/远行 marker + 迁移应期窗·主观层（subjective）

理论来源（缺口批1，设计=缺口方案归档 kimi-gaps-plan-2026-08-20 §一，
行号已回书核对）：
  查法底座：zhongji:1560-1567（盲派三支皆马+年日双查+逢合=停留）；
  口诀：gaoji:6710-6715/6757-6760「马星逢合动则止，马星逄冲急如焚」；
  宫位空间：lixiangxue:4114（年=远方/时=门户/月=祖籍/日=现居）、
           gaoji:5838-5865（年柱动主离乡、月日冲=背井离乡、日时合=安居）；
  总纲：shouke:3600-3602「马冲在哪儿，离开哪儿。马合在哪，留在哪儿」；
  合到门户：zhongji:4179「丙辛合到门户上」+ lixiangxue:6571「甲运合己，
           合到门户」——两书同构互证；
  或然机制：shouke:6692（马星伏吟而动）、shouke:72（流年冲年/时支=冲出，
           书自承「未必所有人都会出门」）。

定位与边界：
  不重造马星查法（复用 objective/shensha 的 _YI_MA 三支皆马表）；
  不重造岁运扫描管线（仿 zinv 消费 engine 透传的 dy/ln 干支序列）。
  ⚠️ 措辞红线：书从未给出「出国 vs 国内迁移」判别边界（zhongji:4179 与
  gaoji:17390 结构同构而结论一为出国一为调动外省），故本模块输出措辞上限
  「迁移/远行/离乡」，任何 desc/note/summary 不出「出国/移民/海外」硬断语；
  「出国」级表达仅属 LLM 叙事层修辞，不作引擎逻辑结论。
  置信度自承：盲派三支皆马查法马星多、动象频（gaoji:15803 书自承），
  伏吟/冲出两机制带「或然」标签（shouke:716 有伏吟外出未应验实录）。

判定维度（缺口批1 立法范围 §一.4）：
  1. qianyi_yuanju 原局三 marker：
     - beijing_lixiang：月日支相冲=背井离乡（gaoji:5857）；
     - anju：日时支相合=安居乐业（gaoji:5858 反向锚）；
     - ma_lin_nianshi：驿马（年日双查口径）落年/时柱=多动远行倾向
       （gaoji:6735 案例九「马星在年时，主远行」）。
  2. qianyi_yingqi 应期窗：
     - move_windows：马逢冲（岁运支冲原局马星支，shouke:3602+gaoji:6757）、
       合到门户（岁运干与原局年/时干成五合，zhongji:4179+lixiangxue:6571）、
       马星伏吟（流年支与原局马星支伏吟，shouke:6692，或然）、
       冲出年时（流年支冲年/时支，shouke:72，或然）；
     - stay_windows：马逢合=停留不动（zhongji:1567+gaoji:6757+shouke:3602
       后半「马合在哪，留在哪儿」）。
       备案：gaoji:6735 案例九「行申运（巳申合，马动）」与同节口诀「逢合
       动则止」相矛盾，本模块从口诀锚（双锚+总纲）归 stay，案例九异读不另立。
  3. summary：只述迁移倾向与应期窗，措辞上限「迁移/远行/离乡」。

收档不立（缺口批1 §一.4）：出国级别判定、方位推断、出行吉凶、六亲迁移。

分层位置：subjective/，单向依赖 objective（constants/shensha 表），
          不反向依赖 engine。
置信度：中（动象高频是书法本身属性，或然标签+措辞上限控制）。
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    TIAN_GAN_HE, LIU_HE, LIU_CHONG, is_pillars,
)
from mangpai.objective.shensha import _YI_MA  # 三支皆马表（zhongji:1563-1565）

_PILLAR_KEYS = ['year', 'month', 'day', 'hour']
# 宫位空间（lixiangxue:4114 + gaoji:5843-5846）：年=远方、月=祖籍、日=现居、时=门户
_PILLAR_SPACE = {'year': '远方', 'month': '祖籍/家乡', 'day': '现居所', 'hour': '门户/外出'}


def _pair_in(a: str, b: str, pairs) -> bool:
    return (a, b) in pairs or (b, a) in pairs


def _gz_of(entry) -> str:
    """岁运条目 → 干支串（兼容 {'gz'}/{'gan','zhi'}/纯字符串，zinv 同式）。"""
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        gz = entry.get('gz', '')
        if gz:
            return gz
        return (entry.get('gan', '') or '') + (entry.get('zhi', '') or '')
    return ''


def analyze_qianyi(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    dayun_list: Optional[List] = None,
    liunian_list: Optional[List] = None,
) -> Dict:
    """迁移/远行 marker + 迁移应期窗。

    签名对齐 analyze_zinv 惯例；岁运序列由 engine 透传（da_yun/liunian），
    测试按 zinv 哨兵惯例手动喂入。缺岁运序列时应期窗空转（仅出原局 marker）。

    Returns:
        {
          'qianyi_yuanju': {'beijing_lixiang': bool, 'anju': bool,
                            'ma_lin_nianshi': {'hit': bool, 'positions': [...]},
                            'markers': [str], 'desc': str},
          'qianyi_yingqi': {'move_windows': [...], 'stay_windows': [...],
                            'desc': str},
          'summary': str,
        }
        window = {'dayun','liunian','mechanism','pillar','confidence',
                  'basis','note'}
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
    _empty = {
        'qianyi_yuanju': {
            'beijing_lixiang': False, 'anju': False,
            'ma_lin_nianshi': {'hit': False, 'positions': []},
            'markers': [], 'desc': '四柱不全，无法判定迁移倾向',
        },
        'qianyi_yingqi': {'move_windows': [], 'stay_windows': [], 'desc': ''},
        'summary': '四柱不全，无法判定迁移倾向',
    }
    if not (len(gans) == 4 and len(zhis) == 4):
        return _empty

    # ── 马星支集合（盲派三支皆马，复用 shensha._YI_MA 表）──
    # ma_union_all：四柱各起取并集（shouke:3600「申子辰寅为马星」口径）；
    # ma_union_yr：年日双查并集（zhongji:1566「以年柱和日柱为主」，
    #              gaoji:6735 案例九马临年时判据口径）。
    ma_union_all: Set[str] = set()
    for z in zhis:
        ma_union_all.update(_YI_MA.get(z, []))
    ma_union_yr: Set[str] = set(_YI_MA.get(zhis[0], [])) | set(_YI_MA.get(zhis[2], []))
    # 原局在局的马星支 → 柱位（「马冲在哪儿，离开哪儿」的宫位锚，shouke:3602）
    ma_positions: Dict[str, str] = {
        z: _PILLAR_KEYS[i] for i, z in enumerate(zhis) if z in ma_union_all}

    # ── 1. 原局三 marker ──
    markers: List[str] = []
    beijing = _pair_in(zhis[1], zhis[2], LIU_CHONG)
    if beijing:
        markers.append('月日支相冲，背井离乡、离祖籍发展之象（gaoji:5857）')
    anju = _pair_in(zhis[2], zhis[3], LIU_HE)
    if anju:
        markers.append('日时支相合，安居现居地之象（gaoji:5858）')
    ns_positions = [k for k in ('year', 'hour')
                    if zhis[_PILLAR_KEYS.index(k)] in ma_union_yr]
    ma_lin = {'hit': bool(ns_positions), 'positions': ns_positions}
    if ns_positions:
        markers.append('马星临年/时柱（远方/门户之位），多动远行倾向（gaoji:6735）')
    if beijing and anju:
        # 月日冲与日时合并存：书未给优先级，两 marker 并列呈现
        markers.append('冲合并见，离乡与安居两象并陈（书未定夺，marker 级并列）')
    yuanju_desc = ('；'.join(markers) if markers
                   else '原局无明显迁移/安居标志')

    # ── 2. 应期窗扫描 ──
    move_windows: List[Dict] = []
    stay_windows: List[Dict] = []
    _seen: Set = set()

    def _emit(bucket: List[Dict], dayun: str, liunian: str, mechanism: str,
              pillar: str, confidence: str, basis: str, note: str):
        key = (dayun, liunian, mechanism, pillar)
        if key in _seen:
            return
        _seen.add(key)
        bucket.append({'dayun': dayun, 'liunian': liunian, 'mechanism': mechanism,
                       'pillar': pillar, 'confidence': confidence,
                       'basis': basis, 'note': note})

    def _scan(gz: str, is_liunian: bool):
        if not gz:
            return
        dg, dz = gz[0], gz[1] if len(gz) > 1 else ''
        dy, ln = ('', gz) if is_liunian else (gz, '')
        # 合到门户：岁运干与原局年干（远方）/时干（门户）成五合
        # （zhongji:4179 丙辛合时干 + lixiangxue:6571 甲运合时干己——双锚同构）
        partner = TIAN_GAN_HE.get(dg, '')
        for gi in (0, 3):
            if partner and gans[gi] == partner:
                pk = _PILLAR_KEYS[gi]
                _emit(move_windows, dy, ln, '合到门户', pk, '中',
                      'zhongji:4179;lixiangxue:6571',
                      f'{dg}合{pk == "year" and "年" or "时"}干{partner}'
                      f'（{_PILLAR_SPACE[pk]}之位），合到门户，有迁移/远行之象')
        if not dz:
            return
        # 马逢冲/马逢合：岁运支冲合原局在局马星支（shouke:3602 总纲 +
        # gaoji:6757 口诀「马星逢合动则止，马星逄冲急如焚」）
        for mz, pk in sorted(ma_positions.items()):
            if _pair_in(dz, mz, LIU_CHONG):
                _emit(move_windows, dy, ln, '马逢冲', pk, '中',
                      'shouke:3600-3602;gaoji:6757',
                      f'{dz}冲{mz}（{_PILLAR_SPACE[pk]}之马星），'
                      f'马冲在哪儿离开哪儿，有迁移/远行之象')
            elif _pair_in(dz, mz, LIU_HE):
                _emit(stay_windows, dy, ln, '马逢合', pk, '中',
                      'zhongji:1567;gaoji:6757;shouke:3602',
                      f'{dz}合{mz}（{_PILLAR_SPACE[pk]}之马星），'
                      f'马合在哪留在哪儿，主停留/不动')
        # 或然两机制（流年锚，shouke:6692/72 均系流年书例，大运不扫）
        if is_liunian:
            # 马星伏吟：流年支与原局马星支伏吟（shouke:6692「马星伏吟而动」）
            if dz in ma_positions:
                _emit(move_windows, dy, ln, '马星伏吟', ma_positions[dz], '或然',
                      'shouke:6692',
                      f'流年{dz}与原局{_PILLAR_SPACE[ma_positions[dz]]}马星伏吟，'
                      f'或有迁移/远动之象（或然）')
            # 冲出年时：流年支冲年支/时支（shouke:72「冲出」，
            # 书自承「未必所有人都会出门」）
            for zi in (0, 3):
                if _pair_in(dz, zhis[zi], LIU_CHONG):
                    pk = _PILLAR_KEYS[zi]
                    _emit(move_windows, dy, ln, '冲出年时', pk, '或然',
                          'shouke:72',
                          f'流年{dz}冲{pk == "year" and "年支（远方/离祖）" or "时支（门户）"}'
                          f'{zhis[zi]}，冲出，或有出门远行之象（或然）')

    for entry in dayun_list or []:
        _scan(_gz_of(entry), is_liunian=False)
    for entry in liunian_list or []:
        _scan(_gz_of(entry), is_liunian=True)

    yingqi_desc = (
        '迁移应期窗：' + '；'.join(w['note'] for w in move_windows)
        if move_windows else '岁运序列内无明显迁移应期窗')
    if stay_windows:
        yingqi_desc += '；停留窗：' + '；'.join(w['note'] for w in stay_windows)

    # ── 3. summary（措辞上限「迁移/远行/离乡」，不出出国级断语）──
    parts: List[str] = []
    if beijing:
        parts.append('背井离乡倾向')
    if ma_lin['hit']:
        parts.append('马临年时多动倾向')
    if anju:
        parts.append('安居现居倾向')
    if move_windows:
        mech = '、'.join(sorted({w['mechanism'] for w in move_windows}))
        parts.append(f'迁移应期窗{len(move_windows)}处（{mech}）')
    if stay_windows:
        parts.append(f'停留窗{len(stay_windows)}处')
    summary = '迁移：' + ('；'.join(parts) if parts else '原局及岁运序列内无明显迁移/远行信号')

    return {
        'qianyi_yuanju': {
            'beijing_lixiang': beijing,
            'anju': anju,
            'ma_lin_nianshi': ma_lin,
            'markers': markers,
            'desc': yuanju_desc,
        },
        'qianyi_yingqi': {
            'move_windows': move_windows,
            'stay_windows': stay_windows,
            'desc': yingqi_desc,
        },
        'summary': summary,
    }


__all__ = ['analyze_qianyi']
