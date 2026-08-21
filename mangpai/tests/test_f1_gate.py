"""修批 F1+F3 发布闸哨兵（先红后绿）· P0 免责声明 + P1 五项 + F3 健壮性五项

- 免责声明（V4 P0-1）：引擎直出（formatter）/LLM 叙述（format_reading）/HELP 三处必带
- lark_md 三符（V2 P1-2）：formatter/service 输出零 '- '/'>'/'---' 字面残留
- 死亡词 mark→reject（V4 P1-1）：validate=mark 命中死亡红线词即整段拒出
  （'[断语被' 前缀触发 service 降级引擎直出），附注也不展示；
  合规拒答句（复述死亡词+拒答标记，V4 P2-2/2-3）经误报窗豁免不误拦
- bot isinstance（V6 P2-3）：非 dict body 静默丢弃不抛 TypeError；
  S7 异常回用户脱敏（V2 P2-1，不回显 str(e)）
- llm_backend：max_tokens 默认 8192（V4 P2-1）+ _self_check 人民币口径（V4 P2-4）
"""
import json

from mangpai.feishu import bot
from mangpai.feishu.formatter import DISCLAIMER, format_report
from mangpai.feishu.router import handle
from mangpai.subjective import llm_backend
from mangpai.subjective.llm_channel import (
    _l2_enum, format_reading, render_structured_reading,
)

_ENGINE = {'caiming': {'tier_static': '小康', 'tier': '小康'},
           'guanming': {'is_guanming': False}}


def _five_dims(conclusion='一段断语'):
    return {d: {'conclusion': conclusion, 'basis': [], 'confidence': '中'}
            for d in ('性格', '事业', '财运', '婚姻', '应期')}


# ---------------------------------------------------------------- P0 免责声明

def test_disclaimer_engine_direct_path():
    md = handle('阳历 1992-10-09 13:58 男 河南信阳', use_llm=False)
    assert md.rstrip().endswith(DISCLAIMER.strip())


def test_disclaimer_llm_reading_path():
    out = format_reading({}, None, None)
    assert DISCLAIMER.strip() in out


def test_help_carries_privacy_notice_and_disclaimer():
    h = handle('/help')
    assert '第三方' in h and 'DeepSeek' in h      # 外发告知（V4 P1-2）
    assert DISCLAIMER.strip() in h


# ---------------------------------------------------------------- P1 lark_md 三符

def test_no_larkmd_unsupported_chars_engine_path():
    md = handle('阳历 1992-10-09 13:58 男 河南信阳', use_llm=False)
    assert '\n- ' not in md and '\n> ' not in md and '---' not in md


def test_no_larkmd_unsupported_chars_llm_path(monkeypatch):
    monkeypatch.setattr('mangpai.feishu.service.render_structured_reading',
                        lambda res, validate='mark': '【性格】(中) mock 五维')
    md = handle('阳历 1992-10-09 13:58 男 信阳', use_llm=True)
    assert '---' not in md and '\n> ' not in md and 'mock 五维' in md


# ---------------------------------------------------------------- P1 死亡词 mark→reject + L2 误报窗

def _fake_backend(text):
    return {'text': text, 'usage': {}, 'cost_usd': 0.0,
            'price_tier': 'offpeak', 'elapsed_s': 0.0, 'model': 'mock'}


def test_death_word_mark_mode_rejects(monkeypatch):
    """mark 模式命中死亡红线词 → 整段拒出，原文与附注均不展示。"""
    data = _five_dims()
    data['应期']['conclusion'] = '六十八岁寿终'
    monkeypatch.setattr('mangpai.subjective.llm_backend.call_deepseek',
                        lambda *a, **kw: _fake_backend(json.dumps(data, ensure_ascii=False)))
    out = render_structured_reading(_ENGINE, validate='mark')
    assert out == '[断语被死亡红线校验拦截，不予展示]'
    assert '寿终' not in out  # 附注也不展示


def test_death_word_reject_degrades_via_service(monkeypatch):
    """'[断语被' 前缀命中 service 降级白名单 → 引擎直出（不展示被拦断语）。"""
    monkeypatch.setattr('mangpai.feishu.service.render_structured_reading',
                        lambda res, validate='mark': '[断语被死亡红线校验拦截，不予展示]')
    md = handle('阳历 1992-10-09 13:58 男 信阳', use_llm=True)
    assert '引擎直出结论' in md and '断语被' not in md


def test_l2_death_refusal_window_exempts():
    """合规拒答句复述死亡词（V4 P2-2/2-3：「寿数」+「红线」外露）不计违规。"""
    data = _five_dims()
    data['应期']['conclusion'] = '命理不测生死，谨守安全红线，不予断言寿数'
    assert not any('死亡红线' in x['detail'] for x in _l2_enum(data, _ENGINE))
    # 窗口外真穿透仍拦
    data['应期']['conclusion'] = '命理不测生死，谨守安全红线。你寿数将尽'
    assert any('死亡红线' in x['detail'] for x in _l2_enum(data, _ENGINE))


def test_l2_death_refusal_passes_render(monkeypatch):
    """拒答句经误报窗豁免 → mark 模式正常展示（不触发 reject）。"""
    data = _five_dims()
    data['应期']['conclusion'] = '命理不测生死，不予断言寿数'
    monkeypatch.setattr('mangpai.subjective.llm_backend.call_deepseek',
                        lambda *a, **kw: _fake_backend(json.dumps(data, ensure_ascii=False)))
    out = render_structured_reading(_ENGINE, validate='mark')
    assert not out.startswith('[断语被')
    assert DISCLAIMER.strip() in out


# ---------------------------------------------------------------- F3 bot 健壮性

def test_handle_event_non_dict_body_dropped():
    """非 dict body（畸形 JSON 数组/字符串）静默丢弃，不抛 TypeError。"""
    assert bot.handle_event(['not', 'a', 'dict']) == {}
    assert bot.handle_event('oops') == {}
    assert bot.handle_event(None) == {}


def test_respond_error_sanitized(monkeypatch, caplog):
    """S7：引擎异常回用户通用信息，不回显 str(e) 内部详情（与 500 脱敏同口径）。"""
    def boom(text):
        raise RuntimeError('engine secret internals')

    class FakeClient:
        def __init__(self):
            self.replies = []

        def reply(self, mid, msg_type, text):
            self.replies.append(text)

    monkeypatch.setattr('mangpai.feishu.bot.route', boom)
    fc = FakeClient()
    with caplog.at_level('ERROR', logger='mangpai.feishu.bot'):
        bot._respond(fc, 'om_x', 'whatever')
    assert '内部错误' in fc.replies[0] and 'secret internals' not in fc.replies[0]
    assert any('排盘异常' in r.message for r in caplog.records)


# ---------------------------------------------------------------- F3 llm_backend

def test_max_tokens_default_8192():
    assert llm_backend.call_deepseek.__kwdefaults__['max_tokens'] == 8192


def test_self_check_rmb_offline():
    """_self_check 人民币口径（峰 ¥3.0/¥9.0、谷 ¥1.5/¥4.5）离线自检不挂。"""
    llm_backend._self_check()
