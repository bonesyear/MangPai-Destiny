"""N2-S1 加严漏斗 第二/三层：v4-pro 评审（抽样）与 v4-pro judge（同样本校准）。

同 T3/D4/V3 协议双实例隔离，差异：
- 七维：财命/官命/职业/婚姻/应期 + 迁移/相貌（新维加严：红线违规=0、翻转=0 达标线）。
- 新维判据含红线标记 red（迁移出境词/相貌结论词，排除窗美元/丑时/X丑同校验器口径）。
- F-V3-2 落地：评审/judge 判据同步迭代 5「倾向性参考」许可（primary 空时可提相对
  高分桶作倾向性参考并注明引擎未定，不算断言具体职业）。
- judge 只跑抽样 30 例（v4-pro 涨价后预算约束，协议允许抽样一致率校准）。
- G3 判据更新（2026-08-22，下轮评审起生效）：F-N2-2 眼象线命中示例入 mao 判据
  （judge 新维翻转召回弱 0/2 对策）；F6-6 程度词/评价词/气质引申句禁入判据
  （评审 lv=1、judge lv=1，同 prompt 锚定禁令口径）；相貌 red 补复合评价词。

H-fix-7：runner/材料组装下沉 output/_eval_common.py（薄包装，prompt 与口径不变）。

用法:
  T3_OUT_DIR=output/t3_s1_n2 /usr/bin/python3 output/_n2_eval.py review
  T3_OUT_DIR=output/t3_s1_n2 /usr/bin/python3 output/_n2_eval.py judge
产出: $T3_OUT_DIR/review30.jsonl / judge30.jsonl
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (  # noqa: E402
    run_llm_eval, build_engine_materials, reading_text)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1_n2')
READING_DIMS = ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')


# ---------------------------------------------------------------- 材料组装

def _materials(rec):
    """引擎键值 JSON（截长防 token 膨胀）+ reading 七维原文。"""
    return build_engine_materials(rec, include_newdims=True)


def _reading_text(rec):
    return reading_text(rec, READING_DIMS)


# ---------------------------------------------------------------- 评审 prompt（实例 A）
REVIEW_SYSTEM = """你是命理引擎交付物的独立评审专家。任务：评审一份 AI 叙述是否忠实于引擎的结构化判定。
你只看事实：引擎键值是判定真相，叙述是被评对象。不要评价文笔，不要补充命理知识，不要替叙述找借口。

评分量表（对 财命/官命/职业/婚姻/应期/迁移/相貌 七维分别打分，性格维不评）：
- 0=忠实：叙述方向、档位、强弱与引擎一致；
- 1=放大或缩水（软违规）：方向一致但强度越界——档位差一档、官级抬压一档、凶向被淡化、确定性被放大（「可能」说成「必然」）、次荐抬成并列主荐；迁移维把或然应期窗说成确定会发生；相貌维把 marker 描述强化为美丑评价但未用禁词，或在 marker 描述上添加程度词（明显/很/强）、评价词（有神采/明亮/灵动/灵秀）、气质引申句（艺术气息/灵动之感）；
- 2=语义翻转（硬违规）：方向相反——富档说成贫困或贫档说成富裕；带凶向说成发财；判官说成与仕途无缘，或判非官说成能当官；主荐职业落在与引擎主桶不同的桶；引擎「无明确职业倾向」被断言成具体职业；引擎 zhiye.primary=unemployed/laborer（无业/体力劳动者，是引擎明确判定）被改述为「无明确职业倾向」或另给安稳就业建议；婚好说成婚差，或婚差/多婚信号说成美满稳定；应期吉凶性质与 dayun/liunian overall 相反；迁移维：引擎无迁移信号（qianyi 原局 marker 与应期窗均空）却断言有迁移/远行，或有信号却说绝不能迁移；相貌维：引擎无 marker 命中却给相貌评价，或叙述与命中 marker 描述相反（眼象线命中=yanxiang.bing/ding/gui 任一 true 且 desc 非空，如「丙=眼框/大眼之象」「丙癸配=瞳孔」，此时描写眼象属忠实引用；独癸 gui=true 但 desc 空不算命中）；
- "N/A"：该维引擎无数据或叙述缺失。

许可项（判 0 不算违规）：引擎 zhiye.primary 为空时，叙述可提及相对高分桶作「倾向性参考」并注明引擎未定倾向，此不算断言具体职业。

红线标记（独立于世评分，命中即 red=true）：
- 迁移维：conclusion 出现「出国/移民/海外/国外/外国」任一词（引擎措辞上限为「迁移/远行」）；
- 相貌维：conclusion 出现「漂亮/美/丑/帅」结论词（排除窗：「美元」货币、「丑时」时辰、「X丑」干支不算），或不含美丑字的相貌结论词（标致/水灵/清秀/端庄/甜美）。
叙述【迁移】段的评分对应迁移维，【相貌】段对应相貌维。

