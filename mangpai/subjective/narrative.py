"""郝金阳风格叙事层。

把 mangpai 引擎的结构化结论（dict）转成郝金阳口吻的自然语言推演。
不靠规则硬编码拼装断语——而是把【引擎结论】+ few-shot 范例 + 系统提示词
组装成 prompt，交给 LLM 习得郝金阳"第二人称直击、先断后理、敢下数字"的口吻
与"取象→锁定→判条件→应期→结论"五步因果链，生成当面断语。

依赖（均软依赖，缺失则降级返回组装好的 prompt 文本，不抛错）：
  - mangpai.subjective.prompts.hao_style_fewshot（FEWSHOT_EXAMPLES / HAO_STYLE_SYSTEM_PROMPT）
  - anthropic SDK（可选；无 API key/网络时降级）
"""
from __future__ import annotations
import os
from typing import Any, Dict, Optional

from mangpai.subjective.prompts.hao_style_fewshot import (
    FEWSHOT_EXAMPLES,
    HAO_STYLE_SYSTEM_PROMPT,
    format_fewshot_block,
)


# ---------------------------------------------------------------------------
# 引擎结论摘要：从 dict 抽取关键字段，拼成一行【引擎结论】（与 few-shot 同款）
# ---------------------------------------------------------------------------
def _zuogong_line(zg: dict) -> str:
    if not zg:
        return ''
    types = zg.get('work_types') or []
    lv = zg.get('work_level')
    tier = zg.get('work_tier', '')
    eff = zg.get('work_efficiency', '')
    head = f"做功：{'+'.join(types) if types else '无'} L{lv} {tier} {eff}".strip()
    return head


def _gongliang_line(gl: dict) -> str:
    if not gl:
        return ''
    lv = gl.get('level')
    tier = gl.get('tier_name', '')
    jing = gl.get('zhi_jing', '')
    fg = gl.get('fugui_pinjian', '')
    boundary = gl.get('boundary') or ''
    btxt = f' ｛边界区·{boundary}｝' if boundary else ''
    return f"层功：L{lv} {tier} {jing}（{fg}）{btxt}".strip()


def _zhengfan_line(zf: dict) -> str:
    if not zf:
        return ''
    cfg = zf.get('configuration', '')
    return f"正反：{cfg}".strip() if cfg else ''


def _caiming_line(cm: dict) -> str:
    if not cm:
        return ''
    return f"财命：{cm.get('tier', '')}·{cm.get('summary', '')}".strip('·')


def _guanming_line(gm: dict) -> str:
    if not gm:
        return ''
    is_g = gm.get('is_guanming')
    lvl = gm.get('level')
    grade = lvl.get('grade') if isinstance(lvl, dict) else lvl
    head = f"官命：{'是' if is_g else '否'}·{grade}"
    return f"{head}（{gm.get('summary', '')}）".strip()


def _hunyin_line(hy: dict) -> str:
    if not hy:
        return ''
    q = hy.get('quality')
    qtxt = q.get('quality') if isinstance(q, dict) else q
    dh = hy.get('duohun')
    dh_txt = '多婚' if isinstance(dh, dict) and dh.get('is_duohun') else ''
    return f"婚姻：{qtxt} {dh_txt}（{hy.get('summary', '')}）".strip()


def _zhiye_line(zy: dict) -> str:
    if not zy:
        return ''
    return f"职业：{zy.get('primary_label', '')}".strip()


def _muku_line(mk: dict) -> str:
    if not mk:
        return ''
    opens = [t.get('zhi') for t in mk.get('open_tombs', []) if t.get('zhi')]
    closed = [t.get('zhi') for t in mk.get('closed_tombs', []) if t.get('zhi')]
    rels = mk.get('tomb_relations', [])
    parts = []
    if opens:
        parts.append(f"开库{','.join(opens)}")
    if closed:
        parts.append(f"闭库{','.join(closed)}")
    if rels:
        parts.append(f"入墓{len(rels)}处")
    return f"墓库：{' '.join(parts)}" if parts else "墓库：无"


