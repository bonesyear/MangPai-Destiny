# -*- coding: utf-8 -*-
"""V3/M1 留出集盲测评估器 — 方向层（yongshen R2/R3）改动前后对比专用。

⚠️ 本脚本只做评估：对 heldout/cases.yaml（215例）与 trainset/cases.yaml（23例）
跑 MangpaiEngine.compute_all()，按机械化 rubric 给 官命/财命/职业 三维打分，
输出 JSON 供前后快照 diff。评估结果不得用于修引擎（留出集铁律）。

评分口径（全部继承 calib_assertions 训练侧 rubric，机械套用，不逐例调参）：
  官命: verdict 是/否 <-> is_guanming，符 ✅ 不符 ❌。
  财命: 正向(巨富/富/小康/平/贫) tier 等级差0✅差1⚠️差>=2❌，有凶向标记直接❌；
        破财=凶向标记或tier贫✅，小康⚠️，余❌；凶=凶向标记✅，贫⚠️，余❌。
        （平 按 小康 档计；凶向标记=summary 含 破财/比劫夺财/坐牢/牢狱/官非/下浮封顶/凶向）
  职业: verdict 关键词 -> 职业桶集合（粗口径，见 _ZY_RULES）；primary 命中 ✅，
        空(无明确倾向) ⚠️，其余 ❌；无法映射的 verdict（官员/农民/无业等）
        记 unscorable 不入准确率，但入翻转明细。

用法:
  python3 blind_eval.py --out /tmp/after.json            # 评估当前引擎
  python3 blind_eval.py --out /tmp/after.json --trainset-only
  python3 blind_eval.py --diff /tmp/before.json /tmp/after.json   # 前后对比报告
  python3 blind_eval.py --out snapshots/YYYYMMDD_x.json --baseline snapshots/上一批.json
  #   ↑ M5：评估+存快照（附 _meta: git sha/rubric 版本）并与基线快照 diff 一条龙
  # 确定性门禁（M1）: PYTHONHASHSEED=0 与默认 seed 各跑一次，输出须逐字节一致；
  #   diff/基线报告末尾「文本抖动」段 >0 即卫生失败。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml

from mangpai import MangpaiEngine

_XIONG_MARKERS = ['破财', '比劫夺财', '坐牢', '牢狱', '官非', '下浮封顶', '凶向']
_TIER_RANK = {'贫': 0, '小康': 1, '富': 2, '巨富': 3}
# rubric 口径版本（P3-M4：任何口径改动须走 --rescore 重设基线并写 CHANGELOG）。
# v2（Group X 修复）：层级断语 tier 差0（档位已正确）时，不再因 summary 附带的
# 凶向词（破财/下浮封顶等）直杀❌——tier 正确即说明引擎定档无误，summary 附加的
# 凶向标记与档位语义一致时原「凶向一律❌」为过杀（li101 穷命型：tier 对、语义对、
# 仅因「下浮封顶」记❌）。diff>=1 或档位无法解析时，凶向直杀口径不变。
# v3（K3 批A 凶向在档标注配套）：_XIONG_MARKERS 增「凶向」——引擎全量轨新增
# 「凶向在档（…）」强制标注（capped=False 也写理由，仅全量轨），破财/凶断语
# 凭该标注识别凶向；层级断语走静态轨不受影响。
# v4（K3 批A+B·M4 粗口径收窄）：military 桶关键词删 武/兵/保安/保卫——
# 「武」命中武侠/武职泛文、「兵」命中当兵经历（qi49 安全局：gold 官员，
# 「当兵转…」为履历非现职）、保卫/保安命中行政岗（ans05 医院保卫科长=
# 官员非军警），均为粗口径假阳性；zhenbao-12（军阀·武职）凭「军阀」仍
# 命中，无金标依赖被删词。被删词案例转 unscorable（不入准确率）。
# v5（K3 批12·M4 粗口径二轮）：新增 _ZY_EXCLUDE 语境排除——performer 桶
# 在 色情业/歌厅/舞厅/歌女 语境下命中作废（段氏：歌厅小姐/歌女=食伤桃花
# 无工作贱命，属色情业非演艺；li263/qi20「色情业·歌厅小姐」、qi41
# 「色情业·歌舞厅歌女」gold 皆色情业，桶体系无此桶 → 转 unscorable，
# 同 v4 被删词处理）；military 桶在 参军 语境下命中作废（履历非现职，
# 同 v4 删「兵」之理：qi29「农民·曾参军逃出」gold 农民）。歌星/舞蹈家/
# 将军/军阀等正当命中不受影响（逐例核对 22✅ 零依赖被排除语境）。
RUBRIC_VERSION = 'v5-20260802'

# P0-a 断语性质判别：流年事件断语（破财/凶 且 文本锚定具体年份/大运 或 案例
# 喂入运岁——金标准多为「戊辰年破财/赔六万」式流年事件，案例所喂运岁即事件锚点）
# 评含岁运 delta 的字段（tier/summary）；层级断语一律评原局轨字段
# （tier_static/summary_static），岁运反局 artifact 不再压原局档位。
_EVENT_RE = re.compile(
    r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥][年运]|\d{2,4}\s*年')

# 职业 verdict 关键词 -> 职业桶（粗口径；多组命中取并集）
_ZY_RULES = [
    (('军', '警', '公安', '部队', '军阀'), 'military'),
    (('公检法', '律师', '法官', '检察', '司法', '法院'), 'lawyer'),
    (('教师', '老师', '教育', '文化', '作家', '编辑', '记者', '文秘', '书画',
      '画家', '文员', '教授'), 'teacher'),
    (('医生', '医疗', '中医', '西医'), 'doctor'),
    (('会计', '财会', '财务', '银行', '出纳'), 'accountant'),
    (('商', '企业家', '炒股', '房地产', '生意', '贸易', '销售', '老板',
      '博彩', '理财', '经商', '个体'), 'merchant'),
    (('演员', '演艺', '艺术', '体育', '歌', '舞', '艺人'), 'performer'),
    # M2 基础职业类目（段氏《中级》体力取财=农民/民工阶层；无业=清家荡产/无功）。
    # 原先无法机械映射的 农民/工人/无业 verdict 自此可评。
    (('农民', '务农', '种地', '种田', '工人', '打工', '民工', '体力'), 'laborer'),
    (('无业', '讨饭', '乞丐', '无正当职业'), 'unemployed'),
]

# v5 语境排除：verdict 含下列语境词时，对应桶整桶命中作废（误命中抑制，
# 逐例依据见 RUBRIC_VERSION v5 注）。粗粒度=verdict 级，语境内无正当共存例。
_ZY_EXCLUDE = {
    'performer': ('色情业', '歌厅', '舞厅', '歌女'),
    'military': ('参军',),
}


def _bazi_data(c):
    b = c['bazi']
    bazi_data = {
        'bazi': dict(b), 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': c.get('gender', '男'), 'year': c.get('year', 1960)},
    }
    dy = c.get('dayun')
    if dy:
        # 金标准大运为「干支」或仅「支」（如 qi02 亥运）：支-only 时补 'zhi' 键，
        # 使 yunfan 等消费方（gz 不足两位回退 gan/zhi 键）仍能吃到该运。
        entry = {'gz': dy, 'start_age': 5}
        if len(dy) == 1:
            entry['zhi'] = dy
        bazi_data['dayun'] = {'direction': '顺', 'start_age': 5,
                              'dayun': [entry]}
    ln = c.get('liunian')
    if ln and len(ln) == 2:
        bazi_data['liunian'] = [{'gz': ln, 'year': c.get('year', 1960)}]
    return bazi_data


def score_guanming(verdict, gm):
    expect = verdict.startswith('是')
    got = bool(gm.get('is_guanming'))
    return ('✅' if got == expect else '❌'), got


def score_caiming(verdict, cm, has_yunsui=False):
    d = verdict.split('·')[0].split('/')[0].split('，')[0].strip()
    # P0-a：流年事件断语（破财/凶 带年/运锚或案例喂运岁）用含 delta 字段；
    # 层级断语（巨富/富/小康/平/贫）一律原局轨
    is_event = d in ('破财', '凶') and (has_yunsui or bool(_EVENT_RE.search(verdict)))
    if is_event:
        tier = cm.get('tier', '')
        summary = str(cm.get('summary', ''))
    else:
        tier = cm.get('tier_static') or cm.get('tier', '')
        summary = str(cm.get('summary_static') or cm.get('summary', ''))
    has_xiong = any(m in summary for m in _XIONG_MARKERS)
    if d == '平':
        d = '小康'
    if d in _TIER_RANK:
        if tier in _TIER_RANK:
            diff = abs(_TIER_RANK[tier] - _TIER_RANK[d])
            # Group X：tier 差0（档位已正确）不因 summary 附带凶向词杀分
            if diff == 0:
                return '✅', tier
            if has_xiong:
                return '❌', tier
            return ('⚠️' if diff == 1 else '❌'), tier
        if has_xiong:
            return '❌', tier
        return '⚠️', tier
    if d == '破财':
        if has_xiong or tier == '贫':
            return '✅', tier
        return ('⚠️' if tier == '小康' else '❌'), tier
    if d == '凶':
        if has_xiong:
            return '✅', tier
        return ('⚠️' if tier == '贫' else '❌'), tier
    return None, tier  # 无法解析的标签不计


def score_zhiye(verdict, zy):
    buckets = set()
    for kws, bucket in _ZY_RULES:
        if any(x in verdict for x in _ZY_EXCLUDE.get(bucket, ())):
            continue  # v5 语境排除：误命中语境下整桶作废（转 unscorable）
        if any(k in verdict for k in kws):
            buckets.add(bucket)
    primary = zy.get('primary', '') or ''
    if not buckets:
        return None, primary  # unscorable
    if primary in buckets:
        return '✅', primary
    if not primary:
        return '⚠️', primary
    return '❌', primary


def eval_cases(path):
    cases = yaml.safe_load(open(path, encoding='utf-8'))
    out = {}
    for c in cases:
        cid = c['id']
        verdicts = c.get('verdicts') or {}
        entry = {'verdict_labels': {}, 'scores': {}, 'engine': {}}
        try:
            res = MangpaiEngine(_bazi_data(c)).compute_all()
        except Exception as e:
            entry['error'] = repr(e)
            out[cid] = entry
            continue
        gm, cm, zy = res.get('guanming', {}), res.get('caiming', {}), res.get('zhiye', {})
        if '官命' in verdicts:
            s, got = score_guanming(verdicts['官命'], gm)
            entry['scores']['官命'] = s
            entry['engine']['is_guanming'] = got
            entry['verdict_labels']['官命'] = verdicts['官命']
        if '财命' in verdicts:
            s, tier = score_caiming(verdicts['财命'], cm,
                                    has_yunsui=bool(c.get('dayun') or c.get('liunian')))
            entry['engine']['tier'] = tier
            entry['engine']['tier_static'] = cm.get('tier_static', '')
            entry['verdict_labels']['财命'] = verdicts['财命']
            if s:
                entry['scores']['财命'] = s
        if '职业' in verdicts:
            s, primary = score_zhiye(verdicts['职业'], zy)
            entry['engine']['zhiye_primary'] = primary
            entry['engine']['zhiye_label'] = zy.get('primary_label', '')
            entry['verdict_labels']['职业'] = verdicts['职业']
            if s:
                entry['scores']['职业'] = s
        # 方向层诊断（R2/R3 命中情况，供报告统计，不参与打分）
        ds = (cm.get('level', {}) or {})
        gmr = gm.get('veto_reasons') or []
        entry['engine']['veto_reasons'] = gmr
        entry['engine']['caiming_adjust'] = ds.get('adjust', '')
        out[cid] = entry
    return out


def summarize(data):
    stats = {}
    for dim in ('官命', '财命', '职业'):
        c = Counter()
        for e in data.values():
            if dim in e.get('scores', {}):
                c[e['scores'][dim]] += 1
        n = sum(c.values())
        ok = c.get('✅', 0)
        stats[dim] = {'n': n, '✅': ok, '⚠️': c.get('⚠️', 0), '❌': c.get('❌', 0),
                      'acc': round(ok / n, 4) if n else None}
    return stats


_ORDER = {'✅': 0, '⚠️': 1, '❌': 2}


# ── M5 快照工具：_meta（git sha/rubric 版本/备注）溯源，加载时剥离 ──
def _git_sha():
    try:
        import subprocess
        r = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, cwd=_REPO)
        return r.stdout.strip()
    except Exception:
        return ''


def _load_snapshot(path):
    """读快照并剥离 _meta（meta 仅溯源，不参与 summarize/diff/rescore）。"""
    data = json.load(open(path, encoding='utf-8'))
    return data, data.pop('_meta', None)


def _print_meta(tag, m):
    if m:
        print(f"[{tag}·meta] git={m.get('git_sha', '')} "
              f"rubric={m.get('rubric_version', '')} {m.get('note', '')}")


# ── M2 分组门禁：财命按 verdict 首词分组（口径同 score_caiming 的 d 解析）──
_GROUP_ORDER = ['巨富', '富', '小康', '平', '贫', '破财', '凶']


def summarize_groups(data):
    groups = {}
    for e in data.values():
        v = (e.get('verdict_labels') or {}).get('财命')
        s = (e.get('scores') or {}).get('财命')
        if v is None or s is None:
            continue
        g = v.split('·')[0].split('/')[0].split('，')[0].strip()
        groups.setdefault(g, Counter())[s] += 1
    return {g: {'n': sum(c.values()), '✅': c.get('✅', 0), '⚠️': c.get('⚠️', 0),
                '❌': c.get('❌', 0),
                'acc': round(c.get('✅', 0) / sum(c.values()), 4)}
            for g, c in groups.items()}


def _print_groups(label, data):
    g = summarize_groups(data)
    if not g:
        return
    keys = [k for k in _GROUP_ORDER if k in g] + sorted(
        k for k in g if k not in _GROUP_ORDER)
    print(f'[{label}·财命分组] ' + '  '.join(
        f"{k} n={g[k]['n']} {g[k]['✅']}✅/{g[k]['⚠️']}⚠️/{g[k]['❌']}❌ acc={g[k]['acc']}"
        for k in keys))


# ── M1 文本抖动：score 全不变但 engine 字段有差异（复跑确定性门禁，>0 即失败）──
def _jitter(before, after):
    out = []
    for cid in sorted(set(before) | set(after)):
        if cid not in before or cid not in after:
            continue  # 单边缺失=新增/移除案例，非文本抖动（非对称快照对比 artifact）
        b, a = before.get(cid, {}), after.get(cid, {})
        if (b.get('scores') or {}) != (a.get('scores') or {}):
            continue
        eb, ea = b.get('engine') or {}, a.get('engine') or {}
        if eb == ea:
            continue
        keys = sorted(k for k in set(eb) | set(ea) if eb.get(k) != ea.get(k))
        out.append((cid, keys, eb, ea))
    return out


def _print_diff(before, after):
    for name, data in (('BEFORE', before), ('AFTER', after)):
        for split in ('heldout', 'trainset'):
            s = summarize(data.get(split, {}))
            line = '  '.join(
                f"{d}: {v['✅']}✅/{v['⚠️']}⚠️/{v['❌']}❌ acc={v['acc']}"
                for d, v in s.items() if v['n'])
            print(f'[{name}][{split}] {line}')
            _print_groups(f'{name}][{split}', data.get(split, {}))
    print('\n=== 翻转明细（heldout + trainset）===')
    for split in ('heldout', 'trainset'):
        flips = diff(before.get(split, {}), after.get(split, {}))
        print(f'\n--- {split}: {len(flips)} 条翻转 ---')
        for f in flips:
            arrow = {1: '↓变差', 2: '↓↓变差', -1: '↑改善', -2: '↑↑改善'}.get(
                f['delta'], '·换档')
            print(f"  [{f['dim']}] {f['id']}  断语={f['verdict'][:40]}  "
                  f"引擎:{f['engine']}  打分:{f['score']} {arrow}")
    print('\n=== 文本抖动（score 不变但 engine 字段变；>0 即卫生失败）===')
    total = 0
    for split in ('heldout', 'trainset'):
        jit = _jitter(before.get(split, {}), after.get(split, {}))
        total += len(jit)
        print(f'--- {split}: {len(jit)} 条 ---')
        for cid, keys, eb, ea in jit:
            print(f'  {cid} 字段={keys}')
            for k in keys:
                print(f'    {k}: {str(eb.get(k))[:60]} -> {str(ea.get(k))[:60]}')
    print(f'文本抖动合计: {total}')


def diff(before, after):
    """前后快照对比：翻转明细（打分变化 + 引擎裸值变化）。"""
    flips = []
    for cid in sorted(set(before) | set(after)):
        b, a = before.get(cid, {}), after.get(cid, {})
        for dim in ('官命', '财命', '职业'):
            sb = (b.get('scores') or {}).get(dim)
            sa = (a.get('scores') or {}).get(dim)
            eb = (b.get('engine') or {})
            ea = (a.get('engine') or {})
            raw_key = {'官命': 'is_guanming', '财命': 'tier',
                       '职业': 'zhiye_label'}[dim]
            vb, va = eb.get(raw_key), ea.get(raw_key)
            if sb != sa or vb != va:
                # delta 口径同 regression67：_ORDER ✅0/⚠️1/❌2，sa-sb>0 = 变差（回归）
                flips.append({
                    'id': cid, 'dim': dim,
                    'verdict': (a.get('verdict_labels') or b.get('verdict_labels') or {}).get(dim, ''),
                    'score': f'{sb}->{sa}',
                    'engine': f'{vb}->{va}',
                    'delta': (_ORDER.get(sa, -1) - _ORDER.get(sb, -1))
                             if sb and sa else None,
                })
    return flips


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', help='评估结果 JSON 输出路径')
    ap.add_argument('--trainset-only', action='store_true')
    ap.add_argument('--diff', nargs=2, metavar=('BEFORE', 'AFTER'),
                    help='对比两个评估快照并输出翻转报告')
    ap.add_argument('--rescore', metavar='SNAPSHOT',
                    help='用当前 _ZY_RULES 重评既有快照的职业维（rubric 扩展后重设基线用；'
                         '只依赖快照内 engine 裸值与断语，不重跑引擎）')
    ap.add_argument('--baseline', metavar='SNAPSHOT',
                    help='评估完成后与该基线快照做 diff（M5：snapshots/ 内最新基线）')
    ap.add_argument('--note', default='',
                    help='写入快照 _meta 的备注（如验证状态），防拿错基线')
    args = ap.parse_args()

    if args.rescore:
        data = json.load(open(args.rescore, encoding='utf-8'))
        for split, cases in data.items():
            if split == '_meta':
                continue
            for e in cases.values():
                v = (e.get('verdict_labels') or {}).get('职业')
                if v is None:
                    continue
                s, _p = score_zhiye(v, {'primary': (e.get('engine') or {}).get('zhiye_primary', '')})
                if s:
                    e.setdefault('scores', {})['职业'] = s
                else:
                    e.get('scores', {}).pop('职业', None)
        out_path = args.rescore.replace('.json', '') + '_rescore.json'
        json.dump(data, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        for split, cases in data.items():
            if split == '_meta':
                continue
            s = summarize(cases)
            line = '  '.join(
                f"{d}: {v['✅']}✅/{v['⚠️']}⚠️/{v['❌']}❌ acc={v['acc']}"
                for d, v in s.items() if v['n'])
            print(f'[{split}·重评] {line}')
        print(f'(saved -> {out_path})')
        return

    if args.diff:
        before, mb = _load_snapshot(args.diff[0])
        after, ma = _load_snapshot(args.diff[1])
        _print_meta('BEFORE', mb)
        _print_meta('AFTER', ma)
        _print_diff(before, after)
        return

    result = {}
    if not args.trainset_only:
        result['heldout'] = eval_cases(os.path.join(_HERE, 'cases.yaml'))
    result['trainset'] = eval_cases(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'))
    for split, data in result.items():
        s = summarize(data)
        line = '  '.join(
            f"{d}: {v['✅']}✅/{v['⚠️']}⚠️/{v['❌']}❌ acc={v['acc']}"
            for d, v in s.items() if v['n'])
        print(f'[{split}] n={len(data)}  {line}')
        _print_groups(split, data)
    if args.out:
        payload = dict(result)
        payload['_meta'] = {'git_sha': _git_sha(),
                            'rubric_version': RUBRIC_VERSION,
                            'note': args.note}
        json.dump(payload, open(args.out, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'(saved -> {args.out})')
    if args.baseline:
        before, mb = _load_snapshot(args.baseline)
        _print_meta('baseline', mb)
        print(f'\n=== vs 基线 {args.baseline} ===')
        _print_diff(before, result)


if __name__ == '__main__':
    main()
