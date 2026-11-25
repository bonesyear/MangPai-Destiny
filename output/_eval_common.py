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
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.llm_channel import (
    _QIANYI_FORBID, _XIANGMAO_FORBID, _xiangmao_exempt)


FEWSHOT_CONTAMINATED_IDS = frozenset({
    'zhenbao-01', 'zhenbao-14a', 'zhenbao-23b',
    'cj-富火运发财数百', 'shouke-qi19-伤官去官官员',
})


def without_fewshot_contamination(records):
    if isinstance(records, dict):
        return {key: value for key, value in records.items()
                if key not in FEWSHOT_CONTAMINATED_IDS}
    return [rec for rec in records
            if (rec if isinstance(rec, str) else rec['id']) not in FEWSHOT_CONTAMINATED_IDS]


# ================================================================ 1. runner

def _validate_eval_result(mode, result, dims):
    root = 'scores' if mode == 'review' else 'items'
    if not isinstance(result, dict) or not isinstance(result.get(root), dict):
        raise ValueError(f'缺少对象字段 {root}')
    if set(result[root]) != set(dims):
        raise ValueError(f'{root} 维键不符: {sorted(result[root])}')
    score_key = 's' if mode == 'review' else 'lv'
    for dim in dims:
        node = result[root][dim]
        if not isinstance(node, dict):
            raise ValueError(f'{dim} 不是对象')
        _score_value(node.get(score_key), score_key)
        if 'red' in node and type(node['red']) is not bool:
            raise ValueError('red 必须为 bool')
        for key in ('narr', 'eng', 'note', 'q', 'ref'):
            if key in node and node[key] is not None and not isinstance(node[key], str):
                raise ValueError(f'{key} 必须为字符串或 null')


def _excerpt_check(mode, result, rec):
    reading = rec.get('reading')
    if not isinstance(reading, dict):
        return 0, 0
    original = json.dumps(reading, ensure_ascii=False)
    root = 'scores' if mode == 'review' else 'items'
    quote = 'narr' if mode == 'review' else 'q'
    total = bad = 0
    for node in result.get(root, {}).values():
        text = node.get(quote)
        if text:
            total += 1
            bad += text not in original
    return total, bad


def summarize_costs(records):
    return {
        'cost_cny': sum(r.get('cost_cny') or 0 for r in records),
        'cost_usd': sum(r.get('cost_usd') or 0 for r in records),
    }


def load_batch(batch_dir):
    attempts = []
    for path in sorted(glob.glob(os.path.join(batch_dir, 'batch_*.jsonl'))):
        with open(path, encoding='utf-8') as f:
            attempts.extend(json.loads(line) for line in f if line.strip())
    latest = {}
    for index, rec in enumerate(attempts):
        key = (rec.get('timestamp') or '', rec.get('run_id') or '', index)
        if rec['id'] not in latest or key >= latest[rec['id']][0]:
            latest[rec['id']] = (key, rec)
    return attempts, [item[1] for item in latest.values()]


