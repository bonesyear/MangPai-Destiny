"""盲派主观层 — 流派定义。

自包含的 School dataclass + 盲派流派注册。
与 fate-subjective 的 School 结构一致，但独立于此包。
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class School:
    id: str
    name: str
    category: str            # 'bazi' | 'ziwei'
    prompt: str              # prompts/ 下模板文件名
    selectors: tuple = field(default_factory=tuple)
    sihua_version: str = ""
    desc: str = ""


MANGPAI_SCHOOL: School = School(
    id="mangpai", name="盲派", category="bazi",
    prompt="mangpai.md",
    selectors=("bazi", "shensha", "nayin", "nayin_work", "canggan",
               "chang_sheng", "kong_wang",
               "di_zhi_relations",
               "binzhu", "tiyong", "zuogong", "gongliang", "muku",
               "anhe", "biqi", "wood_type", "soil",
               "he_types", "virtual_solid", "zhengfan", "xiangfa",
               "shenshu", "dayun_analysis", "liunian_analysis",
               # 领域专辑 + 高级技法模块（gongliang/xiangfa 之下游）
               # 修批A③（R5 block-4）：gongmen_wuzhi 摘除——is_wuzhi 98.8% 恒真
               # 零信息量（F18 已切断 narrative 通道，本步落 payload 通道），
               # engine result 键保留（模块内部存档，不进 LLM）。
               "caiming", "guanming", "hunyin", "xueli", "laoyu",
               "yingqi_subj", "yunfan", "zhiye",
               # D6b：zinv（子女岁运应期+借腹）镜像 liuqin 同通道进特征 JSON
               # （纯数据；LLM 五维不扩不进 prompt——D6a 设计 §3.4）。
               # 缺口批1：qianyi（迁移/远行 marker+应期窗）同口径追加
               # （措辞上限「迁移/远行」；N1 七维批起进叙述维，L2 禁出境词）。
               # 缺口批2：xiangmao（相貌 marker 层，无判定无档位）同口径追加
               # （N1 七维批起进叙述维，L2 禁「美/丑/帅」结论词）。
               "liuqin", "zinv", "qianyi", "xiangmao", "zaihuo", "zeishen_bushen", "xiangfa_ops",
               "narrative", "shipaige"),
    desc="盲派宾主体用做功体系，重象法口诀。《段氏理象学》《盲师断命秘诀》",
)
