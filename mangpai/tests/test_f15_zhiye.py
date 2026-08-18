# -*- coding: utf-8 -*-
"""F15 zhiye 批哨兵测试（先红后绿）。

最终落地（试案-回退纪律见 CHANGELOG F15）：
1. 军警 8.2 明文组合（批7 P0-3：书明列组合全未实现，军警书例 4 中 1；批8：
   gongmen_wuzhi 有实现但 11 条 P0 偏差+is_wuzhi 近恒真，F1 已弃用——决策
   =zhiye 本模块按书重写窄条款，不接该模块）：
   ①戌武库做功+3（gaoji:11620）②火金相战+2（:11648）③金水见火+2（:11654）
   ⑤申酉丑寅交织+2（:11658，≥3字）⑦丑戌刑/阳制阴+2（:11785-11788，书口径
   含天干、子归阴；制类须阳为制方）⑧戌武库刑冲开官杀库+2（口诀二+案例四
   :11745）；贵气门（:11956「先观格局有无贵气」（修批C 更正行号，旧记 :11964，R3）=官杀主气≥2 柱且透干——
   羊刃/官杀库腿经书例检验误伤面大已撤）+组合封顶 +6。④比劫库/羊刃库制印
   不落地（政委例十 未穿子=军权 vs 复例四 辰穿卯=经商，双锚同构不可分，
   铁律16）。
2. 内食神格补书限定「地支食神做功，或食神生财」（批7 P0-4，gaoji:11020/
   7.2 案一 巳火食神被制）——做功=制/合/冲等 HE/ZHI 动作当事人（被日主
   泄秀之生用不算），旧版存在即 +2。
3. 撤回备案（红线优先，勿重试）：
   - merchant 收窄（食伤生财主气化/冲财合财去重）：误伤 heldout merchant
     既有✅ ans33/li131/li133（旧「双计/柱级」口径恰是其过阈来源）；
   - lawyer ⑥伤官合杀/食神制杀：与「伤官制官」同动作复计，误伤 li154
     摇滚歌星/董竹君门户锚；
   - C4 富屋贫人扩展 gating（宾馆服务员 zhongji:3478）：与 7.2 案例一
     董事长同构不可分（铁律16 双锚）——C4 根因定在上游 caiming 财统官(b)
     腿不验身弱（caiming.py:779-785）+gongliang 同判 L3，留 caiming 批。
4. 书例回归：8.2 军官例二、纪检例九归位 military（1/10→3/10）；军官例四
   被贵气门所挡、法院例七 performer tie、例八落 military=公检法/武职桶界
   张力（书 8.2 同章兼收），均备案。7.3 命中持平 2/12（fn 侧 teacher/
   accountant 通道缺口留后续批）。

保护锚：罗斯切尔德/乔布斯 merchant 不得回退；岳飞 performer=1（F13）。
"""
from mangpai.subjective.zhiye import classify_zhiye


def _run(dg, gans, zhis):
    return classify_zhiye(dg, list(gans), list(zhis))


# ── 7.3 职业章书例（保持命中，收窄勿伤）──

def test_lvshi_li8_lawyer():
    """律师例八（辛酉辛卯己丑丙子，gaoji:10939 食神库制官+卯酉冲）。"""
    assert _run('己', '辛辛己丙', '酉卯丑子')['primary'] == 'lawyer'


def test_shangren_li12_merchant():
    """商人例十二（甲辰丙寅乙酉戊寅，gaoji:11040 开家具厂（修批C 更正行号，旧记 :11053，R3））——merchant 收窄
    后仍命中（财入局=日主克财干、食伤生财=丙戊主气明现+生用动作）。"""
    assert _run('乙', '甲丙乙戊', '辰寅酉寅')['primary'] == 'merchant'


# ── 8.2 军警书例（先红后绿）──

def test_junguan_li1_military():
    """军官例一（己卯辛未戊辰甲寅，gaoji:11690 杀入羊刃墓）：保持 military。"""
    assert _run('戊', '己辛戊甲', '卯未辰寅')['primary'] == 'military'


def test_junguan_li2_military():
    """军官例二（丁未辛亥己卯甲戌，gaoji:11708 三合杀局+戌火库）：戌武库做功
    等组合归位 military（先红：military 仅 5，未分类）。"""
    r = _run('己', '丁辛己甲', '未亥卯戌')
    assert r['primary'] == 'military'
    assert any('戌武库' in ln for ln in r['evidence']['military'])


def test_junguan_li4_blocked_by_guiqi_gate():
    """军官例四（辛巳戊戌己未辛未，gaoji:11745 戌未刑开杀库）：局无官杀主气
    亦无羊刃，贵气门挡 8.2 组合（gaoji:11956「先观格局有无贵气」）——戌武库
    类组合不计（守住复例四 merchant 锚之互换代价，备案）。"""
    r = _run('己', '辛戊己辛', '巳戌未未')
    assert not any('8.2' in ln or '戌武库' in ln for ln in r['evidence'].get('military', []))


def test_jijian_li9_military():
    """纪检例九（丁未己酉癸巳丁巳，gaoji:11893 火土制金阳制阴）：归位
    military（先红：merchant 10 吸走）。"""
    r = _run('癸', '丁己癸丁', '未酉巳巳')
    assert r['primary'] == 'military'
    assert any('阳制阴' in ln or '火金相战' in ln for ln in r['evidence']['military'])


def test_guiqi_gate_blocks_no_guan_chart():
    """贵气门（gaoji:11956）：局无官杀主气/羊刃/官杀库者，8.2 字级组合不计
    （防火金相战/阳制阴逢盘泛触）。构造：乙卯日木火局，午克酉火金动作在
    而官杀/刃/官杀库俱无 → military 无 8.2 组合证据。"""
    r = _run('乙', '丙甲乙丁', '午卯巳酉')
    assert not any('8.2' in ln for ln in r['evidence'].get('military', []))


# ── 保护锚 ──

def test_rothschild_merchant_kept():
    """罗斯切尔德（甲子丙寅己丑辛未）：famous 锚 merchant 不得回退（丑未刑冲
    官杀库/丑寅暗合曾误触 8.2 组合，⑤≥3字+⑧限戌 收窄后恢复）。"""
    assert _run('己', '甲丙己辛', '子寅丑未')['primary'] == 'merchant'


def test_jobs_merchant_kept():
    """乔布斯（乙未戊寅丙辰庚寅）：famous 锚 merchant 不得回退。"""
    assert _run('丙', '乙戊丙庚', '未寅辰寅')['primary'] == 'merchant'


def test_yuefei_performer_stays_low():
    """岳飞（癸未乙卯甲子己巳）：F13 哨兵保持——performer 仍 1 分。"""
    assert _run('甲', '癸乙甲己', '未卯子巳')['scores'].get('performer', 0) == 1
