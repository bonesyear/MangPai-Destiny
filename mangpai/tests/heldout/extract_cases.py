# -*- coding: utf-8 -*-
"""V3/K1 候选案例提取器 — 从两书原文扫描「完整八字+断语上下文」候选。

数据源:
  mangpai/docs/duan-books/shouke-jiaocheng.txt   (授课教程 7432 行)
  mangpai/docs/duan-books/mingli-zhenbao-50qi.txt (50期资料 837 行)

输出: mangpai/tests/heldout/candidates.json (草稿，供人工审定为 cases.yaml)

解析两种排版:
  A. 叠排: 「乾造：壬 癸 甲 壬」+ 下一非空行「辰 丑 戌 申」(可夹大运同行)
  B.  inline: 「乾造：癸未、戊午、庚申、壬午」
另设 generic gz-block 探测(无乾坤标记的命例, 如「如岳飞：」)，unmarked=true 待人工判。

OCR 纠错(位置感知): 干位 已/巳->己; 支位 己/已->巳, 戍->戌, 末->未, 西->酉。
六十甲子奇偶校验: 干与支阴阳须一致，不一致且纠错无效者 valid=false。
"""
import json, os, re, sys

GANS = '甲乙丙丁戊己庚辛壬癸'
ZHIS = '子丑寅卯辰巳午未申酉戌亥'
GAN_FIX = {'已': '己', '巳': '己', '杞': '己', '犯': '己'}
ZHI_FIX = {'己': '巳', '已': '巳', '戍': '戌', '末': '未', '西': '酉',
           '免': '卯', '牛': '丑', '卞': '丑'}

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = {
    'shouke': os.path.join(HERE, '..', '..', 'docs', 'duan-books', 'shouke-jiaocheng.txt'),
    'zhenbao': os.path.join(HERE, '..', '..', 'docs', 'duan-books', 'mingli-zhenbao-50qi.txt'),
}

MARKER = re.compile(r'(乾造|坤造|乾：|坤:|乾:|坤：)')
QI_HEADER = re.compile(r'第[一二三四五六七八九十百]+期')
GZ_PAIR = re.compile(r'([甲乙丙丁戊己庚辛壬癸已巳][子丑寅卯辰巳午未申酉戌亥己已戍末西])')

CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def cn2int(s):
    if s in CN: return CN[s]
    if s == '五十': return 50
    if s.startswith('十'): return 10 + CN.get(s[1:], 0)
    if s.endswith('十'): return CN.get(s[0], 0) * 10
    if '十' in s:
        a, b = s.split('十', 1)
        return CN.get(a, 0) * 10 + CN.get(b, 0)
    return 0

SEC_QI = re.compile(r'第([一二三四五六七八九十]+)期(?![作业答])')
SEC_ANS = re.compile(r'第([一二三四五六七八九十]+)期作业答案')
SEC_LI = re.compile(r'例(\d{1,3})')

def find_section(lines, i, tag):
    """向上找最近的 期头/作业答案/例N 标记作 source 段名。"""
    for k in range(i, max(0, i - 400), -1):
        L = lines[k]
        m = SEC_ANS.search(L)
        if m: return f'{tag}-ans{cn2int(m.group(1)):02d}'
        m = SEC_QI.search(L)
        if m: return f'{tag}-qi{cn2int(m.group(1)):02d}'
        m = SEC_LI.search(L)
        if m and k <= i and int(m.group(1)) <= 300: return f'{tag}-li{int(m.group(1)):03d}'
    return f'{tag}-?'


def fix_gan(c):
    return c if c in GANS else GAN_FIX.get(c)


def fix_zhi(c):
    return c if c in ZHIS else ZHI_FIX.get(c)


def clean(s):
    """去空格/全角数字序号/? 等 OCR 噪声，保留干支与混淆字。"""
    s = re.sub(r'[\s?？　]+', '', s)
    s = re.sub(r'[０-９0-9lI]+[、.．]?', '', s)
    return s


