# -*- coding: utf-8 -*-
"""
xiangmao - 盲派相貌 marker 层·主观层（subjective，轻量）

理论来源（缺口批2，设计=缺口方案归档 kimi-gaps-plan-2026-08-20 §二，
行号已回书核对——回核修正：gaoji:4035 慈禧造「相貌非绝色」系反例，
不作秀气正锚，仅备注；gaoji:3976 秀气主「头面」语境为破相，作辅锚）：
  主线1 秀气透干：zhongji:3914-3915「时上丙食，秀气……如是女命则秀气
        主漂亮，男命秀气主文章」；反条件 lixiangxue:6655「秀气并未透干，
        相貌平平」；chuji:1711 梦露造「金水相生为秀气」。
  主线2 金水伤官限辛：zhongji:1484-1485「辛金配癸水组合：金水伤官漂亮」；
        zhongji:5455 自带边界（庚金不算）；shouke:5394 梦露造「辛日主见癸
        长得漂亮」；反条件 shouke:474「辛金不宜多，多则不秀，又怕土重，
        埋没而无光」。
  主线3 活木见火：zhongji:4513 黛安娜造「乙木见火为美貌」；chuji:4371
        刘晓庆造「甲见火为开花，首先此人长得漂亮」；lixiangxue:6628-6630
        「甲木为活木，生火为花朵」。木死活消费 objective/wood_type 结果。
  主线4 眼象：zhongji:1482-1483「丙为眼框，癸为黑，为眼珠」「癸加丙，
        等于瞳孔」；lixiangxue:11124-11126「火土焦干癸水，双目无瞳……
        丙配癸才是瞳孔」。
  弱线1 伤官合官杀→魅力：gaoji:5618-5623 阮玲玉造「伤官庚金合七杀乙木，
        伤官有了吸引男人、魅力、性感的意向」；shouke:634-638 阮玲玉 vs
        美容师对照「庚金伤官不见官杀……伤食只单纯表现为技艺」。
  弱线2 身材曲线：zhongji:3981-3982「乙卯又是曲线好，身材好看」；
        zhongji:1484「己为身体（女性则曲线弯，性感；表现力强）」。

定位与红线（归档 §二.3）：
  纯 marker 层，无判定无档位——不判相貌等级，只产机制 marker+书锚 basis
  供 LLM 叙事层消费（仿 ganqing 定位：ganqing 管性情，xiangmao 管外形）。
  ⚠️ 措辞红线：任何 desc/note/summary 不出「美/丑/帅」结论词（无档位设计；
  书引短语仅作 basis 锚注随行，不作引擎结论）。
  置信度自承：三处书内条件从句（辛金限定/秀气须透干/伤官须见官杀）表明
  书自承为充分性倾向非定律；gaoji:4035 承认个案可反。弱线带「弱」标签。

收档不立（归档 §二.2/§二.4，如实标注）：
  贵相口诀（眼细而长=贵相，书未给干支触发条件，收录不入码）；
  难看反推（zhongji:5064 孤例，机制不明）；五行盛衰形体表
  （lixiangxue:1353-1484，传统《滴天髓》系通论非盲派特色）；
  配偶相貌（过散，叙事层素材）；身高定量。

分层位置：subjective/，单向依赖 objective（constants 表）与
          liuqin 十神工具，不反向依赖 engine。
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    GAN_WX, TIAN_GAN_HE, is_pillars,
)
from mangpai.subjective.liuqin import _compute_shishen

_PILLAR_KEYS = ['year', 'month', 'day', 'hour']


def analyze_xiangmao(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    gender: str = '',
    wood_type: Optional[Dict] = None,
) -> Dict:
    """相貌 marker 层（无判定无档位，供叙事层消费）。

    签名对齐 analyze_qianyi 惯例；wood_type 由 engine 透传
    result['wood_type']（活木判据），测试可手动喂入；缺省时活木线空转。

    Returns:
        {
          'xiuqi':  {'hit': bool, 'tou_gan': [...], 'desc': str},
          'jinshui': {'hit': bool, 'blocked_by': [...], 'desc': str},
          'muhuo':  {'hit': bool, 'fire': [...], 'desc': str},
          'yanxiang': {'bing': bool, 'ding': bool, 'gui': bool,
                       'eye_full': bool, 'desc': str},
          'meili':  {'hit': bool, 'jiyi_only': bool, 'desc': str},
          'shencai': {'hit': bool, 'markers': [...], 'desc': str},
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
        'xiuqi': {'hit': False, 'tou_gan': [], 'desc': ''},
        'jinshui': {'hit': False, 'blocked_by': [], 'desc': ''},
        'muhuo': {'hit': False, 'fire': [], 'desc': ''},
        'yanxiang': {'bing': False, 'ding': False, 'gui': False,
                     'eye_full': False, 'desc': ''},
        'meili': {'hit': False, 'jiyi_only': False, 'desc': ''},
        'shencai': {'hit': False, 'markers': [], 'desc': ''},
        'summary': '四柱不全，无法提取相貌 marker',
    }
    if not (len(gans) == 4 and len(zhis) == 4):
        return _empty

    others = [g for i, g in enumerate(gans) if i != 2 and g]  # 除日主外天干
    _ss = {g: _compute_shishen(day_gan, g) for g in others}   # 透干十神

    # ── 主线1 秀气透干（zhongji:3914-3915；反条件 lixiangxue:6655 不透则平）──
    tou = [g for g, s in _ss.items() if s in ('食神', '伤官')]
    xiuqi_hit = bool(tou)
    xiuqi_desc = ''
    if xiuqi_hit:
        # 性别分流措辞（zhongji:3914-3915 女命秀气主漂亮/男命主文章）
        fen_liu = ('秀气透干（' + '、'.join(tou) + '透），女看秀气漂亮倾向、'
                   '男看文章才华（zhongji:3914；chuji:1711）')
        if gender == '男':
            fen_liu = ('秀气透干（' + '、'.join(tou) + '透），秀气主文章才华'
                       '（zhongji:3914 性别分流）')
        xiuqi_desc = fen_liu

    # ── 主线2 金水伤官限辛（zhongji:1484/5455；shouke:5394 梦露造；
    #    反条件 shouke:474 金多不秀/土埋不秀；庚金不算 zhongji:5455）──
    blocked: List[str] = []
    if day_gan == '辛':
        if '癸' not in others:
            blocked.append('癸水未透')
        # ponytail: 「金多/土重」阈值简化——天干金（含日主）>2 或戊己≥2 即挡，
        # 书未给定量（shouke:474），升级路径=按旺衰量化
        if sum(1 for g in gans if GAN_WX.get(g) == '金') > 2:
            blocked.append('金多不秀（shouke:474）')
        if sum(1 for g in gans if g in ('戊', '己')) >= 2:
            blocked.append('土重埋金（shouke:474）')
    else:
        blocked.append('非辛日主（庚金不算，zhongji:5455）')
    jinshui_hit = day_gan == '辛' and not blocked
    jinshui_desc = ('辛日主癸水透，金水伤官秀气之象（zhongji:1484；'
                    'shouke:5394）' if jinshui_hit else '')

    # ── 主线3 活木见火（zhongji:4513；chuji:4371；lixiangxue:6628-6630）──
    wt = wood_type or {}
    is_huomu = bool(wt.get('is_wood')) and wt.get('wood_type') == '活木'
    fire = [g for g in others if g in ('丙', '丁')]  # 火透干（刘晓庆造丙透口径）
    muhuo_hit = is_huomu and bool(fire)
    muhuo_desc = (f'甲乙活木见{"、".join(fire)}火透，木火开花之象'
                  '（zhongji:4513；chuji:4371）' if muhuo_hit else '')

    # ── 主线4 眼象（zhongji:1482-1483；lixiangxue:11124-11126）──
    all_gz = list(gans) + list(zhis)
    bing = '丙' in all_gz
    ding = '丁' in all_gz
    gui = '癸' in all_gz
    eye_full = bing and gui  # 丙配癸=瞳孔（zhongji:1482；lixiangxue:11125）
    yan_desc_parts = []
    if bing:
        yan_desc_parts.append('丙=眼框/大眼之象')
    if ding:
        yan_desc_parts.append('丁=眼之象（zhongji:2122-2147；gaoji:15337；'
                              'lixiangxue:1777）')
    if eye_full:
        yan_desc_parts.append('丙癸配=瞳孔，眼象全（zhongji:1482-1483）')
    yanxiang = {
        'bing': bing, 'ding': ding, 'gui': gui, 'eye_full': eye_full,
        'desc': '；'.join(yan_desc_parts),
    }

    # ── 弱线1 伤官合官杀→魅力（gaoji:5618-5623；shouke:634-638 对照；
    #    条件「无官杀则仅技艺」shouke:638）──
    shangguan = [g for g, s in _ss.items() if s == '伤官']
    guansha = [g for g, s in _ss.items() if s in ('正官', '七杀')]
    he_pair = next(
        ((sg, gs) for sg in shangguan for gs in guansha
         if TIAN_GAN_HE.get(sg) == gs), None)
    meili_hit = he_pair is not None
    jiyi_only = bool(shangguan) and not guansha
    meili_desc = ''
    if meili_hit:
        meili_desc = (f'伤官{he_pair[0]}合{he_pair[1]}（官杀），伤官带魅力/'
                      f'性感意向（gaoji:5618-5623；shouke:638）[弱线]')
    elif jiyi_only:
        meili_desc = ('伤官透而无官杀，伤官仅主技艺（shouke:638 美容师对照'
                      '反条件）[弱线]')

    # ── 弱线2 身材曲线（zhongji:3981-3982 乙卯禄；zhongji:1484 己土）──
    sc_markers: List[str] = []
    if day_gan == '乙' and '卯' in zhis:
        sc_markers.append('乙木见卯禄，身材曲线之象（zhongji:3981）[弱线]')
    if '己' in others:
        sc_markers.append('己土透，身体曲线/表现力之象（zhongji:1484）[弱线]')
    shencai = {
        'hit': bool(sc_markers), 'markers': sc_markers,
        'desc': '；'.join(sc_markers),
    }

    # ── summary：只列命中机制名+锚，不出结论词 ──
    parts: List[str] = []
    if xiuqi_hit:
        parts.append('秀气透干')
    if jinshui_hit:
        parts.append('金水伤官')
    if muhuo_hit:
        parts.append('活木见火')
    if eye_full:
        parts.append('眼象全')
    if meili_hit:
        parts.append('伤官合官杀魅力')
    if shencai['hit']:
        parts.append('身材曲线')
    summary = ('相貌 marker：' + ('、'.join(parts) if parts
                                else '未命中既有相貌 marker 线')
               + '（marker 层无判定无档位，供叙事层消费）')

    return {
        'xiuqi': {'hit': xiuqi_hit, 'tou_gan': tou, 'desc': xiuqi_desc},
        'jinshui': {'hit': jinshui_hit, 'blocked_by': blocked,
                    'desc': jinshui_desc},
        'muhuo': {'hit': muhuo_hit, 'fire': fire, 'desc': muhuo_desc},
        'yanxiang': yanxiang,
        'meili': {'hit': meili_hit, 'jiyi_only': jiyi_only,
                  'desc': meili_desc},
        'shencai': shencai,
        'summary': summary,
    }


__all__ = ['analyze_xiangmao']