def _shensha_line(ss: dict) -> str:
    if not ss:
        return ''
    names = [k for k, v in ss.items() if isinstance(v, dict) and v.get('in_pillars')]
    return f"神煞：{','.join(names)}" if names else "神煞：无"


def _yingqi_line(yq: dict, da: dict, la: dict) -> str:
    """应期：优先取 yingqi.conclusion，否则回退 dayun/流年 analysis summary。"""
    if yq and (yq.get('conclusion') or yq.get('liunian_trigger') is not None):
        trig = yq.get('liunian_trigger')
        trig_txt = '触发' if trig else '未触发'
        return f"应期：{yq.get('conclusion', '')}（{trig_txt}）".strip()
    parts = []
    if da and da.get('summary'):
        parts.append(f"大运：{da['summary']}")
    if la and la.get('summary'):
        parts.append(f"流年：{la['summary']}")
    return f"应期：{' '.join(parts)}" if parts else ''


def _zeishen_bushen_line(zb: dict) -> str:
    """贼神捕神：净制程度 + 包制/冲链 + 功量点。"""
    if not zb:
        return ''
    sub = zb.get('zeishen_bushen') or {}
    jing = sub.get('jing_zhi') or '无制'
    bao = bool(zb.get('bao_zhi') and zb['bao_zhi'].get('detected'))
    clian = bool(zb.get('chong_lian') and zb['chong_lian'].get('detected'))
    flags = [s for s, on in (('包制', bao), ('冲链', clian)) if on]
    flag_txt = ('，' + '、'.join(flags)) if flags else ''
    return f"贼神捕神：净制={jing}{flag_txt}（功量点{zb.get('points', 0)}）"


def _xiangfa_ops_line(xo: dict) -> str:
    """象法操作层：锁定事物 + 各原则命中数。"""
    if not xo:
        return ''
    locked = xo.get('locked_subjects') or []
    all_f = xo.get('all_findings') or []
    if locked:
        return f"象法：锁{len(locked)}（{','.join(locked[:6])}）"
    if all_f:
        return f"象法：{len(all_f)}象（未锁定）"
    return ''


def _yunfan_line(yf: dict) -> str:
    """岁运反局：summary + 反局计数。"""
    if not yf:
        return ''
    df = yf.get('dayun_fan') or []
    lf = yf.get('liunian_fan') or []
    head = yf.get('summary') or ''
    if not head and not df and not lf:
        return ''
    return f"岁运反局：{head or '无反局'}（大运反{len(df)}·流年反{len(lf)}）"


def _zaihuo_line(zh: dict) -> str:
    """灾祸：最高风险 + 摘要（F14 起经 zaihuo_llm_view 物理屏蔽死亡档/
    寿元星 markers——批10 寿元红线，siwang 不进 LLM 通道）。"""
    if not zh:
        return ''
    from mangpai.subjective.zaihuo import zaihuo_llm_view
    view = zaihuo_llm_view(zh)
    mr = view.get('max_risk', '') or ''
    sm = view.get('summary', '') or ''
    if not mr and not sm:
        return ''
    return f"灾祸：{mr}（{sm}）".strip('（）')


def _laoyu_line(ly: dict) -> str:
    """牢狱：风险 + 摘要。"""
    if not ly:
        return ''
    risk = ly.get('risk', '') or ''
    sm = ly.get('summary', '') or ''
    if not risk and not sm:
        return ''
    return f"牢狱：{risk}（{sm}）".strip('（）')


def _xueli_line(xe: dict) -> str:
    """学历：层级 + 摘要。"""
    if not xe:
        return ''
    lv = xe.get('level_str', '') or ''
    sm = xe.get('summary', '') or ''
    if not lv and not sm:
        return ''
    return f"学历：{lv}（{sm}）".strip('（）')


def _liuqin_line(lq: dict) -> str:
    """六亲：摘要。"""
    if not lq:
        return ''
    sm = lq.get('summary', '') or ''
    return f"六亲：{sm}" if sm else ''


def _shipaige_line(sp: dict) -> str:
    """郑氏十排歌：神数摘要 / 域计数。"""
    if not sp:
        return ''
    ss = sp.get('shenshu_summary', '') or ''
    if ss:
        return f"十排歌：{ss}"
    domains = sp.get('domains') or []
    if domains:
        return f"十排歌：{len(domains)}域命中"
    return ''


