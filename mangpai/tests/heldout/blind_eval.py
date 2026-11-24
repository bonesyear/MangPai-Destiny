# -*- coding: utf-8 -*-
"""V3/M1 历史 heldout/开发集评估器 — 规则改动前后对比。

对 heldout/cases.yaml（215例）与 trainset/cases.yaml（294例）运行引擎并按
固定 rubric 给官命/财命/职业打分。历史 heldout 已参与开发，不再称盲测；
快照只作回归和开发参考，不作为未见数据准确率证明。

评分口径（全部继承 calib_assertions 训练侧 rubric，机械套用，不逐例调参）：
  官命: verdict 是/否 <-> is_guanming，符 ✅ 不符 ❌。
  财命: 正向(巨富/富/小康/平/贫) tier 等级差0✅差1⚠️差>=2❌，有凶向标记直接❌；
        破财=凶向标记或tier贫✅，小康⚠️，余❌；凶=凶向标记✅，贫⚠️，余❌。
        （平 按 小康 档计；凶向标记=summary 含 破财/比劫夺财/坐牢/牢狱/官非/下浮封顶/凶向）
  职业: verdict 关键词 -> 职业桶集合（粗口径，见 _ZY_RULES）；primary 命中 ✅，
        空(无明确倾向) ⚠️，其余 ❌；无法映射的 verdict（官员/农民/无业等）
        记 unscorable 不入准确率，但入翻转明细。

用法:
  python3 blind_eval.py --out <DIAG_DIR>/after.json            # 评估当前引擎
  python3 blind_eval.py --out <DIAG_DIR>/after.json --trainset-only
  python3 blind_eval.py --diff <DIAG_DIR>/before.json <DIAG_DIR>/after.json   # 前后对比报告
  python3 blind_eval.py --out snapshots/YYYYMMDD_x.json --baseline latest
  #   ↑ M5：评估+存快照（附 _meta: git sha/rubric 版本）并与基线快照 diff 一条龙；
  #   latest = snapshots/LATEST 指针指向的当前基线（见 snapshots/README.md）
  # 确定性门禁（M1）: PYTHONHASHSEED=0 与默认 seed 各跑一次，输出须逐字节一致；
  #   diff/基线报告末尾「文本抖动」段 >0 即卫生失败。
  # 显著性门禁（M3）: 汇总行后附 Wilson 95% CI（acc±half/下界）；--diff 报告附
  #   显著性判定——|Δacc| > 两 CI 半宽之和 方判显著改善/退化，余记「噪声带内」；
  #   验收门槛以 CI 下界计（如「财命 CI 下界 ≥ X%」）。纯附加输出，既有行不变。
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from math import comb
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO, os.path.dirname(_HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml

from _atomic_io import atomic_write_json

from mangpai import MangpaiEngine
from mangpai.objective.bazi_calc import GAN, ZHI

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
# v10：运锚层级断语只在文本干支锚等于案例所喂运岁时评 delta 轨；
# 不再读取原局档与金标的差距选轨，避免同一输出因标准答案不同而择优。
# v7（K3 294批1·B3）：破财/凶断语一律评全量轨（tier/summary）——「凶向
# 在档」强制标注仅写全量轨（caiming.py P0-a 防静态轨误杀设计），静态轨
# 对破财/凶断语结构性不可见其应得凶向（gj-财党杀攻身：引擎已正确检出
# 财生杀攻身 severe，静态轨按设计不可见致凶漏判❌）。无岁运时 tier 与
# tier_static 同值（level/level_static 仅岁运反局分叉），改动对破财/凶
# 单调：has_xiong 只增不减、档位不变，无 ✅/⚠️ 回退风险；层级断语判轨
# 不变（v10 运锚规则照旧）。
# v8（K3 294职业批1·B-a）：_ZY_EXCLUDE['military'] 增「冠军」——体育冠军
# 之「军」为 substring 误命中（cj-运动员「网球冠军」/cj-武术「武术全国
# 冠军」，段氏：体育冠军=比劫做功，同 v4 删「武/兵」之理），2 例转
# unscorable（trainset 职业 n 87→85）；两例 verdict 无其他桶关键词，
# 22✅ 零依赖被排除语境。
# v9：新增 driver=司机/运输/开车；zhenbao-04 转✅，ans29 领导司机如实转❌。
RUBRIC_VERSION = 'v10-20261118'

# P0-a 断语性质判别：流年事件断语（破财/凶 且 文本锚定具体年份/大运 或 案例
# 喂入运岁——金标准多为「戊辰年破财/赔六万」式流年事件，案例所喂运岁即事件锚点）
# 评含岁运 delta 的字段（tier/summary）；层级断语一律评原局轨字段
# （tier_static/summary_static），岁运反局 artifact 不再压原局档位。
_EVENT_RE = re.compile(
    r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥][年运]|\d{2,4}\s*年')
# v6 运锚提取：断语文本中的「干支+年/运」锚点（供与所喂运岁比对）
_GZ_ANCHOR_RE = re.compile(
    r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])[年运]')

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
    (('司机', '运输', '开车'), 'driver'),
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
    'military': ('参军', '冠军'),
}


def _yunshi_gz(gz, label):
    if len(gz) == 1:
        if gz in GAN:
            return gz, ''
        if gz in ZHI:
            return '', gz
    elif len(gz) == 2 and gz[0] in GAN and gz[1] in ZHI:
        if (GAN.index(gz[0]) - ZHI.index(gz[1])) % 2 == 0:
            return gz[0], gz[1]
    raise ValueError(f'{label}非法或阴阳不配: {gz!r}')


def _bazi_data(c):
    b = c['bazi']
    bazi_data = {
        'bazi': dict(b), 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': c.get('gender', '男')},
    }
    if c.get('year') is not None:
        bazi_data['input']['year'] = c['year']
    dy = c.get('dayun')
    if dy:
        gan, zhi = _yunshi_gz(dy, '大运')
        entry = {'gz': dy, 'start_age': 5}
        if gan:
            entry['gan'] = gan
        if zhi:
            entry['zhi'] = zhi
        bazi_data['dayun'] = {'direction': '顺', 'start_age': 5,
                              'dayun': [entry]}
    ln = c.get('liunian')
    if ln:
        _yunshi_gz(ln, '流年')
        entry = {'gz': ln}
        if c.get('year') is not None:
            entry['year'] = c['year']
        bazi_data['liunian'] = [entry]
    return bazi_data


def score_guanming(verdict, gm):
    expect = verdict.startswith('是')
    got = bool(gm.get('is_guanming'))
    return ('✅' if got == expect else '❌'), got


def score_caiming(verdict, cm, has_yunsui=False, dayun='', liunian=''):
    d = verdict.split('·')[0].split('/')[0].split('，')[0].strip()
    d_rank = '小康' if d == '平' else d
    # P0-a：流年事件断语（破财/凶）一律用含 delta 全量轨字段（v7：凶向在档
    # 标注仅全量轨可见，无岁运时 tier 与静态同值、改动单调）；层级断语
    # （巨富/富/小康/平/贫）一律原局轨；v10 仅在断语干支锚=所喂运岁时改评 delta 轨
    is_event = d in ('破财', '凶')
    if not is_event and d_rank in _TIER_RANK:
        anchors = set(_GZ_ANCHOR_RE.findall(verdict))
        fed = {dayun, liunian} - {''}
        if anchors & fed:
            is_event = True  # v10：只看断语锚点，不看金标与原局档位的距离
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


_EXPECTED_CASE_COUNTS = {'heldout': 214, 'trainset': 295}


def eval_cases(path):
    cases = yaml.safe_load(open(path, encoding='utf-8'))
    split = os.path.basename(os.path.dirname(path))
    expected = _EXPECTED_CASE_COUNTS.get(split)
    if expected is not None and len(cases or []) != expected:
        raise ValueError(f'{split} 例数异常: {len(cases or [])}，预期 {expected}')
    out = {}
    for c in cases:
        cid = c['id']
        verdicts = c.get('verdicts') or {}
        entry = {'verdict_labels': {}, 'scores': {}, 'engine': {}}
        try:
            res = MangpaiEngine(_bazi_data(c)).compute_all()
        except Exception as e:
            # H-fix-2c：引擎异常不静默——记 case id + 入快照 error 字段，
            # main() 收尾按 error 计数非零退出（验证可信度 > 单例容错，防假 green）
            entry['error'] = repr(e)
            out[cid] = entry
            print(f'!! {cid} 引擎异常: {e!r}')
            continue
        gm, cm, zy = res.get('guanming', {}), res.get('caiming', {}), res.get('zhiye', {})
        entry['engine_sha256'] = _engine_hash(res)
        if '官命' in verdicts:
            s, got = score_guanming(verdicts['官命'], gm)
            entry['scores']['官命'] = s
            entry['engine']['is_guanming'] = got
            entry['verdict_labels']['官命'] = verdicts['官命']
        if '财命' in verdicts:
            s, tier = score_caiming(verdicts['财命'], cm,
                                    has_yunsui=bool(c.get('dayun') or c.get('liunian')),
                                    dayun=c.get('dayun', ''), liunian=c.get('liunian', ''))
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
        if dim == '官命':
            rows = [e for e in data.values()
                    if '官命' in e.get('scores', {})
                    and '官命' in (e.get('verdict_labels') or {})]
            if rows:
                gold = [e['verdict_labels']['官命'].startswith('是') for e in rows]
                pred = [bool((e.get('engine') or {}).get('is_guanming')) for e in rows]
                tp = sum(g and p for g, p in zip(gold, pred))
                fn = sum(g and not p for g, p in zip(gold, pred))
                fp = sum(not g and p for g, p in zip(gold, pred))
                tn = sum(not g and not p for g, p in zip(gold, pred))
                baseline = max(sum(gold), len(gold) - sum(gold)) / len(gold)
                specificity = tn / (tn + fp) if tn + fp else None
                sensitivity = tp / (tp + fn) if tp + fn else None
                stats[dim].update({
                    'majority_baseline': round(baseline, 4),
                    'acc_minus_baseline': round(ok / n - baseline, 4),
                    'confusion': {'TP': tp, 'FN': fn, 'FP': fp, 'TN': tn},
                    'specificity': round(specificity, 4) if specificity is not None else None,
                    'balanced_accuracy': round((sensitivity + specificity) / 2, 4)
                    if sensitivity is not None and specificity is not None else None,
                })
    return stats


_ORDER = {'✅': 0, '⚠️': 1, '❌': 2}


# ── M5 快照工具：_meta（git sha/rubric 版本/备注）溯源，加载时剥离 ──
def _json_hash_default(value):
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    return str(value)


def _engine_hash(result):
    content = json.dumps(result, ensure_ascii=False, sort_keys=True,
                         default=_json_hash_default)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _worktree_meta():
    import subprocess
    try:
        r = subprocess.run(['git', 'status', '--porcelain'], cwd=_REPO,
                           capture_output=True, text=True)
        dirty = bool(r.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        dirty = False
    digest = hashlib.sha256()
    for root in ('mangpai', 'foundation'):
        for path in sorted(Path(_REPO, root).rglob('*')):
            if not path.is_file() or path.suffix not in ('.py', '.yaml', '.sh'):
                continue
            if any(part in ('__pycache__', '.pytest_cache', 'snapshots', 'archive')
                   for part in path.parts):
                continue
            digest.update(str(path.relative_to(_REPO)).encode('utf-8'))
            digest.update(path.read_bytes())
    return {'dirty': dirty, 'tree_hash': digest.hexdigest()}


def _git_sha():
    import subprocess
    try:
        r = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, cwd=_REPO)
        return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        # 白名单（H-fix-2c）：git 不可用等环境降级，与引擎无关
        return ''


def _resolve_snapshot_path(path):
    """H-fix-8：`latest` 或 LATEST 指针文件 → 指针指向的快照路径。

    指针 = snapshots/LATEST 纯文本单行（快照文件名），指向当前基线快照；
    推进基线 = 人工改写指针（刻意不随 --out 自动更新，防误推基线）。
    """
    base = os.path.basename(path.rstrip('/'))
    if path != 'latest' and base != 'LATEST':
        return path
    ptr = os.path.join(_HERE, 'snapshots', 'LATEST') if path == 'latest' else path
    with open(ptr, encoding='utf-8') as f:
        name = f.read().strip()
    return os.path.join(os.path.dirname(os.path.abspath(ptr)), name)


def _load_snapshot(path):
    """读快照并剥离 _meta（meta 仅溯源，不参与 summarize/diff/rescore）。"""
    with open(_resolve_snapshot_path(path), encoding='utf-8') as f:
        data = json.load(f)
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


# ── M3 Wilson 95% CI（P3 测量卫生收尾）：汇总精度区间 + diff 显著性判定 ──
# 纯附加输出：既有汇总行/分组行逐字节不变，CI 行与显著性段为其后新增段落。
# 口径：Wilson score interval（z=1.96，无需 scipy）；--diff 时 |Δacc| 须大于
# 两 CI 半宽之和方判显著改善/退化，余记「噪声带内」；验收门槛以 CI 下界计。
# （注：同一批案例前后对比本属配对设计，两半宽和规则为约定阈，偏保守。）
_WILSON_Z = 1.959964


def _wilson(ok, n):
    """Wilson 95% score interval。返回 (lo, hi, half)；n=0 返回 None。"""
    if not n:
        return None
    p = ok / n
    z2 = _WILSON_Z * _WILSON_Z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    half = _WILSON_Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5) / denom
    return max(0.0, center - half), min(1.0, center + half), half


def _print_ci(label, data):
    """汇总行后附 CI 行：acc%±half%（下界 lo%），n=0 维度跳过。"""
    s = summarize(data)
    parts = []
    for d in ('官命', '财命', '职业'):
        v = s.get(d)
        if not v or not v['n']:
            continue
        lo, _hi, half = _wilson(v['✅'], v['n'])
        parts.append(f"{d}: {v['✅'] / v['n'] * 100:.1f}%±{half * 100:.1f}%"
                     f"(下界{lo * 100:.1f}%)")
    if parts:
        print(f'[{label}·CI95] ' + '  '.join(parts))
    gm = s.get('官命') or {}
    if gm.get('majority_baseline') is not None:
        cf = gm['confusion']
        spec = f"{gm['specificity']:.2%}" if gm['specificity'] is not None else 'NA'
        bal = (f"{gm['balanced_accuracy']:.2%}"
               if gm['balanced_accuracy'] is not None else 'NA')
        print(f"[{label}·官命基线] 多数类={gm['majority_baseline']:.2%} "
              f"准确率-基线={gm['acc_minus_baseline']:+.2%} "
              f"TP/FN/FP/TN={cf['TP']}/{cf['FN']}/{cf['FP']}/{cf['TN']} "
              f"特异度={spec} 平衡准确率={bal}")


def _print_significance(before, after):
    """--diff 显著性：同案例配对 McNemar 精确检验；Wilson 仅用于汇总展示。"""
    print('\n=== M3 显著性（配对 McNemar 精确检验，α=0.05）===')
    for split in ('heldout', 'trainset'):
        sb, sa = summarize(before.get(split, {})), summarize(after.get(split, {}))
        for d in ('官命', '财命', '职业'):
            vb, va = sb.get(d), sa.get(d)
            if not vb or not va or not vb['n'] or not va['n']:
                continue
            changes = [f for f in diff(before.get(split, {}), after.get(split, {}))
                       if f['dim'] == d and f['delta'] is not None]
            lost = sum(f['delta'] > 0 for f in changes)
            gained = sum(f['delta'] < 0 for f in changes)
            n = lost + gained
            p_value = min(1.0, 2 * sum(comb(n, i) for i in range(min(lost, gained) + 1)) / 2 ** n) if n else 1.0
            verdict = '噪声带内'
            if p_value < 0.05 and lost != gained:
                verdict = '显著退化' if lost > gained else '显著改善'
            delta = va['✅'] / va['n'] - vb['✅'] / vb['n']
            print(f'  [{split}][{d}] Δ={delta * 100:+.1f}% '
                  f'lost={lost} gained={gained} p={p_value:.4f} → {verdict}')


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
        hb, ha = b.get('engine_sha256'), a.get('engine_sha256')
        if hb and ha:
            if hb != ha:
                out.append((cid, ['engine_sha256'], eb, ea))
            continue
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
            _print_ci(f'{name}][{split}', data.get(split, {}))
    _print_significance(before, after)
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


def _diff_gate(before, after):
    regressions = 0
    for split in ('heldout', 'trainset'):
        regressions += sum(
            1 for f in diff(before.get(split, {}), after.get(split, {}))
            if f['delta'] is not None and f['delta'] > 0)
    jitter = sum(len(_jitter(before.get(split, {}), after.get(split, {})))
                 for split in ('heldout', 'trainset'))
    return regressions, jitter


def _validate_snapshot(payload):
    """快照写入前校验（H-fix-3）：_meta 溯源字段在场 + 至少一个 split 非空。"""
    meta = payload.get('_meta') or {}
    for key in ('git_sha', 'rubric_version', 'note'):
        if not meta.get(key):
            raise ValueError(f'快照缺 _meta.{key}，拒绝写入')
    splits = [k for k in payload if k != '_meta' and payload[k]]
    if not splits:
        raise ValueError('快照无任何 split 数据，拒绝写入')


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
                    help='评估完成后与该基线快照做 diff（M5：snapshots/ 内最新基线；'
                         'H-fix-8 起支持 latest 或 snapshots/LATEST 指针）')
    ap.add_argument('--note', default='',
                    help='写入快照 _meta 的备注（如验证状态），防拿错基线')
    args = ap.parse_args()

    if args.rescore:
        with open(args.rescore, encoding='utf-8') as f:
            data = json.load(f)
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
        out_path = args.out or datetime.now().strftime('%Y%m%d_rescore.json')
        meta = data.setdefault('_meta', {})
        meta['git_sha'] = _git_sha()
        meta['zhiye_rubric_version'] = RUBRIC_VERSION
        meta['note'] = args.note or (meta.get('note', '') + ' 职业rubric重评').strip()
        meta.update(_worktree_meta())
        atomic_write_json(out_path, data, validate=_validate_snapshot, backup=True)
        for split, cases in data.items():
            if split == '_meta':
                continue
            s = summarize(cases)
            line = '  '.join(
                f"{d}: {v['✅']}✅/{v['⚠️']}⚠️/{v['❌']}❌ acc={v['acc']}"
                for d, v in s.items() if v['n'])
            print(f'[{split}·重评] {line}')
            _print_ci(f'{split}·重评', cases)
        print(f'(saved -> {out_path})')
        return

    if args.diff:
        before, mb = _load_snapshot(args.diff[0])
        after, ma = _load_snapshot(args.diff[1])
        _print_meta('BEFORE', mb)
        _print_meta('AFTER', ma)
        _print_diff(before, after)
        regressions, jitter = _diff_gate(before, after)
        if regressions or jitter:
            print(f'门禁失败：计分退化={regressions}，文本抖动={jitter}')
            sys.exit(1)
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
        _print_ci(split, data)
    if args.out:
        payload = dict(result)
        payload['_meta'] = {'git_sha': _git_sha(),
                            'rubric_version': RUBRIC_VERSION,
                            'note': args.note,
                            **_worktree_meta()}
        # H-fix-3：快照原子写 + 写入前校验（_meta 溯源字段须在场）
        atomic_write_json(args.out, payload, validate=_validate_snapshot)
        print(f'(saved -> {args.out})')
    if args.baseline:
        before, mb = _load_snapshot(args.baseline)
        _print_meta('baseline', mb)
        print(f'\n=== vs 基线 {args.baseline} ===')
        _print_diff(before, result)
        regressions, jitter = _diff_gate(before, result)
        if regressions or jitter:
            print(f'门禁失败：计分退化={regressions}，文本抖动={jitter}')
            sys.exit(1)
    # H-fix-2c：引擎异常计数 >0 → 验证不可信，退出码 1（快照/diff 照常产出供诊断）
    n_err = sum(1 for data in result.values() for e in data.values() if 'error' in e)
    if n_err:
        print(f'!! 引擎异常 {n_err} 例（见输出 error 字段）——验证结果不可信')
        sys.exit(1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
