"""盲派主观层独立测试 — 验证 build_payload / assemble / prompt 加载。"""
import sys
import os
import json
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subjective import (
    MANGPAI_SCHOOL, build_payload, assemble, load_template,
    ENVELOPE_RULES, School,
)
from subjective.schools import MANGPAI_SCHOOL as SCHOOL_FROM_SCHOOLS


class TestSchoolDefinition:
    """流派定义测试"""

    def test_school_id(self):
        assert MANGPAI_SCHOOL.id == "mangpai"

    def test_school_name(self):
        assert MANGPAI_SCHOOL.name == "盲派"

    def test_school_category(self):
        assert MANGPAI_SCHOOL.category == "bazi"

    def test_school_prompt_file(self):
        assert MANGPAI_SCHOOL.prompt == "mangpai.md"

    def test_school_has_39_selectors(self):
        # 24 基础 + 15 领域专辑/高级技法模块（caiming/guanming/hunyin/...）
        # 修批A③：gongmen_wuzhi 摘除（is_wuzhi 98.8% 恒真零信息量），39→38
        # D6b：zinv（子女岁运应期+借腹）镜像 liuqin 进特征 JSON，38→39
        assert len(MANGPAI_SCHOOL.selectors) == 39
        assert 'gongmen_wuzhi' not in MANGPAI_SCHOOL.selectors
        assert 'zinv' in MANGPAI_SCHOOL.selectors

    def test_selectors_include_blind_fields(self):
        for field in ("binzhu", "tiyong", "zuogong", "gongliang", "muku",
                      "anhe", "biqi", "wood_type", "soil",
                      "he_types", "virtual_solid", "zhengfan", "xiangfa",
                      "shenshu", "dayun_analysis", "liunian_analysis",
                      "chang_sheng"):
            assert field in MANGPAI_SCHOOL.selectors, f"缺少 {field}"

    def test_selectors_include_standard_fields(self):
        for field in ("bazi", "shensha", "nayin", "canggan",
                      "kong_wang", "di_zhi_relations"):
            assert field in MANGPAI_SCHOOL.selectors, f"缺少 {field}"

    def test_school_is_same_object_from_schools_module(self):
        assert MANGPAI_SCHOOL is SCHOOL_FROM_SCHOOLS

    def test_school_is_frozen(self):
        with pytest.raises(Exception):
            MANGPAI_SCHOOL.id = "other"  # type: ignore


class TestLoadTemplate:
    """prompt 模板加载测试"""

    def test_template_loads(self):
        text = load_template()
        assert "## 角色" in text
        assert "## 理论框架" in text
        assert "## 参考经典" in text

    def test_template_contains_blind_school_concepts(self):
        text = load_template()
        assert "宾主" in text
        assert "体用" in text
        assert "做功" in text
        assert "功神" in text

    def test_template_mentions_all_selector_fields(self):
        text = load_template()
        for field in ("binzhu", "tiyong", "zuogong", "muku",
                      "anhe", "biqi", "wood_type", "soil",
                      "he_types", "virtual_solid", "zhengfan", "xiangfa",
                      "shenshu", "dayun_analysis", "liunian_analysis"):
            assert field in text, f"模板未提及 {field}"