def chars_of(s, want):
    """提取一行中属干类/支类的字，返回 (修正后list, 原始字数)。"""
    out, raw = [], 0
    for c in clean(s):
        if want == 'gan':
            f = fix_gan(c)
            if f and c not in ZHIS:  # 巳 在干位视为己
                out.append(f); raw += 1
            elif f:
                out.append(f); raw += 1
        else:
            f = fix_zhi(c)
            if f and c not in GANS:
                out.append(f); raw += 1
            elif f and c in ('己', '已'):
                out.append(f); raw += 1
    return out, raw


def valid_gz(g, z):
    return g in GANS and z in ZHIS and (GANS.index(g) - ZHIS.index(z)) % 2 == 0


def parse_inline(text):
    """inline 顿号/逗号分隔的四柱。"""
    pairs = GZ_PAIR.findall(clean(text).replace('、', '').replace('，', '').replace(',', ''))
    if len(pairs) >= 4:
        gs = [fix_gan(p[0]) for p in pairs[:4]]
        zs = [fix_zhi(p[1]) for p in pairs[:4]]
        if all(gs) and all(zs) and all(valid_gz(g, z) for g, z in zip(gs, zs)):
            return gs, zs
    return None


def parse_stacked(lines, i, after):
    """叠排: after=标记行余文。返回 (gans, zhis, consumed_lines) 或 None。"""
    gans, _ = chars_of(after, 'gan')
    j = i
    if len(gans) != 4:  # 标记行无干 → 下一非空行为干行
        for k in range(i + 1, min(i + 4, len(lines))):
            if clean(lines[k]):
                gans, _ = chars_of(lines[k], 'gan')
                j = k
                break
    if len(gans) != 4:
        return None
    for k in range(j + 1, min(j + 4, len(lines))):
        if not clean(lines[k]):
            continue
        # 干行下一非空行应恰为 4 支(可带大运尾)
        seg = re.split(r'大运|大運', lines[k])[0]
        zhis, _ = chars_of(seg, 'zhi')
        if len(zhis) == 4:
            return gans, zhis, k - i
        return None
    return None


def parse_twin(lines, i, after):
    """「X 与 Y」双造同行: 8干+次行8支 → 两例。"""
    if '与' not in after:
        return None
    gans, _ = chars_of(after, 'gan')
    if len(gans) != 8:
        return None
    for k in range(i + 1, min(i + 4, len(lines))):
        if not clean(lines[k]):
            continue
        seg = re.split(r'大运|大運', lines[k])[0]
        zhis, _ = chars_of(seg, 'zhi')
        if len(zhis) == 8:
            return [(gans[:4], zhis[:4]), (gans[4:], zhis[4:])], k - i
        return None
    return None


def grab_dayun(lines, i, upto):
    """在命例邻近行抓大运原文(叠排或inline)，仅作参考字符串。"""
    for k in range(i, min(upto + 3, len(lines))):
        if '大运' in lines[k] or '大運' in lines[k]:
            seg = lines[k].strip()
            tail = lines[k + 1].strip() if k + 1 < len(lines) and clean(lines[k + 1]) else ''
            return (seg + ' ' + tail)[:80]
    return ''


def context_block(lines, i, cap=26):
    """从标记行抓上下文，止于下一命例标记/期头，封顶 cap 行。"""
    out = []
    for k in range(i, min(i + cap, len(lines))):
        L = lines[k]
        if k > i and (MARKER.search(L) or (QI_HEADER.search(L) and '作业' not in L)):
            break
        out.append(L.rstrip())
    txt = '\n'.join(out)
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    return txt.strip()[:900]


