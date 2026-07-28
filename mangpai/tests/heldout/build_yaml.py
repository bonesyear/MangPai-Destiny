# -*- coding: utf-8 -*-
"""V3/K1 构建 cases.yaml — merged.json × 人工标注表 → heldout/ + trainset/。

路由:
  contam=calib10  -> trainset/cases.yaml（金标准镜像 calib_assertions.yaml）
  contam=b67      -> trainset/cases.yaml（67例已用于修引擎，同源书例一并封存于训练侧）
  PHANTOM         -> 幻影性别，弃
  DROP            -> 无断语/纯理论/作业无答/六合彩等，弃（理由记录于 dropped.txt）
  KEPT            -> heldout/cases.yaml  ⚠️ 留出集 · 严禁用于修引擎
校验: 每个 merged 案例必须有归属；KEPT 键必须存在于 merged。
"""
import json, os, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from annotations_meta import CALIB10, B67, PHANTOM, DROP
from annotations_heldout import KEPT, MANUAL


def bazi_of(gans, zhis):
    return {'year': gans[0] + zhis[0], 'month': gans[1] + zhis[1],
            'day': gans[2] + zhis[2], 'hour': gans[3] + zhis[3]}


def entry(cid, name, c, ann):
    e = {'id': cid, 'name': name,
         'bazi': bazi_of(c['gans'], c['zhis'])}
    if ann.get('dy'):
        e['dayun'] = ann['dy']
    if ann.get('ln'):
        e['liunian'] = ann['ln']
    e['gender'] = c['gender']
    e['verdicts'] = ann['v']
    e['source'] = ';'.join(c['sources']) if isinstance(c['sources'], list) else c['sources']
    q = ann.get('q') or c.get('context', '')
    if ann.get('qs'):
        a, b = ann['qs']
        i, j = q.find(a), q.find(b)
        if i >= 0 and j > i:
            q = q[i:j + len(b)]
    e['raw_quote'] = q
    return e


def main():
    merged = json.load(open(os.path.join(HERE, 'merged.json'), encoding='utf-8'))
    bykey = {}
    for c in merged:
        k = '/'.join([''.join(c['gans']), ''.join(c['zhis']), c['gender']])
        bykey[k] = c
    train, held, dropped, unrouted = [], [], [], []
    used = set()
    for c in merged:
        k = '/'.join([''.join(c['gans']), ''.join(c['zhis']), c['gender']])
        tag = c.get('contam', '')
        if tag.startswith('calib10:'):
            cid = tag.split(':')[1]
            ann = CALIB10.get(k)
            assert ann, f'calib10 缺标注: {k}'
            train.append(entry(cid, ann['n'], c, ann)); used.add(k)
        elif tag.startswith('backtest67:'):
            ann = B67.get(k)
            assert ann, f'b67 缺标注: {k}'
            train.append(entry('b67-' + tag.split(':')[1], ann['n'], c, ann)); used.add(k)
        elif k in PHANTOM:
            dropped.append((k, '幻影性别')); used.add(k)
        elif k in DROP:
            dropped.append((k, DROP[k])); used.add(k)
        elif k in KEPT:
            used.add(k)  # 下面统一生成
        else:
            unrouted.append(k)
    # heldout: 按 source 排序生成
    held_keys = [k for k in bykey if k in KEPT and k not in
                 {kk for kk in PHANTOM} | set(DROP)]
    def sort_key(k):
        return bykey[k]['sources'][0]
    for k in sorted(set(held_keys), key=sort_key):
        c = bykey[k]
        ann = KEPT[k]
        cid = f"{c['sources'][0].split(':')[0]}-{ann['n'].split('-', 1)[-1]}"
        held.append(entry(cid, ann['n'], c, ann))
    # 手动补录
    for m in MANUAL:
        c = {'gans': list(m['gans']), 'zhis': list(m['zhis']), 'gender': m['gender'],
             'sources': [m['source']], 'context': m['q']}
        held.append(entry(m['id'], m['id'].split('-', 1)[-1], c,
                          {'v': m['v'], 'dy': m.get('dy'), 'ln': m.get('ln'), 'q': m['q']}))
    # 校验
    orphan_kept = [k for k in KEPT if k not in bykey]
    for k in orphan_kept:
        print(f'⚠️ KEPT 键不在 merged: {k}')
    for k in unrouted:
        c = bykey[k]
        print(f'⚠️ 未路由: {k} {c["sources"]} {c["context"][:60]!r}')
    if orphan_kept or unrouted:
        print('存在未决项，中止。'); sys.exit(1)
    # 写 YAML
    head_h = ('# ⚠️ 留出集 · 严禁用于修引擎 ⚠️\n'
              '# V3/K1 郝金阳/段建业断例留出集 — 仅供引擎评估，任何引擎修改不得参考本文件断语。\n'
              '# 来源: shouke-jiaocheng.txt(授课教程) + mingli-zhenbao-50qi.txt(50期资料)\n'
              '# 提取: extract_cases.py -> curate.py -> 人工逐例审定(annotations_*.py) -> build_yaml.py\n'
              '# verdicts 仅标注明文断语维度；raw_quote 为原文逐字摘录。\n')
    head_t = ('# 训练侧案例集（已用于校准/修引擎，可安全使用）\n'
              '# calib10 = calib_assertions.yaml 金标准10例的简单格式镜像；\n'
              '# b67-*  = regression67.py 67例中出自这两本书的书例（已用于修引擎）。\n')
    with open(os.path.join(HERE, 'cases.yaml'), 'w', encoding='utf-8') as f:
        f.write(head_h)
        yaml.dump(held, f, allow_unicode=True, sort_keys=False, width=120)
    tdir = os.path.join(HERE, '..', 'trainset')
    os.makedirs(tdir, exist_ok=True)
    with open(os.path.join(tdir, 'cases.yaml'), 'w', encoding='utf-8') as f:
        f.write(head_t)
        yaml.dump(train, f, allow_unicode=True, sort_keys=False, width=120)
    with open(os.path.join(HERE, 'dropped.txt'), 'w', encoding='utf-8') as f:
        for k, why in dropped:
            f.write(f'{k}\t{why}\n')
    print(f'heldout={len(held)} trainset={len(train)} dropped={len(dropped)}')


if __name__ == '__main__':
    main()