class TestBuildPayload:
    """payload 裁剪测试"""

    @pytest.fixture
    def mangpai_data(self):
        """模拟 calc_mangpai_full() 输出。"""
        return {
            "bazi": {"year": "己未", "month": "乙亥", "day": "辛巳", "hour": "癸巳",
                     "full": "己未 乙亥 辛巳 癸巳"},
            "input": {"year": 1979, "month": 11, "day": 10},
            "canggan": {"未": [("己", "本气")], "亥": [("壬", "本气")]},
            "chang_sheng": {"year_zhi": "死", "month_zhi": "长生"},
            "chang_sheng": {"year_zhi": "死", "month_zhi": "长生"},
            "nayin": [{"name": "天上火", "wuxing": "火", "weight": 4}],
            "nayin_work": {"total_weight": 10, "dominant_wuxing": "火"},
            "shensha": {"羊刃": {"zhi": "未", "in_pillars": ["year"]}},
            "binzhu": {"layer1": {"label": "主"}, "layer2": {"label": "宾"}},
            "tiyong": {"ti_count": 1, "yong_count": 3},
            "zuogong": {"work_types": ["制用"], "work_level": 1},
            "gongliang": {"level": 1, "tier_name": "小富小贵", "score": 12,
                          "gong_points": 0.0, "reasons": [], "zhi_jing": "无制",
                          "yuanshen_yongshen": None, "controls": [],
                          "gong_shen_cats": [], "chain_length": 0,
                          "penalty": None, "confidence": "中"},
            "muku": {"tombs": [], "tomb_relations": []},
            "anhe": [],
            "biqi": [],
            "wood_type": {"is_wood": False, "wood_type": "非木日主"},
            "soil": {"wet_soil": [], "dry_soil": []},
            "he_types": [],
            "virtual_solid": {"virtual_count": 0, "solid_count": 0},
            "zhengfan": {"type": "neutral"},
            "xiangfa": {"gan_xiang": {}, "zhi_xiang": {}, "shishen_xiang": {}},
            "shenshu": {
                "summary": "偏财1(清纯)、正官2(混杂)、偏印2(混杂)、食神1(清纯)、伤官1(清纯)",
                "grades": {"清纯": ["偏财", "食神", "伤官"], "成势": [], "混杂": ["正官", "偏印"], "不见": []},
            },
            "kong_wang": {},
            "di_zhi_relations": {"六冲": [], "六合": []},
            "dayun_analysis": {
                "dayun": [{"gz": "丙寅", "overall": "吉", "start_age": 5}],
                "ji_count": 1, "xiong_count": 0, "summary": "共1步大运；吉运1步",
            },
            "liunian_analysis": {
                "liunian": [{"gz": "甲子", "overall": "平", "year": 2024}],
                "ji_count": 0, "xiong_count": 0, "summary": "共1年",
            },
            # ── 领域专辑 / 高级技法模块（compute_all 各 analyze_* 输出键） ──
            "caiming": {"tier": "小康", "summary": "禄神当财"},
            "guanming": {"is_guanming": False, "summary": "非官命"},
            "hunyin": {"quality": "平", "summary": "婚姻平"},
            "xueli": {"level_str": "中", "summary": "学历中"},
            "laoyu": {"risk": "无", "summary": "牢狱风险无"},
            "yingqi_subj": {"conclusion": "应期未成立", "summary": "应期未成立"},
            "yunfan": {"dayun_fan": [], "liunian_fan": [], "summary": "无反局"},
            "zhiye": {"primary": "", "summary": "职业未明"},
            "gongmen_wuzhi": {"is_wuzhi": False, "summary": "无公门武职象"},
            "liuqin": {"summary": "六亲论断"},
            "zinv": {"summary": "子女应期：无明显应期窗"},
            "zaihuo": {"max_risk": "无", "summary": "灾祸总风险无"},
            "zeishen_bushen": {"points": 0.0, "summary": "无贼神捕神"},
            "xiangfa_ops": {"all_findings": [], "locked_subjects": []},
            "narrative": "做功：制用 L1 | 正反：无做功",
            "shipaige": {"report": ""},
            "summary": "日主辛巳",
        }

    def test_payload_has_all_selector_fields(self, mangpai_data):
        payload = build_payload(mangpai_data)
        for sel in MANGPAI_SCHOOL.selectors:
            assert sel in payload, f"payload 缺少 {sel}"

    def test_payload_excludes_non_selector_fields(self, mangpai_data):
        payload = build_payload(mangpai_data)
        assert "input" not in payload
        assert "summary" not in payload
        assert "di_zhi_relations" in payload  # selector field stays

    def test_payload_content_is_correct(self, mangpai_data):
        payload = build_payload(mangpai_data)
        assert payload["bazi"]["full"] == "己未 乙亥 辛巳 癸巳"
        assert payload["tiyong"]["ti_count"] == 1
        assert payload["zuogong"]["work_types"] == ["制用"]

    def test_payload_missing_fields_skipped(self):
        """缺失字段静默跳过。"""
        data = {"bazi": {"full": "甲子 甲子 甲子 甲子"}}
        payload = build_payload(data)
        assert "bazi" in payload
        assert "binzhu" not in payload
        assert "zuogong" not in payload

    def test_payload_is_json_serializable(self, mangpai_data):
        payload = build_payload(mangpai_data)
        json.dumps(payload, ensure_ascii=False)

    def test_wildcard_selector_returns_all(self):
        """selectors=('*',) 时返回全量。"""
        school = School(id="test", name="test", category="bazi",
                        prompt="mangpai.md", selectors=("*",))
        data = {"a": 1, "b": [1, 2], "c": {"x": "y"}}
        payload = build_payload(data, school=school)
        assert payload == data


class TestAssemble:
    """prompt 组装测试"""

    @pytest.fixture
    def payload(self):
        return {
            "bazi": {"full": "己未 乙亥 辛巳 癸巳"},
            "zuogong": {"work_types": ["制用"], "work_level": 1},
        }

    def test_returns_system_user_tuple(self, payload):
        result = assemble(question="看事业", payload=payload)
        assert len(result) == 2
        system, user = result
        assert isinstance(system, str)
        assert isinstance(user, str)

    def test_system_contains_template(self, payload):
        system, _ = assemble(payload=payload)
        assert "## 角色" in system
        assert "盲派命理师" in system

    def test_system_contains_envelope_rules(self, payload):
        system, _ = assemble(payload=payload)
        assert "JSON" in system
        assert "dimensions" in system
        assert "data_gaps" in system
        assert "reading" in system

    def test_system_contains_scope(self, payload):
        system, _ = assemble(payload=payload, scope="流年")
        assert "流年" in system

    def test_user_contains_question(self, payload):
        _, user = assemble(question="帮我看看事业", payload=payload)
        assert "帮我看看事业" in user

    def test_user_contains_data(self, payload):
        _, user = assemble(payload=payload)
        assert "己未 乙亥 辛巳 癸巳" in user

    def test_default_question_when_empty(self, payload):
        _, user = assemble(question="", payload=payload)
        assert "请按本派方法论做整体解读" in user

    def test_user_instructs_json(self, payload):
        _, user = assemble(payload=payload)
        assert "JSON" in user

    def test_empty_payload_works(self):
        system, user = assemble(question="test")
        assert "## 角色" in system
        assert "test" in user
