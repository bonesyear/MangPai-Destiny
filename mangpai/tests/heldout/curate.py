# -*- coding: utf-8 -*-
"""V3/K1 审定管线 step1 — 跨文件去重 + 污染标记 + 生成人工审定用 review.txt。

污染定义(不得入 heldout):
  calib10    = calib_assertions.yaml 的 10 例(已校准, -> trainset)
  backtest67 = regression67.py 的 67 例书例(已用于修引擎, -> trainset 附录)
去重键 = (gans, zhis, gender) 全局；跨文件同盘合并，source 双记。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, 'tests', 'backtest'))
sys.path.insert(0, REPO)
import yaml
import regression67 as r67


def norm_g(gs):
    return ''.join('己' if g == '已' else g for g in gs)


def key_of(gans, zhis, gender):
    return (norm_g(gans), ''.join(zhis), gender)


def contaminated():
    """返回 {key: tag}"""
    out = {}
    cal = yaml.safe_load(open(os.path.join(REPO, 'tests', 'calib_assertions.yaml'), encoding='utf-8'))
    for c in cal['cases']:
        out[key_of(c['gans'], c['zhis'], c['gender'])] = 'calib10:' + c['id']
    for name, g, z, *_ in r67.CAT1:
        out.setdefault(key_of(r67.fg(g), z, '男'), 'backtest67:' + name)
    for name, g, z, *_ in r67.CAT2:
        out.setdefault(key_of(r67.fg(g), z, '男'), 'backtest67:' + name)
    for pr, name, gs, zs, _ in r67.CAT3:
        out.setdefault(key_of(list(gs), list(zs), '男'), 'backtest67:' + name)
    for name, g, z, *_ in r67.CAI:
        out.setdefault(key_of(g, z, '男'), 'backtest67:' + name)
    for name, g, z, *_ in r67.GUAN:
        out.setdefault(key_of(g, z, '男'), 'backtest67:' + name)
    for name, g, z, gender, *_ in r67.CAT5:
        out.setdefault(key_of(g, z, gender), 'backtest67:' + name)
    return out


def main():
    cands = json.load(open(os.path.join(HERE, 'candidates.json'), encoding='utf-8'))
    cont = contaminated()
    merged = {}
    for c in cands:
        k = key_of(c['gans'], c['zhis'], c['gender'])
        if k in merged:
            m = merged[k]
            m['sources'].append(f"{c['section']}:{c['line']}")
            if len(c['context']) > len(m['context']):
                m['context'] = c['context']
                m['section'] = c['section']
            m['dup'] = m.get('dup', 0) + 1
        else:
            m = dict(c)
            m['sources'] = [f"{c['section']}:{c['line']}"]
            merged[k] = m
    cases = sorted(merged.values(), key=lambda c: (c['sources'][0]))
    for i, c in enumerate(cases):
        c['idx'] = i
        c['contam'] = cont.get(key_of(c['gans'], c['zhis'], c['gender']), '')
    json.dump(cases, open(os.path.join(HERE, 'merged.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    n_cal = sum(1 for c in cases if c['contam'].startswith('calib10'))
    n_b67 = sum(1 for c in cases if c['contam'].startswith('backtest67'))
    print(f'merged={len(cases)} calib10={n_cal} backtest67={n_b67} heldout-pool={len(cases)-n_cal-n_b67}')
    with open(os.path.join(HERE, 'review.txt'), 'w', encoding='utf-8') as f:
        for c in cases:
            gz = '/'.join([''.join(c['gans']), ''.join(c['zhis'])])
            f.write(f"━━ #{c['idx']} [{'CONTAM:'+c['contam']+']' if c['contam'] else 'POOL'}] "
                    f"{c['gender']} {gz} src={';'.join(c['sources'])}"
                    f"{' UNMARKED' if c['unmarked'] else ''}\n")
            f.write(c['context'] + '\n')


if __name__ == '__main__':
    main()