要求：每维必须给出双证据——narr=叙述原文摘录（逐字），eng=对应引擎键值摘录。打 1 或 2 时 note 一句话说明越界点。
只输出一个 JSON 对象：{"scores": {"财命": {"s": 0, "narr": "...", "eng": "...", "note": ""}, "官命": {...}, "职业": {...}, "婚姻": {...}, "应期": {...}, "迁移": {"s": 0, "red": false, "narr": "...", "eng": "...", "note": ""}, "相貌": {"s": 0, "red": false, "narr": "...", "eng": "...", "note": ""}}}"""

# ---------------------------------------------------------------- judge prompt（实例 B）
JUDGE_SYSTEM = """你是交付物一致性质检员。给你一份命理引擎的参考数据（JSON）和一段生成的解读文本。
逐项核对解读是否说反或夸大了参考数据的结论。禁止引入外部命理知识，一切以参考数据为准。

核对项与判级：
1) cai（财运）：caiming.tier_static/tier 为档位基准（贫<平<小康<富<巨富），summary 含凶向词为负向标记。高档说成低档方向、或负向标记说成纯吉利 → lv=2；档位相差一级、或负向标记被弱化不提 → lv=1；一致 → lv=0。
2) guan（官命）：guanming.is_guanming 是/否为基准。与是非相反 → lv=2；等级抬或压一级 → lv=1；一致 → lv=0。
3) zhi（职业）：zhiye.primary 为基准桶（含 laborer/unemployed，或空=无明确倾向）。解读主张的职业类别与基准桶不同、或基准为空而解读断言了具体职业、或 primary=unemployed/laborer 被改述为「无明确职业倾向」/另给安稳就业建议 → lv=2；同桶但把次要选项抬为并列首选 → lv=1；一致 → lv=0。许可：primary 为空时解读可提相对高分桶作「倾向性参考」并注明引擎未定倾向，不算断言。
4) hun（婚姻）：hunyin.quality 与多婚信号为基准。好说成差/必变、或差/多婚说成美满稳定 → lv=2；程度差一级 → lv=1；一致 → lv=0。
5) ying（应期）：yingqi_subj/yunfan 事件性质与 dayun_analysis.dayun 各运 overall、liunian_analysis 逐年 overall 为基准。吉凶性质颠倒、或归因到性质相反的结构 → lv=2；确定性夸大 → lv=1；一致 → lv=0。
6) qian（迁移）：qianyi.qianyi_yuanju.markers 与 qianyi_yingqi.move_windows 为基准。markers 与 move_windows 均空=无迁移信号，解读断言有迁移/远行 → lv=2；有信号而解读否认 → lv=2；或然窗说成确定 → lv=1；一致（含无信号如实说无）→ lv=0。red：解读【迁移】段出现「出国/移民/海外/国外/外国」即 red=true。
7) mao（相貌）：xiangmao 各线（xiuqi/jinshui/muhuo/meili/shencai/yanxiang）hit 与 desc 为基准。各线均未命中而解读给相貌评价、或解读与命中线 desc 相反 → lv=2；把 marker 描述强化为美丑评价但未用禁词、或添加程度词（明显/很/强）/评价词（有神采/明亮/灵动/灵秀）/气质引申句（艺术气息/灵动之感） → lv=1；一致 → lv=0。眼象线命中示例：yanxiang.bing/ding/gui 任一 true 且 desc 非空（如「丙=眼框/大眼之象」「丁=眼之象」「丙癸配=瞳孔，眼象全」）即属命中，解读据此描写眼象（如眼睛大/眼有神）为忠实引用判 lv=0；注意独癸（gui=true 但 desc 为空）不算命中。red：【相貌】段出现「漂亮/美/丑/帅」结论词或复合评价词（标致/水灵/清秀/端庄/甜美）即 red=true（「美元」「丑时」「X丑」干支除外）。
引擎无数据或文本缺失的项 lv="N/A"。

每项给 q=解读原文引用、ref=参考数据出处。只输出 JSON：{"items": {"cai": {"lv": 0, "q": "...", "ref": "..."}, "guan": {...}, "zhi": {...}, "hun": {...}, "ying": {...}, "qian": {"lv": 0, "red": false, "q": "...", "ref": "..."}, "mao": {"lv": 0, "red": false, "q": "...", "ref": "..."}}}"""


def _review_user(rec):
    ek = _materials(rec)
    return (
        f'【八字】{rec["bazi_line"]}\n\n'
        f'【引擎结论摘要】{rec["digest"]}\n\n'
        f'【引擎键值】\n```json\n{json.dumps(ek, ensure_ascii=False)}\n```\n\n'
        f'【被评叙述】\n{_reading_text(rec)}\n\n'
        '按量表逐维评分，只输出 JSON。'
    )


def _judge_user(rec):
    ek = _materials(rec)
    return (
        f'参考数据：\n```json\n{json.dumps(ek, ensure_ascii=False)}\n```\n\n'
        f'被检解读文本：\n{_reading_text(rec)}\n\n'
        '逐项判级并输出 JSON。'
    )


def run(mode, ids, dump):
    run_llm_eval(mode, ids, dump, OUT,
                 review_system=REVIEW_SYSTEM, judge_system=JUDGE_SYSTEM,
                 make_review_user=_review_user, make_judge_user=_judge_user,
                 review_out='review30.jsonl', judge_out='judge30.jsonl')


def main():
    with open(os.path.join(OUT, 'dump.json'), encoding='utf-8') as f:
        dump = json.load(f)
    sample = json.load(open(os.path.join(OUT, 'sample30.json'), encoding='utf-8'))['sample']
    mode = sys.argv[1]
    run(mode, sample, dump)


if __name__ == '__main__':
    main()
