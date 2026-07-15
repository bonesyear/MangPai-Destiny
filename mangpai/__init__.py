"""盲派命理系统（mangpai）

分层结构:
    mangpai/
    ├── __init__.py      # 公共 API 枢纽（re-export）
    ├── engine.py        # 编排器 MangpaiEngine / calc_mangpai_full（依赖 objective+subjective）
    ├── objective/       # 客观层 - 纯规则检测/确定性分类（不依赖 subjective）
    └── subjective/      # 主观层 - 解释性判断（依赖 objective）

依赖方向单向：objective <- subjective <- engine。
本 __init__ 只做 re-export，方便外部 `from mangpai import MangpaiEngine` 等。
"""
from mangpai.engine import MangpaiEngine, calc_mangpai_full
from mangpai.objective import (
    Pillars,
    get_canggan_mangpai, get_changsheng_mangpai,
    get_nayin_mangpai, analyze_nayin_work,
    compute_shensha_ext, SHENSHA_LAYER,
    analyze_binzhu, classify_tiyong, analyze_muku,
    analyze_anhe, analyze_biqi,
    analyze_wood_type, analyze_soil,
    classify_he_types, analyze_virtual_solid,
    classify_gongshen, analyze_gongshen,
    analyze_shenshu,
    compute_jiaoyun_timeline, safe_compute_jiaoyun,
    get_gan_xiang, get_zhi_xiang, get_shishen_xiang,
    get_gongwei_xiang, get_shensha_xiang, get_liushi_ganzhi_xiang,
    GAN_XIANG, ZHI_XIANG, SHISHEN_XIANG, GONG_WEI_XIANG, SHENSHA_XIANG,
    LIUSHI_GANZHI_XIANG,
)
from mangpai.subjective.zuogong_confirm import analyze_zuogong, assess_work_level
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.shipaige import analyze_shipaige
from mangpai.subjective.dayun import analyze_dayun_mangpai
from mangpai.subjective.liunian import analyze_liunian_mangpai
from mangpai.subjective.yunfan import analyze_yunfan
from mangpai.subjective.zhiye import analyze_zhiye
from mangpai.subjective.gongmen_wuzhi import analyze_gongmen_wuzhi
from mangpai.subjective.liuqin import analyze_liuqin
from mangpai.subjective.zaihuo import analyze_zaihuo

__all__ = [
    'MangpaiEngine', 'calc_mangpai_full', 'Pillars',
    'get_canggan_mangpai', 'get_changsheng_mangpai',
    'get_nayin_mangpai', 'analyze_nayin_work',
    'compute_shensha_ext', 'SHENSHA_LAYER', 'analyze_zuogong',
    'analyze_binzhu', 'classify_tiyong', 'analyze_muku',
    'analyze_anhe', 'analyze_biqi',
    'analyze_wood_type', 'analyze_soil',
    'classify_he_types', 'analyze_virtual_solid',
    'analyze_zhengfan', 'classify_gongshen', 'analyze_gongshen',
    'assess_work_level', 'analyze_gongliang',
    'analyze_shenshu', 'analyze_dayun_mangpai', 'analyze_liunian_mangpai', 'analyze_yunfan',
    'analyze_zhiye', 'analyze_gongmen_wuzhi', 'analyze_liuqin', 'analyze_zaihuo',
    'compute_jiaoyun_timeline', 'safe_compute_jiaoyun',
    'analyze_shipaige',
    'get_gan_xiang', 'get_zhi_xiang', 'get_shishen_xiang',
    'get_gongwei_xiang',
    'GAN_XIANG', 'ZHI_XIANG', 'SHISHEN_XIANG', 'GONG_WEI_XIANG',
]
