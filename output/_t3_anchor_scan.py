"""T3-S1 第一层：规则式语义锚扫描（零 API，281 例全量筛子）。

只吃 output/t3_s1/dump.json（引擎键值 + v5 reading），按 §5.1 五维定义
输出候选冲突清单（cand1=放大/缩水嫌疑，cand2=翻转嫌疑）。
已知假阳高（否定句/条件句），只作评审抽样筛子，不作判据。

产出: output/t3_s1/anchor_candidates.json
用法: python3 output/_t3_anchor_scan.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.llm_channel import _tier_rank, _TIER_ORDER, _GUAN_POSITIVE, _NEG_PREFIX  # noqa: E402
from mangpai.tests.heldout.blind_eval import _ZY_RULES, _ZY_EXCLUDE, _XIONG_MARKERS  # noqa: E402

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1')

# ---- 词族 ----
CAI_DOWN = ('贫穷', '贫困', '穷命', '不富', '难富', '财难聚', '财受制', '求财辛苦',
            '财运差', '财运不佳', '财运平平', '财运一般', '无财', '破财', '贫苦', '寒酸')
# 强向下词（tier 级判词，用于翻转判定；「破财/防破财」类风险警示不算翻转——
# 引擎富档+凶向（防破财）本就合法共存，实测误命中主力）
CAI_DOWN_HARD = ('贫穷', '贫困', '穷命', '不富', '难富', '财难聚', '财运差',
                 '财运不佳', '贫苦', '寒酸')
CAI_UP = ('发财', '财运亨通', '财运佳', '财源广进', '财源滚滚', '大富')
GUAN_NEG = ('与仕途无缘', '不宜官', '无官运', '不是官命', '难当官', '宜商不宜官',
            '非官命', '无官命', '官运不佳', '与官无缘', '仕途无缘', '难成官')
HUN_BAD = ('婚姻不顺', '婚姻差', '二婚', '多婚', '离婚', '婚变', '克夫', '克妻',
           '争战', '破败', '婚姻不稳', '婚姻易不稳', '感情波折', '婚姻波折', '再婚')
HUN_GOOD = ('婚姻美满', '婚姻好', '婚缘好', '婚缘不错', '夫妻恩爱', '婚姻稳定',
            '婚姻幸福', '感情稳定')
YQ_BAD = ('破财', '是非', '伤病', '官非', '牢狱', '大凶', '凶', '车祸', '疾病')
YQ_UP = ('发财', '进财', '得财', '财运亨通', '升官')
GRADE_RANK = {'总理': 5, '元首': 5, '省部级': 4, '厅级': 3, '处级': 2, '科级': 1}


def _neg_window_hit(text, words, before=4):
    """词命中且前 before 字符内无否定字 → 返回命中词。"""
    for w in words:
        i = text.find(w)
        while i != -1:
            if not any(c in _NEG_PREFIX or c in '不非难无莫勿未别' for c in text[max(0, i - before):i]):
                return w
            i = text.find(w, i + 1)
    return None


def _guan_positive_hit(text):
    """与 llm_channel._l2_enum 官命正向断言同口径。"""
    for w in _GUAN_POSITIVE:
        i = text.find(w)
        while i != -1:
            seg = text[max(0, i - 2):i + len(w) + 2]
            if not any(ch in _NEG_PREFIX for ch in seg):
                return w
            i = text.find(w, i + 1)
    return None


def _grade_ranks(text):
    return {GRADE_RANK[g] for g in GRADE_RANK if g in text}


def _occ_buckets(text):
    buckets = set()
    for words, bucket in _ZY_RULES:
        if any(w in text for w in words):
            if not any(x in text for x in _ZY_EXCLUDE.get(bucket, ())):
                buckets.add(bucket)
    return buckets


def scan_case(rec):
    """返回 {dim: {'cand': 1|2, 'why': str}} 候选（仅命中维）。"""
    ek = rec['engine_key']
    rd = rec['reading']
    out = {}

    def concl(dim):
        node = rd.get(dim) or {}
        return str(node.get('conclusion') or '')

    # ---------- 财运 ----------
    cm = ek['caiming']
    ranks = [_TIER_ORDER.index(v) for v in (cm.get('tier_static'), cm.get('tier'))
             if v in _TIER_ORDER]
    t_cai = concl('财运')
    if ranks:
        ceiling = max(ranks)
        nr = _tier_rank(t_cai)
        xiong = any(m in str(cm.get('summary') or '') for m in _XIONG_MARKERS)
        if ceiling >= 3:
            # 翻转=富档被说成贫困/财难聚：叙述未给引擎档位（narr_rank<ceiling）
            # 且含强向下词；「防破财」类风险警示不算（引擎凶向合法共存）
            w = _neg_window_hit(t_cai, CAI_DOWN_HARD)
            if w and nr < ceiling:
                out['财命'] = {'cand': 2, 'why': f'引擎={_TIER_ORDER[ceiling]}档，叙述含强向下词「{w}」且未达引擎档'}
        if ceiling <= 1 and nr >= 3:
            out['财命'] = {'cand': 2, 'why': f'引擎={_TIER_ORDER[ceiling]}档，叙述档位词到{_TIER_ORDER[nr]}'}
        if '财命' not in out and nr >= 0:
            d = nr - ceiling
            if d >= 2:
                out['财命'] = {'cand': 2, 'why': f'叙述档位越引擎两档+：引擎={_TIER_ORDER[ceiling]} 叙述={_TIER_ORDER[nr]}'}
            elif d == 1:
                out['财命'] = {'cand': 1, 'why': f'叙述档位较引擎抬一档：引擎={_TIER_ORDER[ceiling]} 叙述={_TIER_ORDER[nr]}'}
            elif d <= -1:
                out['财命'] = {'cand': 1, 'why': f'叙述档位较引擎压{-d}档：引擎={_TIER_ORDER[ceiling]} 叙述={_TIER_ORDER[nr]}'}
        if '财命' not in out and xiong:
            w = _neg_window_hit(t_cai, CAI_UP)
            has_down = any(w2 in t_cai for w2 in CAI_DOWN + ('凶', '风险', '谨慎', '波折'))
            if w and not has_down:
                out['财命'] = {'cand': 2, 'why': f'引擎全量轨带凶向，叙述称「{w}」且无凶向提示'}
            elif not has_down and nr >= 3:
                out['财命'] = {'cand': 1, 'why': '引擎带凶向，叙述纯正向无提示（淡化嫌疑）'}

    # ---------- 事业：官命 ----------
    gm = ek['guanming']
    t_sy = concl('事业')
    is_g = gm.get('is_guanming')
    if is_g is True:
        w = _neg_window_hit(t_sy, GUAN_NEG)
        if w:
            out['官命'] = {'cand': 2, 'why': f'引擎判官命=是，叙述含「{w}」'}
    elif is_g is False:
        w = _guan_positive_hit(t_sy)
        if w:
            out['官命'] = {'cand': 2, 'why': f'引擎判官命=否，叙述正向断言「{w}」'}
    # 官级抬压（引擎 grade/level 文本 vs 叙述级词）
    gtxt = ' '.join(str(gm.get(k) or '') for k in ('level', 'grade', 'summary'))
    er, nr_ = _grade_ranks(gtxt), _grade_ranks(t_sy)
    if er and nr_ and '官命' not in out:
        d = max(nr_) - max(er)
        if abs(d) >= 2:
            out['官命'] = {'cand': 2, 'why': f'官级差{d:+d}档：引擎={sorted(er)} 叙述={sorted(nr_)}'}
        elif abs(d) == 1:
            out['官命'] = {'cand': 1, 'why': f'官级差{d:+d}档：引擎={sorted(er)} 叙述={sorted(nr_)}'}

    # ---------- 事业：职业 ----------
    zy = ek['zhiye']
    primary = zy.get('primary')
    nb = _occ_buckets(t_sy)
    if nb:
        if not primary:
            # 引擎无明确倾向 → 叙述落具体桶：多为「倾向/宜」式软荐，记 cand1 待评审定性
            out['职业'] = {'cand': 1, 'why': f'引擎无明确职业倾向，叙述落桶={sorted(nb)}'}
        elif primary not in nb:
            out['职业'] = {'cand': 2, 'why': f'引擎主桶={primary}，叙述落桶={sorted(nb)}'}

    # ---------- 婚姻 ----------
    # 数据源=features.hunyin 全键（quality/duohun/dushen/summary）——
    # 引擎「多婚之象/独身之象」信号在 duohun/dushen，只看 quality 会把忠实叙述误判
    hyf = (rec.get('features') or {}).get('hunyin') or {}
    hyq = hyf.get('quality') or {}
    q = str(hyq.get('quality') or '') if isinstance(hyq, dict) else str(hyq or '')
    duo = hyf.get('duohun') or {}
    dus = hyf.get('dushen') or {}
    duo_sig = bool((duo.get('is_duohun') if isinstance(duo, dict) else None) or
                   (duo.get('factors') if isinstance(duo, dict) else None))
    dus_sig = bool((dus.get('is_dushen') if isinstance(dus, dict) else None) or
                   (dus.get('factors') if isinstance(dus, dict) else None))
    eng_neg = q in ('差', '凶', '劣') or duo_sig
    eng_pos = q in ('好', '佳', '吉') and not duo_sig  # 引擎自带多婚信号时叙述提多婚=忠实
    t_hy = concl('婚姻')
    bad_w = _neg_window_hit(t_hy, HUN_BAD)
    good_w = _neg_window_hit(t_hy, HUN_GOOD)
    # 宽口径好/差义（判「整体方向」用）：叙述整体好但附带凶信号（好但多婚/防离婚）
    # 是系统性放大（cand1），整体方向相反才算翻转（cand2）
    SOFT_GOOD = ('好', '稳', '安', '吉', '美', '恩爱', '不错', '尚可', '不坏', '相得')
    SOFT_BAD = ('差', '不顺', '波折', '不稳', '防', '注意', '易变', '孤')
    any_good = good_w or any(w in t_hy for w in SOFT_GOOD)
    any_bad = bad_w or any(w in t_hy for w in SOFT_BAD)
    if eng_pos and bad_w and not any_good:
        out['婚姻'] = {'cand': 2, 'why': f'引擎婚质={q}且无多婚信号，叙述纯差向含「{bad_w}」'}
    elif eng_neg and good_w and not any_bad:
        out['婚姻'] = {'cand': 2, 'why': f'引擎婚质={q or "?"}+多婚信号={duo_sig}，叙述纯好向称「{good_w}」'}
    elif eng_pos and bad_w and any_good:
        out['婚姻'] = {'cand': 1, 'why': f'引擎婚质={q}无多婚信号，叙述整体好但附加「{bad_w}」（放大凶信号嫌疑）'}
    elif eng_neg and any_bad and good_w:
        out['婚姻'] = {'cand': 1, 'why': f'引擎婚质={q or "?"}+多婚信号={duo_sig}，叙述好坏并陈'}
    elif q == '平' and good_w and not bad_w:
        out['婚姻'] = {'cand': 1, 'why': f'引擎婚质=平，叙述称「{good_w}」'}
    elif q == '平' and bad_w and not good_w:
        out['婚姻'] = {'cand': 1, 'why': f'引擎婚质=平，叙述含「{bad_w}」'}

    # ---------- 应期 ----------
    yq_txt = ' '.join([
        str(ek.get('yingqi_subj') or ''),
        json.dumps(ek.get('yunfan') or {}, ensure_ascii=False)])
    eng_yq_bad = any(w in yq_txt for w in ('破财', '是非', '反局', '伤病', '官非', '牢狱', '大凶'))
    t_yq = concl('应期')
    up_w = _neg_window_hit(t_yq, YQ_UP)
    bad_w2 = _neg_window_hit(t_yq, YQ_BAD)
    if eng_yq_bad and up_w and not bad_w2:
        out['应期'] = {'cand': 2, 'why': f'引擎应期含凶/反局，叙述称「{up_w}」无凶提示'}
    elif not eng_yq_bad and bad_w2 and not up_w:
        out['应期'] = {'cand': 1, 'why': f'引擎应期无凶象，叙述断「{bad_w2}」（自创凶事嫌疑）'}

    return out


def main():
    with open(os.path.join(OUT, 'dump.json'), encoding='utf-8') as f:
        dump = json.load(f)
    cands = {}
    from collections import Counter
    stat = Counter()
    for cid, rec in dump.items():
        hits = scan_case(rec)
        if hits:
            cands[cid] = hits
            for dim, h in hits.items():
                stat[(dim, h['cand'])] += 1
    with open(os.path.join(OUT, 'anchor_candidates.json'), 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=1)
    n2 = sum(1 for h in cands.values() if any(x['cand'] == 2 for x in h.values()))
    print(f'扫描 {len(dump)} 例，候选命中 {len(cands)} 例（含 cand2 的 {n2} 例）')
    for (dim, c), n in sorted(stat.items()):
        print(f'  {dim} cand{c}: {n}')


if __name__ == '__main__':
    main()