def run_llm_eval(mode, ids, dump, out_dir, *,
                 review_system, judge_system,
                 make_review_user, make_judge_user,
                 review_out='review30.jsonl', judge_out='judge281.jsonl',
                 review_dims=(), judge_dims=()):
    """评审/judge 批跑；只跳过同 prompt 的成功记录，错误续跑补做。"""
    from mangpai.subjective.llm_backend import (
        call_deepseek, LLMBackendError, _API_URL, _env_value)

    base_url = _env_value('MANGPAI_LLM_BASE_URL', '') or _API_URL
    thinking = (_env_value('MANGPAI_LLM_THINKING', '1') or '1') != '0'
    if (base_url != _API_URL or not thinking) \
            and os.environ.get('MANGPAI_ALLOW_NONDEFAULT_EVALUATOR') != '1':
        raise RuntimeError('非默认评审端点或 thinking 配置；须显式设置 '
                           'MANGPAI_ALLOW_NONDEFAULT_EVALUATOR=1')
    system = review_system if mode == 'review' else judge_system
    mk_user = make_review_user if mode == 'review' else make_judge_user
    out_path = os.path.join(out_dir, review_out if mode == 'review' else judge_out)
    prompt_sha = hashlib.sha256(system.encode('utf-8')).hexdigest()
    endpoint_host = urllib.parse.urlsplit(base_url).hostname or ''
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding='utf-8') as f:
            for line in f:
                rec = json.loads(line)
                if 'result' in rec and rec.get('system_sha256', prompt_sha) == prompt_sha:
                    done.add(rec['id'])
    todo = [cid for cid in ids if cid not in done]
    print(f'{mode}: 待跑 {len(todo)}/{len(ids)}')

    def one(cid):
        rec = {
            'id': cid, 'requested_model': 'deepseek-v4-pro',
            'endpoint_host': endpoint_host, 'thinking': thinking,
            'system_sha256': prompt_sha,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        user = mk_user(dump[cid])
        t0 = time.monotonic()
        try:
            resp = call_deepseek(system, user, model='deepseek-v4-pro', max_tokens=16384)
        except LLMBackendError as e:
            rec['api_error'] = str(e)
            if hasattr(e, 'usage'):
                rec['usage'] = e.usage
                rec['cost_cny'] = e.cost_cny
            return rec
        rec['usage'] = resp['usage']
        rec['cost_cny'] = resp['cost_cny']
        rec['price_tier'] = resp['price_tier']
        rec['elapsed_s'] = round(time.monotonic() - t0, 2)
        rec['model'] = resp.get('model') or resp.get('requested_model') or 'deepseek-v4-pro'
        rec['requested_model'] = resp.get('requested_model', 'deepseek-v4-pro')
        if resp.get('endpoint'):
            rec['endpoint_host'] = urllib.parse.urlsplit(resp['endpoint']).hostname or ''
        rec['thinking'] = resp.get('thinking', thinking)
        try:
            result = json.loads(resp['text'])
        except json.JSONDecodeError:
            rec['parse_error'] = resp['text'][:300]
            return rec
        try:
            _validate_eval_result(
                mode, result, review_dims if mode == 'review' else judge_dims)
        except (TypeError, ValueError) as e:
            rec['schema_error'] = str(e)
            return rec
        rec['result'] = result
        rec['excerpt_total'], rec['excerpt_mismatch'] = _excerpt_check(mode, result, dump[cid])
        return rec

    with ThreadPoolExecutor(max_workers=8) as ex, \
            open(out_path, 'a', encoding='utf-8') as f:
        for rec in ex.map(one, todo):
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            f.flush()
    recs = [json.loads(l) for l in open(out_path, encoding='utf-8')]
    n_err = sum(1 for r in recs
                if 'api_error' in r or 'parse_error' in r or 'schema_error' in r)
    costs = summarize_costs(recs)
    tiers = {r.get('price_tier') for r in recs}
    excerpts = sum(r.get('excerpt_mismatch', 0) for r in recs)
    excerpt_tot = sum(r.get('excerpt_total', 0) for r in recs)
    print(f'{mode}: 完成 {len(recs)}，异常 {n_err}，成本 ¥{costs["cost_cny"]:.2f}'
          f' + ${costs["cost_usd"]:.4f}（分币别），档位={tiers}；'
          f'摘录不符 {excerpts}/{excerpt_tot}')


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


def load_id_file(path):
    data = load_json(path)
    if isinstance(data, dict):
        if type(data.get('n')) is not int or data['n'] <= 0 or not data.get('batch'):
            raise ValueError(f'名单缺少有效 n/batch 来源: {path}')
        return data, data['ids']
    return {'batch': None}, data


def load_jsonl(path):
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            out[r['id']] = r
    return out


def _score_value(value, key):
    if value == 'N/A':
        return value
    if type(value) is not int or value not in (0, 1, 2):
        raise ValueError(f'{key} 必须为整数 0/1/2 或 N/A，收到 {value!r}')
    return value


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
            s = _score_value(sc[dim]['s'], 's')
            r_stat[(dim, s)] += 1
            if s == 2:
                r_flips.append({'id': cid, 'dim': dim,
                                'note': sc[dim].get('note') or '',
                                'narr': sc[dim].get('narr') or '',
                                'eng': sc[dim].get('eng') or '',
                                'l2': cid in l2})
            red = sc[dim].get('red', False)
            if type(red) is not bool:
                raise ValueError(f'red 必须为 bool，收到 {red!r}')
            if dim in new_dims and red:
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
        rsc = review[cid]['result']['scores']
        jsc = judge.get(cid, {}).get('result', {}).get('items', {})
        for dim in dims:
            rv = _score_value(rsc[dim]['s'], 's')
            jkey = dim_map[dim]
            if jsc and jkey not in jsc:
                raise ValueError(f'judge 缺少维度键: {jkey}')
            jv = _score_value(jsc[jkey]['lv'], 'lv') if jkey in jsc else None
            if rv == 2:
                flip_recall_tot += 1
                if jv == 2:
                    flip_recall_hit += 1
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
                    d['r_note'] = (rsc[dim].get('note') or '')[:60]
                    d['j_ref'] = str(jsc.get(dim_map[dim], {}).get('ref', ''))[:60]
                divergences.append(d)
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
        items = r['result'].get('items', {})
        for dim in dims:
            key = dim_map[dim]
            if key not in items:
                raise ValueError(f'judge 缺少维度键: {key}')
            it = items[key]
            lv = _score_value(it.get('lv'), 'lv')
            if lv != 'N/A':
                j_stat[(dim, lv)] += 1
                if lv == 2:
                    f = {'id': cid, 'dim': dim,
                         'q': str(it.get('q', ''))[:120]}
                    if flip_with_ref:
                        f['ref'] = str(it.get('ref', ''))[:120]
                    j_flips.append(f)
            red = it.get('red', False)
            if type(red) is not bool:
                raise ValueError(f'red 必须为 bool，收到 {red!r}')
            if dim in new_dims and red:
                j_reds.append({'id': cid, 'dim': dim,
                               'q': str(it.get('q', ''))[:120]})
    j_tot = sum(j_stat.values())
    return j_stat, j_flips, j_reds, j_tot


def agreement_quality(review, judge, sample, dims, dim_map):
    """多数类一致率基线与 Cohen's κ；只使用双方都有数值的格子。"""
    pairs = []
    for cid in sample:
        if cid not in judge or 'result' not in judge[cid]:
            continue
        rsc = review[cid]['result']['scores']
        jsc = judge[cid]['result'].get('items', {})
        for dim in dims:
            rv = _score_value(rsc[dim]['s'], 's')
            key = dim_map[dim]
            if jsc and key not in jsc:
                raise ValueError(f'judge 缺少维度键: {key}')
            jv = _score_value(jsc[key]['lv'], 'lv') if key in jsc else None
            if rv in (0, 1, 2) and jv in (0, 1, 2):
                pairs.append((rv, jv))
    n = len(pairs)
    if not n:
        return {'n': 0, 'majority_baseline': None, 'kappa': None}
    rc = Counter(r for r, _ in pairs)
    jc = Counter(j for _, j in pairs)
    observed = sum(r == j for r, j in pairs) / n
    expected = sum(rc[v] * jc[v] for v in (0, 1, 2)) / (n * n)
    return {
        'n': n,
        'majority_baseline': max(rc.values()) / n,
        'kappa': (observed - expected) / (1 - expected) if expected != 1 else 0.0,
    }


def judge_acceptance(agree, tot, flip_recall_hit, flip_recall_tot, *, quality=None):
    """须高于多数类基线、κ>0，且有真实翻转样本供召回验证。"""
    agree_rate = agree / tot if tot else 0
    recall = flip_recall_hit / flip_recall_tot if flip_recall_tot else 0.0
    accept = bool(
        quality and flip_recall_tot and agree_rate >= 0.85 and recall >= 1.0
        and agree_rate > quality['majority_baseline'] and quality['kappa'] > 0)
    return agree_rate, recall, accept


# ================================================================ 4. 抽样

def stratification_key(rec):
    tier = (rec['engine_key'].get('caiming') or {}).get('tier_static') or 'NA'
    gm = (rec['engine_key'].get('guanming') or {}).get('is_guanming')
    return [tier, gm]


def stratified_fill(dump, forced, n, rng):
    """分层随机补足（tier_static × is_guanming），原 _n2_sample/_v3_sample 逐字下沉。

    forced 之外的案例按层打乱（rng 由调用方持 seed），按层大小降序轮转取满
    n - len(forced) 个；层全空提前终止。
    """
    if len(forced) > n:
        raise ValueError(f'强制集 {len(forced)} 超过样本上限 {n}')
    strata = defaultdict(list)
    for cid, rec in dump.items():
        if cid in forced:
            continue
        tier, gm = stratification_key(rec)
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

QIANYI_FORBID = _QIANYI_FORBID
XM_FORBID = _XIANGMAO_FORBID
GANZHI_RE = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')
_QIANYI_NOASSERT_RE = re.compile(r'(宜|适合|会|必有|主).{0,4}(迁移|远行)')


def engine_fe(c):
    """trainset 案例 → (compute_all 结果, build_payload 特征)。

    保留案例已有运岁；出生年缺失时保持缺失，不用 1960 伪造时间锚。
    """
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    input_data = {'gender': c.get('gender', '男')}
    if c.get('year') is not None:
        input_data['year'] = c['year']
    bazi_data = {'bazi': dict(c['bazi']), 'input': input_data}
    if c.get('dayun'):
        bazi_data['dayun'] = {'dayun': [{'gz': c['dayun']}]}
    if c.get('liunian'):
        entry = {'gz': c['liunian']}
        if c.get('year') is not None:
            entry['year'] = c['year']
        bazi_data['liunian'] = [entry]
    as_of = c.get('as_of')
    if as_of is None and c.get('as_of_year') is not None:
        as_of = f'{c["as_of_year"]}-07-01T00:00:00'
    res = MangpaiEngine(bazi_data, as_of=as_of).compute_all()
    return res, build_payload(res)


def engine_for_record(case, record=None):
    case = dict(case)
    if record:
        for key in ('as_of', 'as_of_year'):
            if record.get(key) is not None:
                case[key] = record[key]
    res, computed = engine_fe(case)
    return res, (record or {}).get('features') or computed


def seconds_to_valley(now=None):
    from mangpai.subjective.llm_backend import _BJT, _price_tier

    now = now or datetime.now(_BJT)
    now = now.replace(tzinfo=_BJT) if now.tzinfo is None else now.astimezone(_BJT)
    if _price_tier(now.timestamp()) == 'offpeak':
        return 0
    for hour in (12, 18):
        target = now.replace(hour=hour, minute=0, second=3, microsecond=0)
        if target > now:
            return int((target - now).total_seconds())
    target = (now + timedelta(days=1)).replace(hour=12, minute=0, second=3, microsecond=0)
    return int((target - now).total_seconds())


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
    """相貌维禁词直扫，排除窗与生产校验器一致。"""
    hits = []
    for w in XM_FORBID:
        for m in re.finditer(re.escape(w), text):
            i = m.start()
            if not _xiangmao_exempt(text, w, i):
                hits.append((w, text[max(0, i - 1):i + len(w) + 1]))
    return hits


def qianyi_honest_nosignal(text):
    """迁移无信号须使用明确模板，且不得另给出境或迁居断言。"""
    if '无迁移信号' not in text and '没有迁移信号' not in text:
        return False
    assertions = QIANYI_FORBID + ('迁居', '外出', '离开')
    return not _QIANYI_NOASSERT_RE.search(text) \
        and not any(w in text for w in assertions)


def xiangmao_honest_nosignal(text):
    return '无显著相貌特征' in text
