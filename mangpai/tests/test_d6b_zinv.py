# -*- coding: utf-8 -*-
"""D6b 哨兵：zinv 子息岁运应期（得子/损子）+ 借腹 marker + liuqin 时柱喜用腿。

书锚（设计 docs/kimi-d6a-zinv-design-20260819.md §3.5）：
- F1 得子-制枭：坤 己酉丙子丁卯乙巳（gaoji:14087-14107 案例三）——
  己卯运（卯偏印旺夺食）不在得子窗；庚辰运乙庚合制住枭神，方得子。
- F2 得子-合动/开墓 + 合神被克：乾 戊戌己未乙巳丁亥（授课:18-20，一造三机制）——
  壬戌运丁壬合（合动）、丁卯年（子息星到位合运干）、戊辰年辰冲戌开墓（得子）；
  戊辰年戊土克壬合神被克（损子/流产）。
- F4 损子-克到位+合去：乾 癸卯癸亥丁巳丙午（gaoji:14108-14128 案例四）——
  己未运己土克癸水（克到位）、戊寅年戊合癸（合去）。
- H2/H3 借腹：乾 乙巳庚辰辛卯壬辰（gaoji:14317-14334 案例十二）与
  乾 己巳庚辰辛卯壬辰（zhongji:1911-1914/4165-4170）——日支受穿+子息星入时墓。
- 反例 guard：乾 壬辰癸卯丙辰戊子（gaoji:14236-14252 案例八，子女优）不得入损子窗。

红线：损子 desc 字面不得含「死/夭/丧」（LLM 侧另有 _scrub_death 兜底）。
岁运序列手动喂入（yingqi/liuqin 测试惯例），不改引擎岁运逻辑。
"""
import json

from mangpai.subjective.zinv import analyze_zinv
from mangpai.subjective.liuqin import detect_zixi_youlie


def _split8(bazi):
    gans = [bazi[i] for i in (0, 2, 4, 6)]
    zhis = [bazi[i] for i in (1, 3, 5, 7)]
    return gans, zhis


def _run(bazi, gender, dys=(), lns=()):
    gans, zhis = _split8(bazi)
    return analyze_zinv(
        gans[2], gans, zhis, gender,
        dayun_list=[{'gz': d} for d in dys],
        liunian_list=[{'gz': l} for l in lns],
    )


def _dezi_dys(r):
    return {w['dayun'] for w in r['zixi_yingqi_dezi']['windows']}


def _dezi_lns(r):
    return {w['liunian'] for w in r['zixi_yingqi_dezi']['windows']}


def _sunzi(r):
    return r['zixi_yingqi_sunzi']['windows']


# ── 1. 得子-制枭（F1 gaoji:14087-14107）──

def test_dezi_zhixiao_an3():
    """坤 己酉丙子丁卯乙巳：己卯运不生（枭夺食运）、庚辰运乙庚合制枭得子。"""
    r = _run('己酉丙子丁卯乙巳', '女', dys=['己卯', '庚辰'])
    dezi = r['zixi_yingqi_dezi']['windows']
    assert '己卯' not in _dezi_dys(r)
    geng = [w for w in dezi if w['dayun'] == '庚辰']
    assert geng and any(w['mechanism'] == '制枭' for w in geng)
    # 己卯运（卯偏印旺夺食）应在损子窗（书：「己卯运不生孩子」）
    assert any(w['dayun'] == '己卯' and w['mechanism'] == '枭夺食运'
               for w in _sunzi(r))


# ── 2. 得子-合动/开墓 + 损子-合神被克（F2 授课:18-20）──

def test_dezi_hedong_kaimu_shouke18():
    """乾 戊戌己未乙巳丁亥 壬戌运：丁壬合合动；丁卯年子息星到位；戊辰年开墓。"""
    r = _run('戊戌己未乙巳丁亥', '男', dys=['壬戌'], lns=['丁卯', '戊辰'])
    dezi = r['zixi_yingqi_dezi']['windows']
    assert any(w['dayun'] == '壬戌' and w['mechanism'] == '合动' for w in dezi)
    assert any(w['liunian'] == '丁卯' and w['mechanism'] == '合动' for w in dezi)
    assert any(w['liunian'] == '戊辰' and w['mechanism'] == '开墓' for w in dezi)


def test_sunzi_heshen_beike_shouke18():
    """同造：戊辰年戊土克壬（合神被克，壬不能合丁）→ 损子窗。"""
    r = _run('戊戌己未乙巳丁亥', '男', dys=['壬戌'], lns=['丁卯', '戊辰'])
    assert any(w['liunian'] == '戊辰' and w['mechanism'] == '合神被克'
               for w in _sunzi(r))
    # 壬戌运本身（合子息星）不得误判为克到位
    assert not any(w['dayun'] == '壬戌' and w['mechanism'] == '克到位'
                   for w in _sunzi(r))


