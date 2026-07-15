"""
canggan — 盲派藏干

理论来源：段建业《段氏理象学》、郝金阳口传盲师体系
流派共识：段建业《段氏理象学》使用与传统一致的藏干表，
  午藏丁、己（己禄在午），亥藏壬、甲（不含戊）。
  此前版本误删午中己土，现已修正回传统藏干表。
已知争议：部分网络流派主张"午只藏丁"，但四部权威文献
  （段氏理象学、盲派命理、命理瑰宝、盲派八字）均无此说。
  本模块以段氏主流（午藏丁己）为默认，可通过常量
  MANGPAI_WU_ZHI_CANG_DING 切换为网络流派（午只藏丁）。
置信度：高
"""
from typing import List, Tuple

from mangpai.objective.constants import CANG_GAN_MANGPAI, MANGPAI_WU_ZHI_CANG_DING


def get_canggan_mangpai(zhi_str: str) -> List[Tuple[str, str]]:
    """获取盲派藏干。

    段建业《段氏理象学》默认使用与传统一致的藏干表：
    午藏丁、己（己禄在午），亥藏壬、甲（不含戊）。
    若常量 MANGPAI_WU_ZHI_CANG_DING=True（网络流派），则午只藏丁。

    Args:
        zhi_str: 地支字符串

    Returns:
        藏干列表，每项为 (天干, 气名) 元组；无效输入返回空列表
    """
    if not zhi_str or zhi_str not in CANG_GAN_MANGPAI:
        return []
    canggan = list(CANG_GAN_MANGPAI[zhi_str])
    # 网络流派：午只藏丁（段氏主流默认午藏丁、己）
    if MANGPAI_WU_ZHI_CANG_DING and zhi_str == '午':
        canggan = [item for item in canggan if item[0] == '丁']
    return canggan
