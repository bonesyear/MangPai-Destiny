"""
tiyong - 盲派体用分类

理论来源：段建业《段氏理象学》体用篇
核心思想：
  体 = 日主 + 印（正印/偏印）+ 比劫（比肩/劫财）+ 禄 -- 自我工具
  用 = 财（正财/偏财）+ 官杀（正官/七杀）-- 追求目标
  中性 = 食伤（食神/伤官）-- 日主所生之工具，居体用之间：
    食神 bias=+体（性顺，略偏体），伤官 bias=+用（性逆，略偏用）。
  体用配合做功，看用什么体去追求什么用。

  禄属体：禄为日干在地支的临官位（同我，比劫之属），故属体；然禄是地支
    位、非十神，本模块按天干十神分类不直接判定，禄由 zuogong 侧补判
    （地支禄位 / _tiyong_of 五行生克）。

  食伤两层归属：粗分上食伤为日主所生之工具（食伤生财、食伤制杀），属自我
    工具体域，故仍列于 _TI_SHISHEN 供 zuogong 等粗分补判；细分上食伤居体
    用之间为中性，classify_tiyong 以 category='中性'+bias 标注，不再硬归体
    （旧实现把食伤全归体，即此处分流）。bias 计入 ti_count/yong_count
    （食神入 ti、伤官入 yong），neutral_count 单独计中性数，
    保留 ti/yong/neutral 三分计数。
置信度：高
"""
from typing import Dict

# 体域（粗分）：印 + 比劫 + 日主 + 食伤。食伤为日主所生之工具，属自我工具
# 之体域，故仍列于此（供 zuogong 等粗分补判、§8 体域归属校验）；细分上
# 食伤为中性，由 _NEUTRAL_BIAS 在 classify_tiyong 内先行分流。
_TI_SHISHEN = {'正印', '偏印', '比肩', '劫财', '日主', '食神', '伤官'}
# 用：财 + 官杀（追求目标）
_YONG_SHISHEN = {'正财', '偏财', '正官', '七杀'}
# 中性（细分）：食伤居体用之间，带偏向。食神 bias='体'（略偏体），
# 伤官 bias='用'（略偏用）。bias 计入对应 ti/yong 计数，见 classify_tiyong。
_NEUTRAL_BIAS = {'食神': '体', '伤官': '用'}


def classify_tiyong(shishen: Dict[str, str], day_gan: str) -> Dict:
    """分类体用（体/用/中性 三分）。

    体 = 印 + 比劫 + 日主 + 禄（自我工具；禄由 zuogong 侧补判）
    用 = 财 + 官杀（追求目标）
    中性 = 食伤（食神 bias=+体、伤官 bias=+用）

    中性食伤虽居体用之间，仍带偏向：食神略偏体、伤官略偏用，故 bias 计入
    ti_count/yong_count（食神入 ti、伤官入 yong），neutral_count 单独统计
    中性总数，保留 ti/yong/neutral 三分计数。

    Args:
        shishen: 十神字典，如 {'year_gan': '正财', ...}
        day_gan: 日干

    Returns:
        体用分类结果，含各柱分类（category + bias）和
        ti_count/yong_count/neutral_count
    """
    result: Dict = {}
    ti_count = 0
    yong_count = 0
    neutral_count = 0

    for key, ss in shishen.items():
        # 先判中性（食伤）：食伤虽在 _TI_SHISHEN 体域粗分集内，细分为中性，
        # 须先于 _TI_SHISHEN 判定，否则会被归为体（即旧实现“食伤全归体”之 bug）。
        if ss in _NEUTRAL_BIAS:
            category = '中性'
            bias = _NEUTRAL_BIAS[ss]
            neutral_count += 1
            # 中性食伤带偏向：偏向一侧计入 ti/yong 计数（食神入 ti、伤官入 yong）
            if bias == '体':
                ti_count += 1
            else:  # bias == '用'
                yong_count += 1
        elif ss in _TI_SHISHEN:
            category = '体'
            bias = None
            ti_count += 1
        elif ss in _YONG_SHISHEN:
            category = '用'
            bias = None
            yong_count += 1
        else:
            category = '未知'
            bias = None

        result[key] = {
            'shishen': ss,
            'category': category,
            'bias': bias,
        }

    result['ti_count'] = ti_count
    result['yong_count'] = yong_count
    result['neutral_count'] = neutral_count
    # 键名用 tiyong_day_gan 而非 day_gan：shishen 含 'day_gan'（日主十神）时，
    # 上述循环已把该柱分类写入 result['day_gan']；若此处再用 'day_gan' 会覆盖之，
    # 丢失日主体用分类。真实排盘 shishen 含 day_gan，verify 用空 shishen={} 测不出。
    result['tiyong_day_gan'] = day_gan
    return result