def _tiyong_line(ty: dict) -> str:
    """体用：体/用计数。"""
    if not ty:
        return ''
    ti = ty.get('ti_count')
    yong = ty.get('yong_count')
    if ti is None and yong is None:
        return ''
    return f"体用：体{ti or 0}用{yong or 0}"


def _gongshen_line(gs: dict) -> str:
    """宫身：宫位六亲摘要。"""
    if not gs:
        return ''
    sm = gs.get('summary', '') or ''
    return f"宫身：{sm}" if sm else ''


def summarize_engine_result(engine_result: Dict[str, Any]) -> str:
    """把引擎结构化结论 dict 压成一行【引擎结论】（与 few-shot 同款风格）。

    engine_result 兼容两种形态：
      1. 裸 MangpaiEngine.compute_all() 输出（仅引擎维度：做功/层功/正反/墓库/
         神煞/大运流年分析）；
      2. bundle_case_result 合并后的 enriched dict（额外含 caiming/guanming/
         hunyin/zhiye/yingqi 及 dayun_gz/liunian_gz）。
    缺失字段静默跳过，不抛错。
    """
    if not isinstance(engine_result, dict):
        return str(engine_result)

    zg = engine_result.get('zuogong') or {}
    gl = engine_result.get('gongliang') or {}
    zf = engine_result.get('zhengfan') or {}
    mk = engine_result.get('muku') or {}
    ss = engine_result.get('shensha') or {}
    cm = engine_result.get('caiming') or {}
    gm = engine_result.get('guanming') or {}
    hy = engine_result.get('hunyin') or {}
    zy = engine_result.get('zhiye') or {}
    # 应期键名兼容：裸 compute_all() 产出 'yingqi_subj'，bundle_case_result
    # 合并的 enriched dict 用 'yingqi'。两者皆读，缺一取另一。
    yq = engine_result.get('yingqi') or engine_result.get('yingqi_subj') or {}
    da = engine_result.get('dayun_analysis') or {}
    la = engine_result.get('liunian_analysis') or {}
    zb = engine_result.get('zeishen_bushen') or {}
    xo = engine_result.get('xiangfa_ops') or {}
    yf = engine_result.get('yunfan') or {}
    zh = engine_result.get('zaihuo') or {}
    ly = engine_result.get('laoyu') or {}
    xe = engine_result.get('xueli') or {}
    lq = engine_result.get('liuqin') or {}
    sp = engine_result.get('shipaige') or {}
    ty = engine_result.get('tiyong') or {}
    gsh = engine_result.get('gongshen') or {}

    segs = [
        _zuogong_line(zg),
        _gongliang_line(gl),
        _zhengfan_line(zf),
        _caiming_line(cm),
        _guanming_line(gm),
        _hunyin_line(hy),
        _zhiye_line(zy),
        _muku_line(mk),
        _shensha_line(ss),
        _yingqi_line(yq, da, la),
        _zeishen_bushen_line(zb),
        _xiangfa_ops_line(xo),
        _yunfan_line(yf),
        _zaihuo_line(zh),
        _laoyu_line(ly),
        _xueli_line(xe),
        _liuqin_line(lq),
        # F18：gongmen_wuzhi 正式弃用隔离——is_wuzhi 近恒真零信息量，
        # 结论行通道切断（engine result 键因 schools selectors 保护链保留）
        _shipaige_line(sp),
        _tiyong_line(ty),
        _gongshen_line(gsh),
    ]
    segs = [s for s in segs if s and s.split('：', 1)[-1].strip()]
    return ' | '.join(segs)


def _bazi_line(engine_result: Dict[str, Any]) -> str:
    """拼【八字】行：四柱 + 可选大运/流年柱。"""
    bazi = engine_result.get('bazi') or {}
    if isinstance(bazi, dict):
        pillars = ' '.join(
            bazi.get(k, '') for k in ('year', 'month', 'day', 'hour') if bazi.get(k)
        )
    else:
        pillars = str(bazi)
    extra = []
    # F1 批删除 _dayun_gz/_liunian_gz 回退键（全库无写入者=死回退，批10）。
    dy = engine_result.get('dayun_gz')
    if dy:
        extra.append(f"{dy}运")
    ln = engine_result.get('liunian_gz')
    if ln:
        extra.append(f"{ln}年")
    return (pillars + ' ' + ' '.join(extra)).strip()


