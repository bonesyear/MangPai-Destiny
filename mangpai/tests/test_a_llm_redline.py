"""修批A 哨兵（先红后绿）· LLM 红线三项（R5 block×3）

- A① siwang 死亡词典 scrub：zaihuo 键外泄漏（shipaige 寿元断语/liuqin 早夭/
  xiangfa_ops lianti 寿命 warning/guanming 制死/liunian 冲破主死亡）经
  payload 装配层统一 scrub；引擎内部 siwang 保留（F14 设计不变）。
- A② zeishen 单源化：huanxiang 改消费引擎已算 zeishen_bushen（缺省 fallback
  以 zuogong_confirm 标记后 work_actions 自算），caiming._zeishen_jingzhi
  补传 zg——11/509 矛盾例（payload 换象断语 locked 与 zeishen_bushen.jing_zhi
  同帧矛盾）口径统一。
- A③ gongmen_wuzhi 从 selectors 摘除（is_wuzhi 98.8% 恒真零信息量，
  F18 已切断 narrative 通道，本步落 payload 通道），selectors 39→38，
  engine result 键保留。
"""
import json

from mangpai import MangpaiEngine
from mangpai.subjective import (
    MANGPAI_SCHOOL, _DEATH_TERMS, _scrub_death, build_payload,
)
from mangpai.subjective.caiming import _zeishen_jingzhi
from mangpai.subjective.xiangfa_ops import analyze_xiangfa_ops


def _run(gz: str) -> dict:
    """gz=8字干支串（年月日時），跑引擎全量（blind_eval 同款 bazi_data 构造）。"""
    from mangpai.objective.bazi_calc import get_kong_wang
    eng = MangpaiEngine({
        'bazi': {'year': gz[:2], 'month': gz[2:4], 'day': gz[4:6], 'hour': gz[6:]},
        'kong_wang': get_kong_wang(gz[4], gz[5]),
        'input': {'gender': '男'},
    })
    return eng.compute_all()


def _split(gz: str):
    gans = [gz[i] for i in (0, 2, 4, 6)]
    zhis = [gz[i] for i in (1, 3, 5, 7)]
    return gans, zhis


# ── A① siwang 死亡词典 scrub ──

class TestDeathScrub:
    def test_scrub_unit_leak_strings(self):
        """四处 R5 实测泄漏串 + liunian 死亡 desc，scrub 后零命中。"""
        payload = _scrub_death({
            'shipaige': {'triggered': {'寿元': ['食伤被制短命'], '事业': ['身旺']},
                         'todos': ['父母：比劫旺相印空亡父死母再嫁（空亡未接入）']},
            'liuqin': {'markers': ['比劫坐未墓逢冲（手足早夭）', '月透七杀（兄弟有损）']},
            'xiangfa_ops': {'xiangfa_fallback': {'lianti': {
                'warning': '庚辰连根之体被制，制之防伤身体及寿命'}}},
            'guanming': {'veto': ['官被制空制死，不立官命（李昌镐例）', '反局']},
            'liunian_analysis': {'desc': '冲破（所冲极衰无救，冲破主终结/死亡，大凶）'},
        })
        blob = json.dumps(payload, ensure_ascii=False)
        for t in _DEATH_TERMS:
            assert t not in blob, f'scrub 后仍命中 {t}'
        # 非死亡内容保留
        assert payload['shipaige']['triggered']['事业'] == ['身旺']
        assert payload['liuqin']['markers'] == ['月透七杀（兄弟有损）']
        assert payload['guanming']['veto'] == ['反局']

    def test_death_charts_payload_zero_hit(self):
        """R5 两死亡盘实跑：payload 死亡词典零命中。"""
        for gz in ('甲申辛未壬子壬寅', '癸寅庚申己未丁丑'):
            blob = json.dumps(build_payload(_run(gz)), ensure_ascii=False)
            for t in _DEATH_TERMS:
                assert t not in blob, f'{gz} payload 命中 {t}'

    def test_engine_internal_siwang_kept(self):
        """红线只动 LLM 视图层：引擎内部 zaihuo.siwang 保留（F14 设计不变）。"""
        res = _run('甲申辛未壬子壬寅')
        assert 'siwang' in (res.get('zaihuo') or {})


# ── A② zeishen 单源化 ──

class TestZeishenSingleSource:
    def test_contra_case_no_huanxiang(self):
        """zhenbao-09（R5 矛盾样例）：引擎判不净 → 换象不再触发（口径统一）。"""
        res = _run('壬子癸卯壬子丙午')
        zb = (res['zeishen_bushen'] or {}).get('zeishen_bushen') or {}
        assert zb.get('jing_zhi') == '不净'
        assert res['xiangfa_ops']['huanxiang'] == []

    def test_fallback_consistent_without_zb_result(self):
        """缺省 fallback（不传 zeishen_result，zhiye 内部调用路径）同口径。"""
        gans, zhis = _split('壬子癸卯壬子丙午')
        xo = analyze_xiangfa_ops(gans[2], gans, zhis)
        assert xo['huanxiang'] == []

    def test_jing_anchor_still_huanxiang(self):
        """正向锚 李嘉诚（净制巨富）：净 → 换象保留，caiming 净制豁免成立。"""
        res = _run('戊辰己未庚午丁亥')
        zb = (res['zeishen_bushen'] or {}).get('zeishen_bushen') or {}
        assert zb.get('jing_zhi') == '净'
        assert len(res['xiangfa_ops']['huanxiang']) >= 1
        gans, zhis = _split('戊辰己未庚午丁亥')
        assert _zeishen_jingzhi(gans[2], gans, zhis) is True

    def test_caiming_jingzhi_matches_engine(self):
        """caiming._zeishen_jingzhi 与引擎 zb_res 同口径（补传 zg）。"""
        for gz in ('壬子癸卯壬子丙午', '戊辰己未庚午丁亥', '甲申丁卯甲申甲子'):
            res = _run(gz)
            zb = (res['zeishen_bushen'] or {}).get('zeishen_bushen') or {}
            engine_jz = (zb.get('jing_zhi') == '净'
                         and float(zb.get('bushen_strength') or 0)
                         >= float(zb.get('zeishen_strength') or 0))
            gans, zhis = _split(gz)
            assert _zeishen_jingzhi(gans[2], gans, zhis) == engine_jz


# ── A③ gongmen 从 selectors 摘除 ──

class TestGongmenRemoved:
    def test_selectors_40_no_gongmen(self):
        assert 'gongmen_wuzhi' not in MANGPAI_SCHOOL.selectors
        # D6b：zinv 追加（镜像 liuqin 通道），38→39
        # 缺口批1：qianyi 追加（迁移 marker+应期窗，同口径），39→40
        # 缺口批2：xiangmao 追加（相貌 marker 层，同口径），40→41
        assert len(MANGPAI_SCHOOL.selectors) == 41

    def test_payload_no_gongmen_result_key_kept(self):
        """payload 不含 gongmen_wuzhi；engine result 键保留（内部存档）。"""
        res = _run('甲申辛未壬子壬寅')
        assert 'gongmen_wuzhi' not in build_payload(res)
        assert 'gongmen_wuzhi' in res
