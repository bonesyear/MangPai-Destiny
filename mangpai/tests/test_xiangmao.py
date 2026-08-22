# -*- coding: utf-8 -*-
"""缺口批2 哨兵：xiangmao 相貌 marker 层（无判定无档位）。

书锚（设计 = 缺口方案归档 kimi-gaps-plan-2026-08-20 §二，行号已回书核对）：
- 金水伤官限辛：梦露造 坤 丙寅癸巳辛酉癸巳（shouke:5394「辛日主见癸长得
  漂亮」；zhongji:1484-1485「辛金配癸水组合：金水伤官漂亮」；反条件
  shouke:474 金多不秀/土埋不秀；庚金不算 zhongji:5455）。
- 秀气透干：zhongji:3914-3915（女命秀气主漂亮/男命主文章）；反例
  lixiangxue:6655 坤 癸亥癸亥壬寅癸卯「秀气并未透干，相貌平平」。
- 活木见火：刘晓庆造 坤 乙未丙戌甲子乙亥（chuji:4371「甲见火为开花，
  首先此人长得漂亮」；zhongji:4513 黛安娜造；lixiangxue:6628-6630）。
- 眼象：zhongji:1482-1483（丙=眼框、癸=瞳、丙配癸=瞳孔）；
  lixiangxue:11124-11126（「火土焦干癸水，双目无瞳」须见丙/巳）。
- 伤官合官杀：阮玲玉 坤 庚戌辛巳己亥乙亥 vs 美容师 坤 庚戌辛巳己亥己巳
  （gaoji:5618-5623 + shouke:634-638 对照「无官杀则伤食仅表技艺」——
  一造正一反天然哨兵）。
- 身材曲线弱线：zhongji:3981（乙卯禄）、zhongji:1484（己土）。

红线：输出任何 desc/note/summary 不得含「美/丑/帅」结论词（无判定无档位
设计——归档 §二.3）；书引短语仅作 basis 锚注。收档不立：贵相口诀/难看
反推/五行形体表/配偶相貌/身高定量。
"""
import json

from mangpai.subjective.xiangmao import analyze_xiangmao
from mangpai.objective.wood_type import analyze_wood_type


def _split8(bazi):
    gans = [bazi[i] for i in (0, 2, 4, 6)]
    zhis = [bazi[i] for i in (1, 3, 5, 7)]
    return gans, zhis


def _run(bazi, gender='女', wt=None):
    gans, zhis = _split8(bazi)
    return analyze_xiangmao(gans[2], gans, zhis, gender=gender, wood_type=wt)


# ── 1. 对照造·梦露（shouke:5394）：金水伤官限辛 + 秀气透干 + 眼象 ──

def test_menglu_jinshui_xiuqi_yanxiang():
    """坤 丙寅癸巳辛酉癸巳：辛日主+癸透 → 金水伤官；癸食透 → 秀气透干；
    丙癸同见 → 眼象全（zhongji:1482-1483）。"""
    r = _run('丙寅癸巳辛酉癸巳')
    assert r['jinshui']['hit'] is True and not r['jinshui']['blocked_by']
    assert r['xiuqi']['hit'] is True and '癸' in r['xiuqi']['tou_gan']
    assert r['yanxiang']['eye_full'] is True


# ── 2. 对照造·刘晓庆（chuji:4371）：活木见火 ──

def test_liuxiaoqing_huomu_jianhuo():
    """坤 乙未丙戌甲子乙亥：甲=活木（wood_type 真实计算）+ 丙火透 → 活木见火。"""
    wt = analyze_wood_type('甲', '未', '戌', '子', '亥')
    assert wt['is_wood'] and wt['wood_type'] == '活木'
    r = _run('乙未丙戌甲子乙亥', wt=wt)
    assert r['muhuo']['hit'] is True and '丙' in r['muhuo']['fire']
    # 死木反条件：同造改判死木则不出 marker（lixiangxue:6628 活木为前提）
    r2 = _run('乙未丙戌甲子乙亥',
              wt={'is_wood': True, 'wood_type': '死木'})
    assert r2['muhuo']['hit'] is False


# ── 3. 对照造·阮玲玉 vs 美容师（gaoji:5618-5623 + shouke:634-638）──