# ---------------------------------------------------------------------------
# bundle：把 calib_zhenbao.run_case 的 6 元组压成 render_hao_narrative 的入参 dict
# ---------------------------------------------------------------------------
def bundle_case_result(res, cm, gm, hy, zy, yq, dayun=None, liunian=None) -> Dict[str, Any]:
    """合并 engine compute_all() 输出与各 subjective 分析器输出为单一 dict。

    dayun/liunian 为 (gan, zhi[, year]) 元组，用于在【八字】行还原运/年柱。
    """
    merged: Dict[str, Any] = {}
    if isinstance(res, dict):
        merged.update(res)
    merged['caiming'] = cm
    merged['guanming'] = gm
    merged['hunyin'] = hy
    merged['zhiye'] = zy
    merged['yingqi'] = yq
    if dayun:
        gz = (dayun[0] if len(dayun) >= 1 else '') + (dayun[1] if len(dayun) >= 2 else '')
        merged['dayun_gz'] = gz
    if liunian:
        gz = (liunian[0] if len(liunian) >= 1 else '') + (liunian[1] if len(liunian) >= 2 else '')
        merged['liunian_gz'] = gz
    return merged


# ---------------------------------------------------------------------------
# LLM 调用（软依赖）
# ---------------------------------------------------------------------------
def _call_llm(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    """调 anthropic Claude 生成郝金阳风格断语。失败抛异常由调用方降级。"""
    import anthropic  # 软依赖
    client = anthropic.Anthropic()
    model = model or os.environ.get('ANTHROPIC_MODEL') or 'claude-sonnet-5'
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0.2,  # 低温度抑幻觉（原 0.7 数字漂移大）
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_prompt}],
    )
    # 兼容不同版本返回：content 为 list[Block] 或 str
    content = getattr(resp, 'content', resp)
    if isinstance(content, list):
        # 只取 TextBlock.text，跳过 ThinkingBlock 等非文本块。
        return ''.join(getattr(b, 'text', '') for b in content if hasattr(b, 'text'))
    return str(content)


# ---------------------------------------------------------------------------
# N1 生成后校验：断语中的数字/年份回对引擎字段，不存在则标记或拒绝
# ---------------------------------------------------------------------------
_CN_NUM = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5,
           '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def _cn_to_int(s: str) -> int | None:
    """中文小数字转 int（一/两/三/十/十一/二十…≤99），失败 None。"""
    if not s:
        return None
    if s in _CN_NUM:
        return _CN_NUM[s]
    if '十' in s:
        left, _, right = s.partition('十')
        tens = _CN_NUM.get(left, 1) if left else 1
        ones = _CN_NUM.get(right, 0) if right else 0
        if (left and left not in _CN_NUM) or (right and right not in _CN_NUM):
            return None
        return tens * 10 + ones
    return None


