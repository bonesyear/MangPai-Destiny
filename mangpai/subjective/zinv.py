# -*- coding: utf-8 -*-
"""
zinv - 盲派子女岁运应期 + 借腹 marker·主观层（subjective）

理论来源：段建业《盲派命理高级内容篇》第十章案例三/四/十一/十二、
          《盲派命理授课教程》18-20（戊戌造一造三机制）/428、
          《盲派中级命理学》1911-1914（借腹同构）。
          设计规格：docs/kimi-d6a-zinv-design-20260819.md（D6a，书锚 F1-F10/H1-H4）。

定位与边界（D6a §3.1）：
  zinv = 子息**岁运应期**（得子窗/损子窗）+ **借腹/养子** marker。
  不重造星宫定位/有无/性别/优劣——那是 liuqin 已立之域，本模块只读消费
  liuqin 输出（child_star_cat/枭夺食 marker 语境），不重算星宫定位。

判定维度（D6b 立 4 项之 zinv 侧三项，书锚行号随行）：
  1. zixi_yingqi_dezi 得子应期窗：
     - 合动：岁运干与原局子息星透干成天干五合，或流年干为子息星到位
       而与大运动干/原局干成合（授课:18-20「丁卯年丁壬合怀孕」）。
     - 开墓：子息星/妻星之墓逢岁运冲开（授课:18-20「辰冲戌墓」+
       gaoji:14008-14009/14372-14373「运岁开库或填实，或有转机」口诀）。
     - 制枭：原局枭（偏印）明现而子息星为食伤（枭夺食潜势），岁运干
       合制枭印（gaoji:14087-14107「庚辰运，乙庚合，制住枭神，方得子」）。
  2. zixi_yingqi_sunzi 损子应期窗（引擎内部 marker 级，措辞中性，
     LLM 侧由 build_payload _scrub_death 统一兜底，本模块不自建过滤）：
     - 克到位：子息星克星于大运到位，且运干不合子息星（合则归合动，
       gaoji:14108-14128「己未运，己土克癸水」）。
     - 合去：克到位运中流年克星合走原局子息星
       （gaoji:14108-14128「戊寅年戊土合克癸水」）。
     - 穿引动：岁运支穿原局子息星所临之支。
       口径备案（修批 E4 裁定 a·改注，U1 P1-1）：直接书锚=gaoji:17465-17484
       （案例八「运逢己巳，巳火到位穿寅木」——岁运支穿原局子息支，与本实现
       逐字同构；书自承「疑案例有误或指他刑」故降权）。gaoji:14295-14312
       （案例十一）书机制实为「原局已有子未穿 + 运岁引动穿害力」（断语原文），
       其自身岁运（己丑/辛巳）不构成六穿、不触发本实现——锚与实现配对偏松，
       特此备案。(b) 补书据否决：F5 为唯一直锚（gaoji:17783-17810 系同案例
       重出，非独立书证），四书无第二处「岁运支穿原局支」明文。(c) 改实现
       否决：书未给「引动」具体口径（F6 己丑运/辛巳年如何引动书未明言），
       任何具体化皆工程自造，违书锚铁律。行为不变。
     - 「冲」增补候选收档（修批 E4）：仅 gaoji:14122「后巳运，巳亥冲，次子
       亦亡」一处直锚；gaoji:21038-21052（案例五）机制以「午冲子引动双子夹巳
       凶象」为主、「午为子息星之禄被冲」为辅，形态非同构——未达双锚，不立。
     - 枭夺食运：枭夺食潜势盘行枭（偏印）运（授课:428）。
     - 合神被克：合动之运干被流年干所克，合局解体
       （授课:18-20「戊克壬，壬不能合丁」）。
  3. jiefu 借腹/养子 marker：日支（妻宫）受穿 + 子息星/妻星入时墓
     （gaoji:14317-14334 案例十二 + zhongji:1911-1914/4165-4170 两书同构）。
  4. summary：只述应期与借腹，不复拼 liuqin 子息段。

分层位置：subjective/，单向依赖 objective + subjective.liuqin（只读其输出）。
          本模块不反向依赖 engine。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    TIAN_GAN_HE, LIU_CHONG, LIU_HAI, TOMB_MAP, PILLAR_KEYS, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.liuqin import (
    analyze_liuqin, _child_star_cat, _pillar_has_cat, _compute_shishen, _cat,
)


def _pair_in(a: str, b: str, pairs) -> bool:
    return (a, b) in pairs or (b, a) in pairs


def _child_wx(day_gan: str, cat: str) -> str:
    """子息星五行（与 liuqin.detect_zixi_youwu 同口径）。"""
    day_wx = GAN_WX.get(day_gan, '')
    if cat == '官杀':
        return WX_KE_ME.get(day_wx, '')
    if cat == '食伤':
        return WX_SHENG.get(day_wx, '')
    if cat == '财':
        return WX_KE.get(day_wx, '')
    return ''


def _benqi_shishen(day_gan: str, zhi: str) -> str:
    """地支本气藏干十神。"""
    cg = get_canggan_mangpai(zhi)
    return _compute_shishen(day_gan, cg[0][0]) if cg else ''


def _gz_of(entry) -> str:
    """岁运条目 → 干支串（兼容 {'gz'}/{'gan','zhi'}/纯字符串）。"""
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        gz = entry.get('gz', '')
        if gz:
            return gz
        return (entry.get('gan', '') or '') + (entry.get('zhi', '') or '')
    return ''


def analyze_zinv(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    gender: str = '男',
    *,
    relations: Optional[Dict] = None,
    liuqin_result: Optional[Dict] = None,
    dayun_list: Optional[List] = None,
    liunian_list: Optional[List] = None,
) -> Dict:
    """子女岁运应期（得子/损子窗）+ 借腹 marker。

    签名对齐 analyze_liuqin 惯例；岁运序列由 engine 透传（da_yun/liunian），
    测试按 liuqin/yingqi 惯例手动喂入。缺岁运序列时应期窗空转（仅出 jiefu）。

    Returns:
        {
          'zixi_yingqi_dezi':  {'windows': [...], 'desc': str},
          'zixi_yingqi_sunzi': {'windows': [...], 'desc': str},
          'jiefu': {'is_jiefu': bool, 'basis': [str], 'desc': str},
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
    _empty = {
        'zixi_yingqi_dezi': {'windows': [], 'desc': '四柱不全，无法判定子女应期'},
        'zixi_yingqi_sunzi': {'windows': [], 'desc': ''},
        'jiefu': {'is_jiefu': False, 'basis': [], 'desc': ''},
        'summary': '四柱不全，无法判定子女应期',
    }
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return _empty

    if relations is None:
        try:
            relations = detect_relations(
                day_gan, zhis[2], gans[0], zhis[0], gans[1], zhis[1],
                gans[3], zhis[3])
        except Exception:
            relations = {}
    if liuqin_result is None:
        try:
            liuqin_result = analyze_liuqin(day_gan, gans, zhis, gender,
                                           relations=relations)
        except Exception:
            liuqin_result = {}

    # 星定位唯一来源=liuqin 输出（不重造）
    cat = ((liuqin_result.get('zixi_youwu') or {}).get('child_star_cat')
           or _child_star_cat(day_gan, gans, zhis, gender))
    child_wx = _child_wx(day_gan, cat)
    ke_wx = WX_KE_ME.get(child_wx, '')          # 子息星之克星五行
    cai_wx = WX_KE.get(GAN_WX.get(day_gan, ''), '')  # 妻星（财）五行

    natal_child_gans: Set[str] = {
        gans[i] for i in (0, 1, 3)
        if gans[i] and _cat(_compute_shishen(day_gan, gans[i])) == cat}
    natal_xiao_gans: Set[str] = {
        gans[i] for i in (0, 1, 3)
        if gans[i] and _compute_shishen(day_gan, gans[i]) == '偏印'}
    child_zhis: Set[str] = {
        zhis[i] for i in range(4)
        if _pillar_has_cat(day_gan, gans[i], zhis[i], cat)}
    child_present = bool(natal_child_gans) or bool(child_zhis)

    # 枭夺食潜势：子息星=食伤且枭（偏印）明现（F1 书例原局卯木偏印旺；
    # liuqin 计数口径 marker 未达阈值时此结构仍在场，gaoji:14087-14107）
    xiao_present = bool(natal_xiao_gans) or any(
        _benqi_shishen(day_gan, z) == '偏印' for z in zhis)
    xiao_gate = (cat == '食伤') and xiao_present

    # 子息星/妻星之墓（开墓扫描对象，授课:18-20 妻星戌为丁火之墓）
    tomb_targets: Set[str] = set()
    for z in zhis:
        if z in TOMB_MAP:
            stored = TOMB_MAP[z]
            if child_wx in stored or (gender == '男' and cai_wx in stored):
                tomb_targets.add(z)

    dy_gzs = [g for g in (_gz_of(d) for d in (dayun_list or [])) if g]
    ln_gzs = [g for g in (_gz_of(l) for l in (liunian_list or [])) if g]

    dezi_windows: List[Dict] = []
    sunzi_windows: List[Dict] = []
    _seen: Set = set()

    def _emit(bucket: List[Dict], dayun: str, liunian: str,
              mechanism: str, basis: str, note: str):
        key = (dayun, liunian, mechanism)
        if key in _seen:
            return
        _seen.add(key)
        bucket.append({'dayun': dayun, 'liunian': liunian,
                       'mechanism': mechanism, 'basis': basis, 'note': note})

    # ── 大运级扫描 ──
    hedong_dy_gans: Set[str] = set()   # 合动运干（合神被克扫描对象）
    kedaowei_dy = False                # 克到位运在场（合去闸门）
    for gz in dy_gzs:
        dg, dz = gz[0], gz[1] if len(gz) > 1 else ''
        # 得子·合动：运干合原局子息星（授课:18-20 丁壬合）
        if TIAN_GAN_HE.get(dg) in natal_child_gans:
            hedong_dy_gans.add(dg)
            _emit(dezi_windows, gz, '', '合动', 'shouke:18-20',
                  f'运干{dg}合原局子息星{TIAN_GAN_HE[dg]}，星被合动，有得子/孕育之象')
        # 得子·制枭：枭夺食潜势盘，运干合制枭印（gaoji:14087-14107 乙庚合制枭）
        if xiao_gate and TIAN_GAN_HE.get(dg) in natal_xiao_gans:
            _emit(dezi_windows, gz, '', '制枭', 'gaoji:14087-14107',
                  f'运干{dg}合制枭神{TIAN_GAN_HE[dg]}，夺食之势得解，有得子之象')
        # 得子·开墓：运支冲开子息星/妻星之墓（授课:18-20 + gaoji:14008-14009/14372-14373）
        for t in sorted(tomb_targets):
            if dz and _pair_in(dz, t, LIU_CHONG):
                _emit(dezi_windows, gz, '', '开墓', 'gaoji:14008-14009/14372-14373;shouke:18-20',
                      f'运支{dz}冲开{t}墓，墓中子息/妻星得出，有得子之象')
        # 损子·克到位：运干为子息星克星且不合子息星
        # （gaoji:14108-14128 己未运己土克癸水；运干合星者归合动不论克——
        #  授课:18-20 壬戌运壬合丁仍主怀孕）
        if (child_present and dg and GAN_WX.get(dg) == ke_wx
                and TIAN_GAN_HE.get(dg) not in natal_child_gans):
            kedaowei_dy = True
            _emit(sunzi_windows, gz, '', '克到位', 'gaoji:14108-14128',
                  f'运干{dg}（{GAN_WX[dg]}）克子息星（{child_wx}）到位，子息星受创之象')
        # 损子·枭夺食运：枭夺食潜势盘行枭（偏印）运（授课:428）
        if xiao_gate and (dg and _compute_shishen(day_gan, dg) == '偏印'
                          or dz and _benqi_shishen(day_gan, dz) == '偏印'):
            _emit(sunzi_windows, gz, '', '枭夺食运', 'shouke:428',
                  f'运{gz}枭（偏印）旺地，夺食损子息星之象')
        # 损子·穿引动：运支穿原局子息星所临之支
        # （口径备案见模块 docstring——直锚 gaoji:17465-17484 降权；
        #  gaoji:14295-14312 实系「原局有穿+岁运引动」，修批 E4 裁定 a 改注）
        for cz in sorted(child_zhis):
            if dz and _pair_in(dz, cz, LIU_HAI):
                _emit(sunzi_windows, gz, '', '穿引动',
                      'gaoji:14295-14312;gaoji:17465-17484',
                      f'运支{dz}穿{cz}（子息星所临），子女宫星引动受创之象')
                break

    # ── 流年级扫描 ──
    for gz in ln_gzs:
        lg, lz = gz[0], gz[1] if len(gz) > 1 else ''
        # 得子·合动：流年干为子息星到位，与运干/原局干成合
        # （授课:18-20 丁卯年丁壬合怀孕——丁为子息星临流年而合运干壬）
        if lg and _cat(_compute_shishen(day_gan, lg)) == cat:
            partner = TIAN_GAN_HE.get(lg, '')
            hit_dy = next((d for d in dy_gzs if d and d[0] == partner), '')
            if hit_dy or partner in {gans[i] for i in (0, 1, 3) if gans[i]}:
                _emit(dezi_windows, hit_dy, gz, '合动', 'shouke:18-20',
                      f'流年{lg}子息星到位合{partner}，有得子/孕育之象')
        # 得子·开墓：流年支冲开子息星/妻星之墓
        for t in sorted(tomb_targets):
            if lz and _pair_in(lz, t, LIU_CHONG):
                _emit(dezi_windows, '', gz, '开墓', 'gaoji:14008-14009/14372-14373;shouke:18-20',
                      f'流年支{lz}冲开{t}墓，有得子/孕育之象')
        # 损子·合去：克到位运中，流年克星合走原局子息星
        # （gaoji:14108-14128 己未运中戊寅年戊合癸）
        if (kedaowei_dy and lg and TIAN_GAN_HE.get(lg) in natal_child_gans
                and GAN_WX.get(lg) == ke_wx):
            _emit(sunzi_windows, '', gz, '合去', 'gaoji:14108-14128',
                  f'流年{lg}合去子息星{TIAN_GAN_HE[lg]}（克星当运），子息星受创之象')
        # 损子·合神被克：合动之运干被流年干所克，合局解体
        # （授课:18-20「戊克壬，壬不能合丁」）
        if lg:
            for hg in sorted(hedong_dy_gans):
                if WX_KE.get(GAN_WX.get(lg, ''), '') == GAN_WX.get(hg, ''):
                    hit_dy = next((d for d in dy_gzs if d and d[0] == hg), '')
                    _emit(sunzi_windows, hit_dy, gz, '合神被克', 'shouke:18-20',
                          f'流年{lg}克合神{hg}，子息星之合解体，孕育有损之象')
                    break
        # 损子·穿引动：流年支穿原局子息星所临之支（备案见模块 docstring）
        for cz in sorted(child_zhis):
            if lz and _pair_in(lz, cz, LIU_HAI):
                _emit(sunzi_windows, '', gz, '穿引动',
                      'gaoji:14295-14312;gaoji:17465-17484',
                      f'流年支{lz}穿{cz}（子息星所临），子女宫星引动受创之象')
                break

    # ── 借腹/养子 marker：日支（妻宫）受穿 + 子息星/妻星入时墓 ──
    # （H2 gaoji:14317-14334 卯辰穿倒妻宫、庚辰年借腹生子
    #   + H3 zhongji:1911-1914/4165-4170 乙财在时上辰墓——两书同构）
    jiefu_basis: List[str] = []
    wa: List[Dict] = relations.get('work_actions') or []
    day_chuan = any(a.get('type') == '穿'
                    and 'day_zhi' in (a.get('from_pos', ''), a.get('to_pos', ''))
                    for a in wa)
    if day_chuan:
        jiefu_basis.append('日支（妻宫）受穿（gaoji:14317-14334）')
    hour_tomb_star = ''
    if zhis[3] in TOMB_MAP:
        for cg, _src in get_canggan_mangpai(zhis[3]):
            cg_cat = _cat(_compute_shishen(day_gan, cg))
            if cg_cat in (cat, '财'):
                hour_tomb_star = cg
                break
    if hour_tomb_star:
        jiefu_basis.append(
            f'{hour_tomb_star}（{_compute_shishen(day_gan, hour_tomb_star)}）'
            f'入时上{zhis[3]}墓（zhongji:1911-1914/4165-4170）')
    is_jiefu = day_chuan and bool(hour_tomb_star)
    jiefu = {
        'is_jiefu': is_jiefu,
        'basis': jiefu_basis if is_jiefu else [],
        'desc': ('日支受穿、子息星/妻星入时墓，有借腹/养子之象'
                 if is_jiefu else '无明显借腹/养子标志'),
    }

    dezi_desc = ('岁运引动，有得子/孕育之象：'
                 + '；'.join(w['note'] for w in dezi_windows)
                 if dezi_windows else '岁运序列内无明显得子应期窗')
    sunzi_desc = ('子息星受创/子女宫引动之象：'
                  + '；'.join(w['note'] for w in sunzi_windows)
                  if sunzi_windows else '岁运序列内无明显子息受创应期窗')

    parts: List[str] = []
    if dezi_windows:
        mech = '、'.join(sorted({w['mechanism'] for w in dezi_windows}))
        parts.append(f'得子应期窗{len(dezi_windows)}处（{mech}）')
    if sunzi_windows:
        mech = '、'.join(sorted({w['mechanism'] for w in sunzi_windows}))
        parts.append(f'子息受创应期窗{len(sunzi_windows)}处（{mech}）')
    if is_jiefu:
        parts.append('借腹/养子之象')
    summary = '子女应期：' + ('；'.join(parts) if parts else '岁运序列内无明显应期窗')

    return {
        'zixi_yingqi_dezi': {'windows': dezi_windows, 'desc': dezi_desc},
        'zixi_yingqi_sunzi': {'windows': sunzi_windows, 'desc': sunzi_desc},
        'jiefu': jiefu,
        'summary': summary,
    }


__all__ = ['analyze_zinv']