def extract(path, tag):
    lines = open(path, encoding='utf-8').read().splitlines()
    cands, seen_lines = [], set()
    for i, L in enumerate(lines):
        m = MARKER.search(L)
        if not m:
            continue
        gender = '男' if m.group(1).startswith('乾') else '女'
        after = L[m.end():]
        # 大运同行时先切断
        after_main = re.split(r'大运|大運', after)[0]
        # 「X 与 Y」双造同行
        twin = parse_twin(lines, i, after_main)
        if twin:
            pairs, consumed = twin
            for gi, (gans, zhis) in enumerate(pairs):
                ok = all(valid_gz(g, z) for g, z in zip(gans, zhis))
                cands.append({
                    'file': tag, 'line': i + 1, 'gender': gender, 'unmarked': False,
                    'section': find_section(lines, i, tag) + chr(ord('a') + gi),
                    'gans': gans, 'zhis': zhis, 'valid': ok,
                    'dayun_raw': grab_dayun(lines, i, i + max(consumed, 1)),
                    'context': context_block(lines, i),
                })
            continue
        r = parse_inline(after_main)
        consumed = 0
        if r:
            gans, zhis = r
        else:
            r2 = parse_stacked(lines, i, after_main)
            if not r2:
                continue
            gans, zhis, consumed = r2
        ok = all(valid_gz(g, z) for g, z in zip(gans, zhis))
        cands.append({
            'file': tag, 'line': i + 1, 'gender': gender, 'unmarked': False,
            'section': find_section(lines, i, tag),
            'gans': gans, 'zhis': zhis, 'valid': ok,
            'dayun_raw': grab_dayun(lines, i, i + max(consumed, 1)),
            'context': context_block(lines, i),
        })
        seen_lines.add(i)
    # generic gz-block 探测(无标记)
    for i, L in enumerate(lines):
        if i in seen_lines or MARKER.search(L):
            continue
        Lmain = re.split(r'大运|大運', L)[0]
        gans, _ = chars_of(Lmain, 'gan')
        if len(gans) != 4:
            continue
        for k in range(i + 1, min(i + 3, len(lines))):
            if not clean(lines[k]):
                continue
            seg = re.split(r'大运|大運', lines[k])[0]
            zhis, _ = chars_of(seg, 'zhi')
            if len(zhis) == 8:  # 命盘4支+大运干支尾(无大运关键字)
                zhis = zhis[:4]
            if len(zhis) != 4:
                break
            head = ''.join(lines[max(0, i - 3):i])
            if not re.search(r'[造例命：:]', head + L[:4] + L.strip()[:10]):
                break
            if not all(valid_gz(g, z) for g, z in zip(gans, zhis)):
                break
            near = ''.join(lines[max(0, i - 3):i + 6])
            gender = '女' if re.search(r'坤|女命|她|妻(?!星)', near) else '男'
            cands.append({
                'file': tag, 'line': i + 1, 'gender': gender, 'unmarked': True,
                'section': find_section(lines, i, tag),
                'gans': gans, 'zhis': zhis, 'valid': True,
                'dayun_raw': grab_dayun(lines, i, i + 1),
                'context': context_block(lines, i),
            })
            break
    cands.sort(key=lambda c: c['line'])
    return cands


def main():
    all_c = []
    for tag, path in BOOKS.items():
        all_c.extend(extract(path, tag))
    # 去重: 同文件同八字同性别(保留 context 最长者)
    best = {}
    for c in all_c:
        key = (c['file'], ''.join(c['gans']), ''.join(c['zhis']), c['gender'])
        if key not in best or len(c['context']) > len(best[key]['context']):
            best[key] = c
    dedup = sorted(best.values(), key=lambda c: (c['file'], c['line']))
    out = os.path.join(HERE, 'candidates.json')
    json.dump(dedup, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inv = [c for c in dedup if not c['valid']]
    unm = [c for c in dedup if c['unmarked']]
    print(f'total={len(dedup)} valid={len(dedup)-len(inv)} unmarked={len(unm)}')
    for c in inv:
        print(f"  INVALID {c['file']}:{c['line']} {c['gans']}{c['zhis']}")
    for c in unm:
        print(f"  unmarked {c['file']}:{c['line']} {''.join(c['gans'])}/{''.join(c['zhis'])} {c['gender']}")


if __name__ == '__main__':
    main()