def _engine_number_whitelist(engine_result: Dict[str, Any]) -> Dict[str, Any]:
    """从引擎结果抽取数字白名单（年份/年龄/计数/金额档），供断语数字回对。

    - years: 结果 JSON 中全部 1800-2099 四位数（出生年/流年年/交运日期等）；
    - ages: 大运 start_age/end_age 整数 + 当前年龄（当前年−出生年）；
    - counts: 上下文计数（N步大运/N流年/入墓N处/锁N/命中N法/约N个/work_level/
      gongliang level/score 等）；
    - bands: 财命 summary 中的金额档字（百万/千万/亿/百亿/千亿…）。
    """
    import json
    import re
    from datetime import datetime

    years, ages, counts, bands = set(), set(), set(), set()
    try:
        blob = json.dumps(engine_result, ensure_ascii=False, default=str)
    except Exception:
        blob = str(engine_result)

    for m in re.finditer(r'(18\d{2}|19\d{2}|20\d{2})', blob):
        years.add(int(m.group(1)))
    for m in re.finditer(r'(?:start_age|end_age)["\']?\s*:\s*(\d+(?:\.\d+)?)', blob):
        ages.add(int(float(m.group(1))))
    birth_year = (engine_result.get('input') or {}).get('year')
    if birth_year:
        try:
            ages.add(datetime.now().year - int(birth_year))
        except Exception:
            pass
    for pat in (r'(\d+)步大运', r'(\d+)流年', r'入墓(\d+)处', r'锁(\d+)',
                r'命中(\d+)法', r'约(\d+)个', r'(\d+)岁运联动',
                r'"(?:work_level|level|score)": (\d+)'):
        for m in re.finditer(pat, blob):
            counts.add(int(m.group(1)))
    cm = engine_result.get('caiming') or {}
    cm_blob = str(cm.get('summary', '')) + str(cm.get('tier', ''))
    for m in re.finditer(r'(百亿|千亿|数十亿|千万|百万|十万|亿|万)', cm_blob):
        bands.add(m.group(1))
    return {'years': years, 'ages': ages, 'counts': counts, 'bands': bands}


def validate_narrative_numbers(text: str, engine_result: Dict[str, Any]) -> Dict[str, Any]:
    """校验断语中的数字：凡年份/年龄/计数/具体金额，须能在引擎字段中找到出处。

    覆盖：4位/2位年份（93年→1993 归一）、N岁、N次婚/N个孩子（含中文数字）、
    具体金额（N万/N亿，引擎只出档位不出具体金额，故一律标记）、金额档字
    （百万级/千万级/亿级须与财命档位同族）。

    Returns:
      {'ok': bool, 'violations': [{'text','kind','detail'}], 'whitelist': {...}}
    """
    import re

    wl = _engine_number_whitelist(engine_result)
    violations = []

    # 年份：4 位直接对；2 位对任一百家尾数
    for m in re.finditer(r'(\d{4})年', text):
        y = int(m.group(1))
        if 1800 <= y <= 2099 and y not in wl['years']:
            violations.append({'text': m.group(0), 'kind': 'year',
                               'detail': f'{y}年不在引擎年份白名单'})
    for m in re.finditer(r'(?<!\d)(\d{1,2})年', text):
        yy = int(m.group(1))
        if not any(y % 100 == yy for y in wl['years']):
            violations.append({'text': m.group(0), 'kind': 'year',
                               'detail': f'{m.group(1)}年无对应引擎年份'})

    # 年龄
    for m in re.finditer(r'(\d{1,2})岁', text):
        a = int(m.group(1))
        if a not in wl['ages']:
            violations.append({'text': m.group(0), 'kind': 'age',
                               'detail': f'{a}岁不在引擎年龄白名单'})

    # 计数：N次婚/段情/场官司、N个孩子/兄弟/丈夫（阿拉伯+中文数字）
    num = r'(\d+|[一二两三四五六七八九十]+)'
    for m in re.finditer(num + r'(?:次|段|场)(?:婚|情|官司|牢狱)', text):
        n = int(m.group(1)) if m.group(1).isdigit() else _cn_to_int(m.group(1))
        if n is not None and n not in wl['counts']:
            violations.append({'text': m.group(0), 'kind': 'count',
                               'detail': f'{m.group(1)}(次/段/场)不在引擎计数白名单'})
    for m in re.finditer(num + r'个(?:孩子|兄弟|姐妹|丈夫|老婆|妻子|儿子|女儿)', text):
        n = int(m.group(1)) if m.group(1).isdigit() else _cn_to_int(m.group(1))
        if n is not None and n not in wl['counts']:
            violations.append({'text': m.group(0), 'kind': 'count',
                               'detail': f'{m.group(1)}个不在引擎计数白名单'})

    # 具体金额：引擎只出档位不出具体金额，一律标记
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(万|亿)(?![级档])', text):
        violations.append({'text': m.group(0), 'kind': 'amount',
                           'detail': '具体金额非引擎产出（引擎仅出金额档）'})

    # 金额档字：须与财命档位同族
    for m in re.finditer(r'(百亿|千亿|数十亿|千万|百万|十万|亿)级', text):
        if m.group(1) not in wl['bands']:
            violations.append({'text': m.group(0), 'kind': 'band',
                               'detail': f'{m.group(1)}级与财命档位不符'})

    return {'ok': not violations, 'violations': violations, 'whitelist': wl}


