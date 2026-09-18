"""H-fix-7 评测框架公共模块（防口径漂移）。

承载 output/ 评估管线四组公共逻辑（原 _n2_*/_t3_*/_v3_*/_w4_*/_w5_* 各自重复实现，
同一指标三份实现改一处漏一处 = 口径漂移风险，H10 P1 清单）：

1. runner — `run_llm_eval`：LLM 批跑调度（ThreadPoolExecutor 并发 + jsonl 断点续跑
   + 成本累加 + 汇总打印）。异常纪律继承 H-fix-2c：LLMBackendError / JSONDecodeError
   **不吞**——记 api_error/parse_error 入记录并在汇总打印异常计数；其它异常不捕获。
   llm_backend 为惰性 import（检查类脚本不依赖 LLM 后端）。
2. 材料组装 — `build_engine_materials` / `reading_text`：评审/judge prompt 用户材料。
   脚本间差异（hunyin signals 截断、新维 qianyi/xiangmao 并入）以显式形参标注，
   禁止静默统一。
3. 校准 — `load_jsonl` / `review_stats` / `agreement_stats` / `judge_stats` /
   `judge_acceptance`：一致率 / 翻转召回 / 达标判定（三层漏斗）。cal 字典装配与
   打印格式留在各脚本（历史 schema 不动）。
4. 抽样 — `stratified_fill`：tier_static × is_guanming 分层随机补足（seed 由调用方
   持有，可复现）。
5. 检查 — `engine_fe` / 禁词表 / `xm_forbidden_scan` / `qianyi_info` /
   `xiangmao_info` / `qianyi_honest_nosignal`：引擎重算入口、迁移/相貌禁词扫描、
   无信号如实判定（原 _w4/_w5/_n2_analyze 跨脚本重复）。

口径红线：只下沉逐字相同的逻辑；任何脚本间差异一律走形参，且默认值保持
原脚本行为。历史报告数字的可复现性由新老实现对拍（零 API）保证。
"""
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ================================================================ 1. runner

def run_llm_eval(mode, ids, dump, out_dir, *,
                 review_system, judge_system,
                 make_review_user, make_judge_user,
                 review_out='review30.jsonl', judge_out='judge281.jsonl'):
    """评审（review）/ judge 双实例批跑（原 _t3_eval.run/_n2_eval.run 逐字下沉）。

    断点续跑：已入 out jsonl 的 id 跳过；api_error/parse_error 记账不吞。
    """
    from mangpai.subjective.llm_backend import call_deepseek, LLMBackendError

    system = review_system if mode == 'review' else judge_system
    mk_user = make_review_user if mode == 'review' else make_judge_user
    out_path = os.path.join(out_dir, review_out if mode == 'review' else judge_out)
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding='utf-8') as f:
            for line in f:
                done.add(json.loads(line)['id'])
    todo = [cid for cid in ids if cid not in done]
    print(f'{mode}: 待跑 {len(todo)}/{len(ids)}')

    def one(cid):
        rec = {'id': cid}
        user = mk_user(dump[cid])
        t0 = time.monotonic()
        try:
            resp = call_deepseek(system, user, model='deepseek-v4-pro', max_tokens=16384)
        except LLMBackendError as e:
            rec['api_error'] = str(e)
            return rec
        rec['usage'] = resp['usage']
        rec['cost_cny'] = resp['cost_cny']
        rec['price_tier'] = resp['price_tier']
        rec['elapsed_s'] = round(time.monotonic() - t0, 2)
        try:
            rec['result'] = json.loads(resp['text'])
        except json.JSONDecodeError:
            rec['parse_error'] = resp['text'][:300]
        return rec

    with ThreadPoolExecutor(max_workers=8) as ex, \
            open(out_path, 'a', encoding='utf-8') as f:
        for rec in ex.map(one, todo):
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            f.flush()
    recs = [json.loads(l) for l in open(out_path, encoding='utf-8')]
    n_err = sum(1 for r in recs if 'api_error' in r or 'parse_error' in r)
    # S1：未知 provider cost_cny=None（未计价），不计入汇总；cost_usd=历史批兼容键
    cost = sum(r.get('cost_cny') or r.get('cost_usd') or 0 for r in recs)
    tiers = {r.get('price_tier') for r in recs}
    print(f'{mode}: 完成 {len(recs)}，异常 {n_err}，成本 ¥{cost:.2f}，档位={tiers}')


