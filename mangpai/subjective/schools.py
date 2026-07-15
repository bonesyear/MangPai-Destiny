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
               "caiming", "guanming", "hunyin", "xueli", "laoyu",
               "yingqi_subj", "yunfan", "zhiye", "gongmen_wuzhi",
               "liuqin", "zaihuo", "zeishen_bushen", "xiangfa_ops",
               "narrative", "shipaige"),
    desc="盲派宾主体用做功体系，重象法口诀。《段氏理象学》《盲师断命秘诀》",
)