def test_ruanlingyu_shangguan_he_guansha():
    """坤 庚戌辛巳己亥乙亥：伤官庚合七杀乙 → 魅力 marker（shouke:638 正造）。"""
    r = _run('庚戌辛巳己亥乙亥')
    assert r['meili']['hit'] is True
    assert '伤官庚合乙' in r['meili']['desc']
    assert r['meili']['jiyi_only'] is False


def test_meirongshi_guard_jiyi_only():
    """坤 庚戌辛巳己亥己巳：伤官庚透而无官杀 → 仅技艺 marker，不出魅力
    （shouke:638 美容师反例=天然反例 guard）。"""
    r = _run('庚戌辛巳己亥己巳')
    assert r['meili']['hit'] is False
    assert r['meili']['jiyi_only'] is True


# ── 4. 反例 guard：秀气不透干则平（lixiangxue:6655）──

def test_guard_xiuqi_not_tou_lixiangxue6655():
    """坤 癸亥癸亥壬寅癸卯：满盘比劫、伤食藏支不透 → 零秀气 marker，
    各主线全空（书「秀气并未透干，相貌平平」）。"""
    r = _run('癸亥癸亥壬寅癸卯')
    assert r['xiuqi']['hit'] is False
    assert r['jinshui']['hit'] is False
    assert r['muhuo']['hit'] is False
    assert r['meili']['hit'] is False


# ── 5. schema + 红线措辞（无判定无档位，不出「美/丑/帅」结论词）──

def test_schema_and_wording_redline():
    for bazi in ('丙寅癸巳辛酉癸巳', '乙未丙戌甲子乙亥', '庚戌辛巳己亥乙亥'):
        r = _run(bazi)
        assert set(r) >= {'xiuqi', 'jinshui', 'muhuo', 'yanxiang',
                          'meili', 'shencai', 'summary'}
        blob = json.dumps(r, ensure_ascii=False)
        for term in ('美', '丑', '帅'):
            assert term not in blob


# ── 6. engine 接线 + 特征 JSON 通道（镜像 qianyi 缺口批1 口径）──

def test_engine_wiring_and_payload_channel():
    """compute_all 产出 result['xiangmao']；build_payload 经 selectors 进特征 JSON。"""
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    bazi_data = {
        'bazi': {'year': '丙寅', 'month': '癸巳', 'day': '辛酉', 'hour': '癸巳'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': '女', 'year': 1926},
        'da_yun': {'start_age': 3, 'dayun': [
            {'gz': '壬辰', 'start_age': 3, 'end_age': 13},
        ]},
        'liunian': [{'gz': '丙戌', 'year': 1946}],
    }
    res = MangpaiEngine(bazi_data).compute_all()
    assert 'xiangmao' in res
    assert res['xiangmao']['jinshui']['hit'] is True
    payload = build_payload(res)
    assert 'xiangmao' in payload
    assert payload['xiangmao']['jinshui']['hit'] is True


# ── 7. G3 措辞哨兵：秀气线去「漂亮」（F-N2-1）+ 大眼锚注（#15）──

def test_g3_xiuqi_desc_no_piaoliang():
    """梦露造 坤 丙寅癸巳辛酉癸巳：秀气线 desc 收敛为「女看秀气倾向」
    （书原文 zhongji:3914-3915「女命秀气主漂亮」，措辞红线不进结论词）。"""
    r = _run('丙寅癸巳辛酉癸巳')
    assert r['xiuqi']['hit'] is True
    assert '女看秀气倾向' in r['xiuqi']['desc']
    assert '漂亮' not in r['xiuqi']['desc']


def test_g3_yanxiang_dayan_anchor():
    """眼象线「丙=眼框/大眼之象」补 inline 书锚：zhongji:4531「丙主眼睛大」
    明锚 + zhongji:1483 眼框 + lixiangxue:12632 黛安娜大眼睛旁证。"""
    r = _run('丙寅癸巳辛酉癸巳')
    assert r['yanxiang']['bing'] is True
    assert '大眼' in r['yanxiang']['desc']
    assert 'zhongji:1483/4531' in r['yanxiang']['desc']
