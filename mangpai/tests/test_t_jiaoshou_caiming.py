# -*- coding: utf-8 -*-
"""test_t_jiaoshou_caiming — T-教授财命窄条款微批哨兵（日支穿月令财 → 封顶小康）

书锚（逐字回书已核，预注册=docs/kimi-t-jiaoshou-caiming-prereg-20260918.md）：
- 锚① cj-教授（甲辰/丙子/己未/戊辰）：chuji:2379-2384「为月令的财被坐支穿…此造
  是制财结构，财还是可以的，教授，收入还可以」+chuji:3678-3681「穿了月令财主日主
  与财星无缘…甲己合官，坐下财库，有地位」+chuji:5995「挣工资的，也不是发大财的」。
- 锚② zj-邢铭芬（乙未/乙酉/丙戌/庚寅）：zhongji:2322-2323「动了，但穿了财，故发不
  了大财，只能发点小财。如是丁酉日主见了戌则是得财之命」。

口径：月令取本气（ZHI_WX）——藏干口径会误中马云（戌中气辛金=丁财），书自反例
「丁酉日主见了戌则是得财之命」（zhongji:2323）即丁酉+戌月令结构，支持本气口径排除。
仅 tier_idx>2 时 cap 生效追加文本，tier_idx≤2 完全 no-op（零文本抖动）。
修法纪律：全走 caiming 消费侧（assess_caiming_level 内一处），objective 零改动。
"""
from mangpai.subjective.caiming import analyze_caiming


def _split(gz4):
    return [g[0] for g in gz4], [g[1] for g in gz4]


def _level_static(gz4):
    gans, zhis = _split(gz4)
    r = analyze_caiming(gans[2], gans, zhis)
    return r['level_static']['tier'], r['level_static']['adjust']


# 三锚例（真阳：该限）
JIAOSHOU = ('甲辰', '丙子', '己未', '戊辰')      # cj-教授：未穿子（月令本气水=己财）
XINGMINGFEN = ('乙未', '乙酉', '丙戌', '庚寅')    # zj-邢铭芬：戌穿酉（月令本气金=丙财）
PINQIONG = ('癸丑', '癸亥', '戊申', '辛酉')       # yx-贫穷命贫困线上：申穿亥（亥本气水=戊财）
# 假阳锚（不该限）：马云=丁酉日+戌月令，戌本气土≠丁财金（书自反例 zhongji:2323）
MAYUN = ('甲辰', '甲戌', '丁酉', '戊申')
LIJIACHENG = ('戊辰', '己未', '庚午', '丁亥')     # 午未不穿
BAOERSEN = ('丙申', '壬辰', '戊辰', '壬戌')       # 辰戌冲非穿
AONAXIS = ('乙巳', '己丑', '己未', '庚午')        # 丑未冲非穿
MEIKUANG = ('丁巳', '癸丑', '丙戌', '甲午')       # 丑戌刑非穿
# no-op guard：谓词命中（未穿子、子本气水=己财）但档本在 cap 下（凶向链压小康）
NOOP = ('甲子', '丙子', '己未', '甲子')


# ─────────── 真阳锚：日支穿月令财 → 封顶小康 ───────────

def test_jiaoshou_capped_xiaokang():
    """cj-教授：日支未穿月令子财 → 巨富封顶小康（书「财还是可以的…收入还可以」）。"""
    tier, adjust = _level_static(JIAOSHOU)
    assert tier == '小康'
    assert '穿了月令财' in adjust


def test_xingmingfen_capped_xiaokang():
    """zj-邢铭芬：日支戌穿月令酉财 → 富封顶小康（书「穿了财…只能发点小财」）。"""
    tier, adjust = _level_static(XINGMINGFEN)
    assert tier == '小康'
    assert '穿了月令财' in adjust


def test_pinqiong_capped_xiaokang():
    """yx-贫穷命贫困线上：日支申穿月令亥财 → 富封顶小康（❌→⚠️ 改善非✅）。"""
    tier, adjust = _level_static(PINQIONG)
    assert tier == '小康'
    assert '穿了月令财' in adjust


# ─────────── 假阳锚：谓词结构性不命中，档位逐字不动 ───────────

def test_mayun_benqi_not_hit():
    """马云：酉穿戌但戌本气土≠丁财金（藏干辛金不取）→ 谓词 False，tier 富不动，
    adjust 无穿财文本（famous 零回归红线）。"""
    tier, adjust = _level_static(MAYUN)
    assert tier == '富'
    assert '穿了月令财' not in adjust


def test_fu_anchors_not_hit():
    """富命锚：李嘉诚/保尔森/奥纳西斯/煤矿 谓词全 False（冲/刑非穿），巨富不动。"""
    assert _level_static(LIJIACHENG)[0] == '巨富'
    for gz4 in (BAOERSEN, AONAXIS, MEIKUANG):
        tier, adjust = _level_static(gz4)
        assert '穿了月令财' not in adjust
    assert _level_static(AONAXIS)[0] == '巨富'
    assert _level_static(MEIKUANG)[0] == '巨富'


def test_noop_when_tier_below_cap():
    """no-op guard：谓词命中但 tier_idx≤2（凶向链已压小康）→ 完全不追加文本。"""
    tier, adjust = _level_static(NOOP)
    assert tier == '小康'
    assert '穿了月令财' not in adjust