# ================================================================ 2. 材料组装

def build_engine_materials(rec, *, truncate_hunyin_signals=False,
                           include_newdims=False):
    """引擎键值 JSON（截长防 token 膨胀），原 _t3_eval/_n2_eval._materials。

    形参=脚本间既有差异（保留原口径，不统一）：
    - truncate_hunyin_signals：_t3_eval 旧口径，hunyin.signals 长列表截前 6 条
      （注意：features 有 hunyin 时整键被替换，该截断仅对 features 缺 hunyin 的
      记录生效）；_n2_eval 无此步。
    - include_newdims：_n2_eval 新维材料（qianyi 原局 marker+应期窗、xiangmao
      各线 hit/desc 并入引擎键值）；_t3_eval 五维口径无此步。
    """
    ek = json.loads(json.dumps(rec['engine_key'], ensure_ascii=False))
    # yunfan 流年反局逐年长列表截前 2 年
    yf = ek.get('yunfan') or {}
    for k in ('liunian_fan', 'liunian_ji', 'sui_yun_liandong'):
        v = yf.get(k)
        if isinstance(v, list) and len(v) > 2:
            yf[k] = v[:2] + [{'_截断': f'共{len(v)}条'}]
    if truncate_hunyin_signals:
        hy = ek.get('hunyin') or {}
        if isinstance(hy.get('signals'), list) and len(hy['signals']) > 6:
            hy['signals'] = hy['signals'][:6] + [f'…共{len(hy["signals"])}条']
    fe = rec.get('features') or {}
    # 婚姻维材料补全：engine_key 只有 quality，多婚/独身信号在
    # duohun/dushen/summary——缺失会把忠实叙述误判成放大/翻转
    hyf = fe.get('hunyin') or {}
    if hyf:
        ek['hunyin'] = {k: hyf.get(k) for k in ('quality', 'duohun', 'dushen', 'summary')}
    # 应期维材料补全：yunfan 只含反局，流年吉/凶依据在 liunian_analysis；
    # yingqi_subj 只给了 conclusion 一行
    yq = fe.get('yingqi_subj') or {}
    if yq:
        ek['yingqi_subj'] = yq
    la = fe.get('liunian_analysis') or {}
    if la:
        comp = {'summary': la.get('summary'), 'ji_count': la.get('ji_count'),
                'xiong_count': la.get('xiong_count'), 'liunian': []}
        for e in (la.get('liunian') or [])[:3]:
            rels = []
            for r in (e.get('gan_relations') or []) + (e.get('zhi_relations') or []):
                d_ = str(r.get('desc') or '')
                hs = (r.get('he_semantic') or {}).get('desc')
                rels.append(d_ + (f'（{hs}）' if hs else ''))
            comp['liunian'].append({'gz': e.get('gz'), 'shishen': e.get('gan_shishen'),
                                    'overall': e.get('overall'),
                                    'rels': rels[:6]})
        ek['liunian_analysis'] = comp
    # 评审/judge 判定应期维须见 dayun_analysis 逐运 overall+正负信号
    # （叙述按迭代 5 锚定此表，评审看不到会把忠实叙述误判成自创）。
    da = fe.get('dayun_analysis') or {}
    if da.get('dayun'):
        ek['dayun_analysis'] = {
            'summary': da.get('summary'),
            'dayun': [{'gz': d.get('gz'), 'order': d.get('order'),
                       'overall': d.get('overall'),
                       'positive_signals': d.get('positive_signals'),
                       'negative_signals': d.get('negative_signals')}
                      for d in da['dayun']]}
    if include_newdims:
        # N2 新维材料：qianyi（原局 marker + 应期窗/安居窗）、xiangmao（各线 hit/desc）
        qy = fe.get('qianyi') or {}
        if qy:
            ek['qianyi'] = qy
        xm = fe.get('xiangmao') or {}
        if xm:
            ek['xiangmao'] = xm
    return ek


def reading_text(rec, dims):
    """被评叙述原文拼装（按维度顺序，缺维标「（无叙述）」）。"""
    lines = []
    for dim in dims:
        node = (rec['reading'].get(dim) or {})
        c = str(node.get('conclusion') or '').strip()
        lines.append(f'【{dim}】{c}' if c else f'【{dim}】（无叙述）')
    return '\n'.join(lines)


# ================================================================ 3. 校准

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(path):
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            out[r['id']] = r
    return out