# ── 3. 损子-克到位+合去（F4 gaoji:14108-14128）──

def test_sunzi_kedaowei_hequ_an4():
    """乾 癸卯癸亥丁巳丙午：己未运己土克癸水（克到位），戊寅年戊合癸（合去）。"""
    r = _run('癸卯癸亥丁巳丙午', '男', dys=['己未'], lns=['戊寅'])
    sunzi = _sunzi(r)
    assert any(w['dayun'] == '己未' and w['mechanism'] == '克到位' for w in sunzi)
    assert any(w['liunian'] == '戊寅' and w['mechanism'] == '合去' for w in sunzi)


# ── 4. 借腹（H2 gaoji:14317-14334 + H3 zhongji:1911-1914/4165-4170）──

def test_jiefu_an12_gaoji():
    """乾 乙巳庚辰辛卯壬辰：卯辰穿倒妻宫+乙财入时上辰墓 → is_jiefu。"""
    r = _run('乙巳庚辰辛卯壬辰', '男')
    assert r['jiefu']['is_jiefu'] is True
    assert r['jiefu']['basis']


def test_jiefu_zhongji1911():
    """乾 己巳庚辰辛卯壬辰：同构（穿倒妻宫财星，乙财在时上辰墓）→ is_jiefu。"""
    r = _run('己巳庚辰辛卯壬辰', '男')
    assert r['jiefu']['is_jiefu'] is True


# ── 5. 反例 guard（案例八 子女优，防穿/克误伤）──

def test_guard_an8_no_sunzi_no_jiefu():
    """乾 壬辰癸卯丙辰戊子（子女优，gaoji:14236-14252）：平和岁运不得入损子窗。"""
    r = _run('壬辰癸卯丙辰戊子', '男', dys=['丙午'], lns=['庚寅'])
    assert _sunzi(r) == []
    assert r['jiefu']['is_jiefu'] is False


# ── 6. schema + 红线措辞 ──

def test_zinv_schema_and_no_death_terms():
    r = _run('癸卯癸亥丁巳丙午', '男', dys=['己未'], lns=['戊寅'])
    assert set(r) >= {'zixi_yingqi_dezi', 'zixi_yingqi_sunzi', 'jiefu', 'summary'}
    blob = json.dumps(r, ensure_ascii=False)
    for term in ('死', '夭', '丧'):
        assert term not in blob


def test_zinv_summary_only_yingqi_jiefu():
    """summary 只述应期与借腹，不复拼 liuqin 子息段。"""
    r = _run('乙巳庚辰辛卯壬辰', '男')
    assert '借腹' in r['summary'] or '养子' in r['summary']


# ── engine 接线 + 特征 JSON 通道（build_payload selectors 镜像 liuqin）──

def test_engine_wiring_and_payload_channel():
    """compute_all 产出 result['zinv']；build_payload 经 selectors 进特征 JSON。"""
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    bazi_data = {
        'bazi': {'year': '乙巳', 'month': '庚辰', 'day': '辛卯', 'hour': '壬辰'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': '男', 'year': 1965},
        'da_yun': {'start_age': 3, 'dayun': [
            {'gz': '己卯', 'start_age': 3, 'end_age': 13},
            {'gz': '戊寅', 'start_age': 13, 'end_age': 23},
        ]},
        'liunian': [{'gz': '庚辰', 'year': 2000}],
    }
    res = MangpaiEngine(bazi_data).compute_all()
    assert 'zinv' in res
    assert res['zinv']['jiefu']['is_jiefu'] is True
    payload = build_payload(res)
    assert 'zinv' in payload
    assert payload['zinv']['jiefu']['is_jiefu'] is True


# ── 7. liuqin 增补腿（R4：时柱为喜用→优/为忌→劣，
#       D1 gaoji:14226-14240 + D2 gaoji:5972-5973/6341-6342 + D3 理象学研究版:4283-4285）──

def test_youlie_hour_xiyong_leg_an8():
    """案例八（壬辰癸卯丙辰戊子 女）从弱、时柱戊子=食伤+官杀皆喜用 → 优腿在列。"""
    r = detect_zixi_youlie('丙', list('壬癸丙戊'), list('辰卯辰子'), gender='女')
    assert any('时柱为喜用' in y for y in r['you'])
    assert r['verdict'] == '优'


def test_youlie_hour_jishen_leg():
    """身强盘时柱为印比（忌神）→ 劣腿（D2「若为忌神，则子女不肖」）。"""
    # 甲日身强（天干四甲+丑土培根）：时柱甲子=比肩+正印皆忌神
    r = detect_zixi_youlie('甲', list('甲甲甲甲'), list('丑丑丑子'), gender='男')
    assert any('时柱为忌神' in l for l in r['lie'])
