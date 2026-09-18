"""T3-S1 第二/三层：v4-pro 评审（30 例）与 v4-pro judge（281 例）——双实例隔离。

隔离设计（§5.0 用户拍板）：
- 评审（--mode review）：system A「独立评审专家」+ 键值材料 + digest 行；
  输出 schema A（scores/s/narr/eng/note）。单盲：不给 L2/规则锚标记。
- judge（--mode judge）：system B「一致性质检」+ 仅引擎键值（无 digest 行，
  与评审看到的信息面不同）+ 不同措辞判据；输出 schema B（items/lv/q/ref）。
  judge 永不接触评审输出。
- 两实例均 deepseek-v4-pro（谷段）；被评对象=v4-flash v5 生产叙述。

判据两版文字不同但语义同源（§5.1 表），量表 0=忠实/1=放大或缩水/2=翻转/N/A。
注：本文件为五维口径历史轮次存档；第七轮起 judge/评审用七维口径
（迁移/相貌加严判据 + F6-6 程度词禁入 + 眼象线命中示例）见 output/_n2_eval.py。

H-fix-7：runner/材料组装下沉 output/_eval_common.py（薄包装，prompt 与口径不变）。

用法:
  python3 output/_t3_eval.py review            # 30 例评审
  python3 output/_t3_eval.py judge [start end] # 281 例 judge（可分段）
产出: output/t3_s1/review30.jsonl / judge281.jsonl
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _eval_common import (  # noqa: E402
    run_llm_eval, build_engine_materials, reading_text)

OUT = os.environ.get('T3_OUT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 't3_s1')
DIMS = ('财命', '官命', '职业', '婚姻', '应期')
READING_DIMS = ('性格', '事业', '财运', '婚姻', '应期')

# ---------------------------------------------------------------- 材料组装

def _materials(rec):
    """引擎键值 JSON（截长防 token 膨胀）+ reading 五维原文。"""
    return build_engine_materials(rec, truncate_hunyin_signals=True)


def _reading_text(rec):
    return reading_text(rec, READING_DIMS)


# ---------------------------------------------------------------- 评审 prompt（实例 A）
REVIEW_SYSTEM = """你是命理引擎交付物的独立评审专家。任务：评审一份 AI 叙述是否忠实于引擎的结构化判定。
你只看事实：引擎键值是判定真相，叙述是被评对象。不要评价文笔，不要补充命理知识，不要替叙述找借口。

评分量表（对 财命/官命/职业/婚姻/应期 五维分别打分，性格维不评）：
- 0=忠实：叙述方向、档位、强弱与引擎一致；
- 1=放大或缩水（软违规）：方向一致但强度越界——档位差一档、官级抬压一档、凶向被淡化（如「破财风险」淡化为「小有波折」）、确定性被放大（「可能」说成「必然」）、次荐抬成并列主荐；
- 2=语义翻转（硬违规）：方向相反——富档说成贫困/财难聚或贫档说成富裕；带凶向（破财/凶）说成发财/财运佳；判官说成与仕途无缘/宜商不宜官，或判非官说成能当官/有官运；主荐职业落在与引擎主桶不同的桶；引擎「无明确职业倾向」被断言成具体职业；婚好说成婚差/必变，或婚差/多婚信号说成婚姻美满稳定；应期某运/某年吉凶性质与 dayun_analysis.dayun 各运 overall 或 liunian_analysis 逐年 overall 相反（凶运说成吉运/吉年说成凶年），或把某事件的依据引到性质相反的结构上；
- "N/A"：该维引擎无数据或叙述缺失。

要求：每维必须给出双证据——narr=叙述原文摘录（逐字），eng=对应引擎键值摘录。打 1 或 2 时 note 一句话说明越界点。
只输出一个 JSON 对象：{"scores": {"财命": {"s": 0, "narr": "...", "eng": "...", "note": ""}, "官命": {...}, "职业": {...}, "婚姻": {...}, "应期": {...}}}"""

# ---------------------------------------------------------------- judge prompt（实例 B，与 A 措辞/结构/信息面均不同）
JUDGE_SYSTEM = """你是交付物一致性质检员。给你一份命理引擎的参考数据（JSON）和一段生成的解读文本。
逐项核对解读是否说反或夸大了参考数据的结论。禁止引入外部命理知识，一切以参考数据为准。

核对项与判级：
1) cai（财运）：参考数据 caiming.tier_static/tier 为档位基准（贫<平<小康<富<巨富），summary 含凶向词（破财/牢狱/官非等）为负向标记。解读把高档说成低档方向、或把负向标记说成纯吉利 → lv=2；档位相差一级、或负向标记被弱化不提 → lv=1；一致 → lv=0。
2) guan（官命）：guanming.is_guanming 是/否为基准。解读与是非相反 → lv=2；等级（level/grade）抬或压一级 → lv=1；一致 → lv=0。
3) zhi（职业）：zhiye.primary 为基准桶（military/lawyer/teacher/doctor/accountant/merchant/performer，或 laborer/unemployed，或空=无明确倾向）。解读主张的职业类别与基准桶不同、或基准为空而解读断言了具体职业 → lv=2；同桶但把次要选项抬为并列首选 → lv=1；一致 → lv=0。
4) hun（婚姻）：hunyin.quality 与多婚信号为基准。好说成差/必变、或差/多婚说成美满稳定 → lv=2；程度差一级（如「有摩擦」说成「争战不断」）→ lv=1；一致 → lv=0。
5) ying（应期）：yingqi_subj 与 yunfan 的事件性质（吉/凶/反局）为基准，逐运吉凶以 dayun_analysis.dayun 各运 overall 为准、逐年以 liunian_analysis 逐年 overall 为准。吉凶性质颠倒（凶运说成吉运等）、或把事件归因到性质相反的结构 → lv=2；把「可能」说成「必然」等确定性夸大 → lv=1；一致 → lv=0。
引擎无数据或文本缺失的项 lv="N/A"。

每项给 q=解读原文引用、ref=参考数据出处。只输出 JSON：{"items": {"cai": {"lv": 0, "q": "...", "ref": "..."}, "guan": {...}, "zhi": {...}, "hun": {...}, "ying": {...}}}"""


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
                 review_out='review30.jsonl', judge_out='judge281.jsonl')


def main():
    with open(os.path.join(OUT, 'dump.json'), encoding='utf-8') as f:
        dump = json.load(f)
    mode = sys.argv[1]
    if mode == 'review':
        sample = json.load(open(os.path.join(OUT, 'sample30.json'), encoding='utf-8'))
        run('review', sample['sample'], dump)
    else:
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        end = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
        run('judge', sorted(dump)[start:end], dump)


if __name__ == '__main__':
    main()