def review_stats(review, sample, dims, l2, new_dims=()):
    """评审样本汇总：逐维评分计数 + 翻转（s=2）清单 + 新维红线清单。

    返回 (r_stat, r_flips, r_reds, r_tot)；new_dims 为空时 r_reds 恒 []。
    """
    r_stat = Counter()
    r_flips = []
    r_reds = []
    for cid in sample:
        sc = review[cid]['result']['scores']
        for dim in dims:
            s = sc[dim]['s']
            r_stat[(dim, s)] += 1
            if s == 2:
                r_flips.append({'id': cid, 'dim': dim,
                                'note': sc[dim].get('note', ''),
                                'narr': sc[dim].get('narr', ''),
                                'eng': sc[dim].get('eng', ''),
                                'l2': cid in l2})
            if dim in new_dims and sc[dim].get('red'):
                r_reds.append({'id': cid, 'dim': dim,
                               'narr': sc[dim].get('narr', '')})
    r_tot = sum(v for (d, s), v in r_stat.items() if s in (0, 1, 2))
    return r_stat, r_flips, r_reds, r_tot


def agreement_stats(review, judge, sample, dims, dim_map, *,
                    divergence_detail=False):
    """评审 vs judge 一致率 + 翻转召回（抽样重叠例，N/A 双方剔除）。

    divergence_detail=True 时 divergences 条目带 r_note/j_ref 摘录
    （_t3/_v3 旧口径；_n2 旧口径不带）。
    返回 (agree, tot, flip_recall_hit, flip_recall_tot, per_dim, divergences)。
    """
    agree = tot = 0
    flip_recall_hit = flip_recall_tot = 0
    per_dim = Counter()
    divergences = []
    for cid in sample:
        if cid not in judge or 'result' not in judge[cid]:
            continue
        rsc = review[cid]['result']['scores']
        jsc = judge[cid]['result'].get('items', {})
        for dim in dims:
            rv = rsc[dim]['s']
            jv = jsc.get(dim_map[dim], {}).get('lv')
            if rv == 'N/A' or jv == 'N/A' or jv is None:
                continue
            tot += 1
            per_dim[(dim, 'tot')] += 1
            if rv == jv:
                agree += 1
                per_dim[(dim, 'agree')] += 1
            else:
                d = {'id': cid, 'dim': dim, 'review': rv, 'judge': jv}
                if divergence_detail:
                    d['r_note'] = rsc[dim].get('note', '')[:60]
                    d['j_ref'] = str(jsc.get(dim_map[dim], {}).get('ref', ''))[:60]
                divergences.append(d)
            if rv == 2:
                flip_recall_tot += 1
                if jv == 2:
                    flip_recall_hit += 1
    return agree, tot, flip_recall_hit, flip_recall_tot, per_dim, divergences


def judge_stats(judge, dims, dim_map, new_dims=(), *, flip_with_ref=False):
    """judge 记录集汇总：逐维 lv 计数 + 翻转清单 + 新维红线清单。

    flip_with_ref=True 时翻转条目带 ref 摘录（_t3/_v3 旧口径；_n2 不带）。
    返回 (j_stat, j_flips, j_reds, j_tot)。
    """
    j_stat = Counter()
    j_flips = []
    j_reds = []
    for cid, r in judge.items():
        if 'result' not in r:
            continue
        for dim in dims:
            it = r['result'].get('items', {}).get(dim_map[dim], {})
            lv = it.get('lv')
            if lv in (0, 1, 2):
                j_stat[(dim, lv)] += 1
                if lv == 2:
                    f = {'id': cid, 'dim': dim,
                         'q': str(it.get('q', ''))[:120]}
                    if flip_with_ref:
                        f['ref'] = str(it.get('ref', ''))[:120]
                    j_flips.append(f)
            if dim in new_dims and it.get('red'):
                j_reds.append({'id': cid, 'dim': dim,
                               'q': str(it.get('q', ''))[:120]})
    j_tot = sum(j_stat.values())
    return j_stat, j_flips, j_reds, j_tot


def judge_acceptance(agree, tot, flip_recall_hit, flip_recall_tot):
    """达标判定：一致率 ≥85% 且翻转召回 100% → 采信 judge。
    返回 (agree_rate, recall, accept)。"""
    agree_rate = agree / tot if tot else 0
    recall = flip_recall_hit / flip_recall_tot if flip_recall_tot else 1.0
    return agree_rate, recall, agree_rate >= 0.85 and recall >= 1.0


