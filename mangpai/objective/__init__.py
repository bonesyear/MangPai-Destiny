"""
objective - 盲派客观层

盲派命理计算引擎的客观层：只做"纯规则检测"与确定性分类，不做解释性判断。
包含藏干、长生、纳音、神煞、做功检测、宾主、体用、墓库、暗合、闭气、
木活死、土燥湿、合类型、虚实、正反局、象法等模块。

编排器（MangpaiEngine / calc_mangpai_full）已上移至 mangpai/engine.py，
本层不再持有 orchestrator，确保 objective 不反向依赖 subjective。

理论来源：段建业《段氏理象学》、盲师口传体系
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any, List

from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.changsheng import get_changsheng_mangpai
from mangpai.objective.nayin import get_nayin_mangpai, analyze_nayin_work
from mangpai.objective.shensha import compute_shensha_ext, SHENSHA_LAYER
from mangpai.objective.binzhu import analyze_binzhu
from mangpai.objective.tiyong import classify_tiyong
from mangpai.objective.muku import analyze_muku
from mangpai.objective.anhe import analyze_anhe
from mangpai.objective.biqi import analyze_biqi
from mangpai.objective.wood_type import analyze_wood_type
from mangpai.objective.soil_type import analyze_soil
from mangpai.objective.he_types import classify_he_types
from mangpai.objective.virtual_solid import analyze_virtual_solid
from mangpai.objective.gongfei import classify_gongshen
from mangpai.objective.gongshen import analyze_gongshen
from mangpai.objective.shenshu import analyze_shenshu
from mangpai.objective.jiaoyun import safe_compute_jiaoyun, compute_jiaoyun_timeline
from mangpai.objective.xiangfa import (
    get_gan_xiang, get_zhi_xiang, get_shishen_xiang,
    get_gongwei_xiang, get_shensha_xiang, get_liushi_ganzhi_xiang,
    GAN_XIANG, ZHI_XIANG, SHISHEN_XIANG, GONG_WEI_XIANG, SHENSHA_XIANG,
    LIUSHI_GANZHI_XIANG,
)
from mangpai.objective.body_parts import (
    get_gan_body, get_zhi_body, get_pillar_body, get_shishen_body,
    GAN_BODY, ZHI_BODY, PILLAR_BODY, SHISHEN_BODY,
)

logger = logging.getLogger(__name__)


@dataclass
class Pillars:
    """四柱数据封装，用于统一函数签名。"""
    year_gan: str = ''
    year_zhi: str = ''
    month_gan: str = ''
    month_zhi: str = ''
    day_gan: str = ''
    day_zhi: str = ''
    hour_gan: str = ''
    hour_zhi: str = ''

    @property
    def gans(self) -> List[str]:
        return [self.year_gan, self.month_gan, self.day_gan, self.hour_gan]

    @property
    def zhis(self) -> List[str]:
        return [self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi]

    @property
    def year_gz(self) -> str:
        return f'{self.year_gan}{self.year_zhi}'

    @property
    def month_gz(self) -> str:
        return f'{self.month_gan}{self.month_zhi}'

    @property
    def day_gz(self) -> str:
        return f'{self.day_gan}{self.day_zhi}'

    @property
    def hour_gz(self) -> str:
        return f'{self.hour_gan}{self.hour_zhi}'

    @property
    def pillar_gzs(self) -> List[str]:
        return [self.year_gz, self.month_gz, self.day_gz, self.hour_gz]


__all__ = [
    'Pillars',
    'get_canggan_mangpai', 'get_changsheng_mangpai',
    'get_nayin_mangpai', 'analyze_nayin_work',
    'compute_shensha_ext', 'SHENSHA_LAYER',
    'analyze_binzhu', 'classify_tiyong', 'analyze_muku',
    'analyze_anhe', 'analyze_biqi',
    'analyze_wood_type', 'analyze_soil',
    'classify_he_types', 'analyze_virtual_solid',
    'classify_gongshen', 'analyze_gongshen',
    'analyze_shenshu',
    'compute_jiaoyun_timeline', 'safe_compute_jiaoyun',
    'get_gan_xiang', 'get_zhi_xiang', 'get_shishen_xiang',
    'get_gongwei_xiang',
    'GAN_XIANG', 'ZHI_XIANG', 'SHISHEN_XIANG', 'GONG_WEI_XIANG',
    'get_gan_body', 'get_zhi_body', 'get_pillar_body', 'get_shishen_body',
    'GAN_BODY', 'ZHI_BODY', 'PILLAR_BODY', 'SHISHEN_BODY',
]