def _format_validation_note(report: Dict[str, Any]) -> str:
    lines = ['【引擎校验】以下数字未在引擎结论中找到出处（请人工复核，勿直采信）：']
    for v in report['violations']:
        lines.append(f"  - 「{v['text']}」({v['kind']}): {v['detail']}")
    return '\n'.join(lines)



# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def render_hao_narrative(
    engine_result: Dict[str, Any],
    user_question: Optional[str] = None,
    *,
    call_llm: bool = True,
    fewshot_examples: list | None = None,
    model: str | None = None,
    validate: str = 'mark',
) -> str:
    """把引擎结构化结论渲染成郝金阳风格的自然语言推演。

    Args:
      engine_result: 引擎结构化结论 dict（裸 compute_all() 输出或
        bundle_case_result 合并后的 enriched dict 均可）。
      user_question: 命主当面所问（可选，如"你看我今年养车怎么样？"）。
        若给，则断语须围绕此问；否则做通推断语。
      call_llm: True 则调 LLM 生成断语；False 或 LLM 不可用时，
        返回组装好的 prompt 文本（系统提示+few-shot+引擎结论+所问），
        供外部接 LLM。默认 True。
      fewshot_examples: 自定义 few-shot 列表覆盖默认 FEWSHOT_EXAMPLES。
      model: 指定 LLM 模型 id，默认取 ANTHROPIC_MODEL 环境变量或 claude-sonnet-5。
      validate: 生成后数字校验（N1）。'mark'(默认)=断语后附【引擎校验】
        未出处的数字清单；'reject'=有未出处数字则不出断语，返回拦截说明；
        'off'=不校验。仅对 LLM 实调路径生效（prompt 降级路径不校验）。

    Returns:
      郝金阳口吻的断语文本；LLM 不可用时返回降级 prompt 文本。
    """
    engine_conclusion = summarize_engine_result(engine_result)
    bazi_line = _bazi_line(engine_result)
    examples = fewshot_examples if fewshot_examples is not None else FEWSHOT_EXAMPLES
    fewshot_text = format_fewshot_block(examples)

    question_part = f"命主所问：{user_question}" if user_question else "命主未明问，做通推断语。"
    user_prompt = (
        f"以下是郝金阳断语的范例，每例三段：【八字】→【引擎结论】→【郝断语】：\n\n"
        f"{fewshot_text}\n\n"
        f"────────\n"
        f"现在请你照此范例，对下面这个命造当面断来：\n"
        f"【八字】{bazi_line}\n"
        f"【引擎结论】{engine_conclusion}\n"
        f"{question_part}\n\n"
        f"要求：第二人称直击命主，先断后理、口语化不绕弯；"
        f"凡下数字（年份/岁数/次数/金额），只许下引擎结论中出现的数字，"
        f"引擎未给的数字不许编造，宁可断方向不断数；"
        f"因果五步（取象→锁定→判条件→应期→结论）每步显式。只输出断语本身。"
    )

    if not call_llm:
        return user_prompt

    try:
        text = _call_llm(HAO_STYLE_SYSTEM_PROMPT, user_prompt, model=model)
    except Exception as e:
        # 降级：返回组装好的 prompt，供外部接 LLM；不抛错、不破验证。
        return (
            f"[LLM 不可用，降级返回 prompt 文本 | 原因: {e}]\n\n"
            f"===== SYSTEM =====\n{HAO_STYLE_SYSTEM_PROMPT}\n\n"
            f"===== USER =====\n{user_prompt}"
        )

    # N1 生成后校验：断语数字回对引擎字段
    if validate != 'off':
        report = validate_narrative_numbers(text, engine_result)
        if not report['ok']:
            if validate == 'reject':
                return (
                    '[断语被引擎校验拦截：含引擎结论中无出处的数字，不予输出]\n'
                    + _format_validation_note(report)
                )
            text = text + '\n\n' + _format_validation_note(report)
    return text