# ================================================================ 4. 抽样

def stratified_fill(dump, forced, n, rng):
    """分层随机补足（tier_static × is_guanming），原 _n2_sample/_v3_sample 逐字下沉。

    forced 之外的案例按层打乱（rng 由调用方持 seed），按层大小降序轮转取满
    n - len(forced) 个；层全空提前终止。
    """
    strata = defaultdict(list)
    for cid, rec in dump.items():
        if cid in forced:
            continue
        tier = (rec['engine_key'].get('caiming') or {}).get('tier_static') or 'NA'
        gm = (rec['engine_key'].get('guanming') or {}).get('is_guanming')
        strata[(tier, gm)].append(cid)
    for v in strata.values():
        rng.shuffle(v)
    fill = []
    order = sorted(strata, key=lambda s: -len(strata[s]))
    while len(fill) < n - len(forced):
        progressed = False
        for s in order:
            if strata[s] and len(fill) < n - len(forced):
                fill.append(strata[s].pop())
                progressed = True
        if not progressed:
            break
    return fill


# ================================================================ 5. 检查

QIANYI_FORBID = ('出国', '移民', '海外', '国外', '外国')
XM_FORBID = ('漂亮', '美', '丑', '帅')
XM_EXEMPT = ('美元', '美金')  # 丑时/X丑干支另行判定
GANZHI_RE = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')
_QIANYI_NOASSERT_RE = re.compile(r'(宜|适合|会|必有|主).{0,4}(迁移|远行)')


def engine_fe(c):
    """trainset 案例 → (compute_all 结果, build_payload 特征)。

    合成 bazi_data（shishen/kong_wang/di_zhi_relations 空壳由引擎重算填充），
    原 _w4/_w5/_n2_analyze/_t3_dump 四处逐字相同构造。
    """
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    bazi_data = {'bazi': dict(c['bazi']), 'shishen': {}, 'kong_wang': {},
                 'di_zhi_relations': {},
                 'input': {'gender': c.get('gender', '男'),
                           'year': c.get('year', 1960)}}
    res = MangpaiEngine(bazi_data).compute_all()
    return res, build_payload(res)


def qianyi_info(fe):
    """迁移维引擎信号摘要：原局 markers + 应期移动窗 + 安居窗。"""
    qy = fe.get('qianyi') or {}
    yj = qy.get('qianyi_yuanju') or {}
    yq = qy.get('qianyi_yingqi') or {}
    return {'markers': [str(m) for m in (yj.get('markers') or [])],
            'moves': yq.get('move_windows') or [],
            'stays': yq.get('stay_windows') or []}


def xiangmao_info(fe, *, require_desc=False):
    """相貌维命中线 {线名: desc}（xiuqi/jinshui/muhuo/meili/shencai + yanxiang）。

    require_desc=True 时五主线须 hit 且 desc 非空（_w5 旧口径）；False 仅看 hit
    （_w4 旧口径）。眼象线两口径一致：bing/ding/gui 任一真且 desc 非空。
    """
    xm = fe.get('xiangmao') or {}
    lines = {}
    for k in ('xiuqi', 'jinshui', 'muhuo', 'meili', 'shencai'):
        node = xm.get(k) or {}
        if node.get('hit') and (not require_desc or node.get('desc')):
            lines[k] = str(node.get('desc') or '')
    yan = xm.get('yanxiang') or {}
    if (yan.get('bing') or yan.get('ding') or yan.get('gui')) and yan.get('desc'):
        lines['yanxiang'] = str(yan['desc'])
    return lines


def xm_forbidden_scan(text):
    """相貌维禁词直扫（±1 相邻字排除窗，与校验器同口径近似）。"""
    hits = []
    for w in XM_FORBID:
        for m in re.finditer(re.escape(w), text):
            i = m.start()
            ctx = text[max(0, i - 1):i + len(w) + 1]
            if any(e in ctx for e in XM_EXEMPT):
                continue
            if w == '丑':
                after = text[i + 1:i + 2]
                before = text[i - 1:i]
                if after == '时' or before in '甲乙丙丁戊己庚辛壬癸':
                    continue
            hits.append((w, ctx))
    return hits


def qianyi_honest_nosignal(text):
    """迁移无信号如实判定：含「无」且不含迁移/远行断言（w4/w5/_n2_analyze 同口径）。"""
    return '无' in text and not _QIANYI_NOASSERT_RE.search(text)
