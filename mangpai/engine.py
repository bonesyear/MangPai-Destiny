"""
mangpai.engine - 盲派排盘编排器（orchestrator）

职责：位于 objective / subjective 两层之上，把"纯规则检测"与"解释性判断"
      串联成完整的 compute_all() 结果。本模块是唯一同时依赖两层的入口：
        objective  <- engine 依赖（确定性检测/分类）
        subjective <- engine 依赖（解释性判断）
      objective 自身不反向依赖 subjective，分层单向。

MangpaiEngine 接收 calc_bazi_full() 的输出，逐模块计算盲派分析结果。
异常策略（H-fix-2a，H11 施工图落地）：关键路径模块（_PROPAGATE_KEYS）
异常包装为 EngineComputeError 传导，上游必须感知；可选模块失败记 warning
并经 _write 回写明确默认值（_MODULE_DEFAULTS），不裸 or {}、不缺键。
"""
import copy
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional

from mangpai.objective import (
    Pillars,
    get_canggan_mangpai, get_changsheng_mangpai,
    get_nayin_mangpai, analyze_nayin_work,
    compute_shensha_ext,
    analyze_binzhu, classify_tiyong, analyze_muku,
    analyze_anhe, analyze_biqi,
    analyze_wood_type, analyze_soil,
    classify_he_types, analyze_virtual_solid,
    analyze_gongshen,
    analyze_shenshu,
    safe_compute_jiaoyun,
    get_gan_xiang, get_zhi_xiang, get_shishen_xiang, get_gongwei_xiang,
)
from mangpai.objective.bazi_calc import calc_bazi_full, GAN, ZHI
from mangpai.objective.jiaoyun import _year_gz
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.zuogong_confirm import analyze_zuogong
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.shipaige import analyze_shipaige
from mangpai.subjective.dayun import analyze_dayun_mangpai
from mangpai.subjective.liunian import analyze_liunian_mangpai
# 领域专辑 + 高级技法模块（objective 检测 ← subjective 判断 ← engine 编排）
from mangpai.subjective.caiming import analyze_caiming
from mangpai.subjective.guanming import analyze_guanming
from mangpai.subjective.hunyin import analyze_hunyin
from mangpai.subjective.xueli import analyze_xueli
from mangpai.subjective.laoyu import analyze_laoyu
from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi
from mangpai.subjective.yunfan import analyze_yunfan, current_fan_slice
from mangpai.subjective.zhiye import analyze_zhiye
from mangpai.subjective.gongmen_wuzhi import analyze_gongmen_wuzhi
from mangpai.subjective.liuqin import analyze_liuqin
from mangpai.subjective.zinv import analyze_zinv
from mangpai.subjective.qianyi import analyze_qianyi
from mangpai.subjective.xiangmao import analyze_xiangmao
from mangpai.subjective.zaihuo import analyze_zaihuo
from mangpai.subjective.zeishen_bushen import analyze_zeishen_bushen
from mangpai.subjective.xiangfa_ops import analyze_xiangfa_ops
from mangpai.subjective.narrative import summarize_engine_result
from mangpai.subjective.yongshen import assess_direction_signals

logger = logging.getLogger(__name__)


class EngineInputError(ValueError):
    """引擎入口输入非法（bazi_data 非 dict / 缺 bazi 四柱 / 非法干支）。

    输入缺陷不可降级——静默接受只会产出垃圾结论，调用方必须修正输入。
    """


class EngineComputeError(RuntimeError):
    """关键路径模块（_PROPAGATE_KEYS）计算失败，包装原始异常传导。

    关键模块静默降级为 {} 会让下游拿空数据算出错误结论（H8 P0：
    _safe_compute 裸 except 全吞），故失败必须让上游知道。
    """

    def __init__(self, key: str, orig: Exception):
        self.key = key
        self.orig = orig
        super().__init__(f'关键模块 {key} 计算失败: {orig}')


# 异常策略分类（H-fix-2a，H11「_safe_compute 模块对照表」逐模块裁定）：
#   传导类（14）：模块间判定链 backbone，输出被其他模块的判定消费，
#     静默降级=隐性误判，必须传导。
#   降级类（29）：可选/展示性模块（含纯数据层、terminal 领域模块、
#     叙事层），失败记 warning + _write 回写明确默认值，主链不受影响。
_PROPAGATE_KEYS = frozenset({
    'shensha',          # 灾祸/婚姻/职业等多模块消费（resolve_shensha 单源）
    'zuogong',          # 做功主线：zhengfan/gongliang/yunfan/运岁全链上游
    'zeishen_bushen',   # gongliang 净制/包制信号源
    'gongliang',        # 功量层：direction/caiming/guanming 消费
    'muku',             # caiming/xiangfa_ops 消费
    'zhengfan',         # 正反局：direction/财/官/职 veto 链消费
    'relations',        # detect_relations：领域模块全量消费
    'yunfan',           # A1 切片入财/官/职/灾祸否决链
    'laoyu',            # direction 总线+灾祸 max_risk 消费
    'direction',        # 方向总线：婚姻/学历/六亲/灾祸只读消费
    'caiming',          # 财命主判定（zhiye base_career 消费）
    'guanming',         # 官命主判定
    'zhiye',            # 职业主判定
    'zaihuo',           # 灾祸主判定（红线域，静默空转=漏判灾祸）
})

# 全模块失败回写默认值（回写契约统一，H8 P1：or {}/is not None/缺键
# 三态 → 显式 is not None 判断 + 失败写明确结构）。正常路径各 analyze_*
# 恒返回非 None 容器，默认值仅在异常降级路径生效。
_MODULE_DEFAULTS: Dict[str, Any] = {
    'canggan': {}, 'chang_sheng': {},
    'nayin': [], 'nayin_work': {},
    'shensha': {}, 'binzhu': {}, 'tiyong': {},
    'zuogong': {}, 'zeishen_bushen': {}, 'gongliang': {}, 'muku': {},
    'anhe': {'anhe': []}, 'biqi': {'biqi': []},
    'wood_type': {}, 'soil': {}, 'he_types': {'he_types': []},
    'virtual_solid': {},
    'zhengfan': {'configuration': '无做功，不论正反', 'type': 'neutral'},
    'shenshu': {}, 'xiangfa': {}, 'gongshen': {},
    'dayun_analysis': {}, 'liunian_analysis': {}, 'jiaoyun_analysis': {},
    'shipaige': {}, 'relations': {}, 'yunfan': {}, 'laoyu': {},
    'direction': {}, 'caiming': {}, 'guanming': {}, 'hunyin': {},
    'xueli': {}, 'xiangfa_ops': {}, 'zhiye': {}, 'gongmen_wuzhi': {},
    'liuqin': {}, 'zinv': {}, 'qianyi': {}, 'xiangmao': {},
    'zaihuo': {}, 'yingqi_subj': {}, 'narrative': '',
}


def _validate_bazi_data(bazi_data: Any) -> Dict[str, Any]:
    """入口校验（H-fix-2a）：畸形输入抛 EngineInputError，禁止静默接受。

    合法输入行为零变化；None/非 dict/缺四柱/非法干支一律明确报错。
    """
    if not isinstance(bazi_data, dict):
        raise EngineInputError(
            f'bazi_data 须为 dict（calc_bazi_full 输出），'
            f'收到 {type(bazi_data).__name__}')
    bazi = bazi_data.get('bazi')
    if not isinstance(bazi, dict) or not bazi:
        raise EngineInputError("bazi_data 缺 'bazi' 四柱字典")
    for k in ('year', 'month', 'day', 'hour'):
        gz = bazi.get(k)
        if (not isinstance(gz, str) or len(gz) != 2
                or gz[0] not in GAN or gz[1] not in ZHI):
            raise EngineInputError(
                f'非法干支 {k} 柱: {gz!r}（须为 2 字合法干支，如 甲子）')
    return bazi


class MangpaiEngine:
    """盲派排盘引擎。

    接收 calc_bazi_full() 的输出作为输入，计算盲派特有的分析结果。

    Args:
        bazi_data: calc_bazi_full() 返回的完整八字数据字典
        shensha_reference: 神煞参考柱，'day' 用日支（盲派，gaoji:7912
            「先以日支为主…年支亦需同查」），'year' 用年支（传统）。
            默认 'day'（F13 配置断路修复）。
    """

    def __init__(self, bazi_data: Dict[str, Any], shensha_reference: str = 'day'):
        bazi = _validate_bazi_data(bazi_data)
        self.shensha_reference = shensha_reference
        self.year_gz: str = bazi.get('year', '')
        self.month_gz: str = bazi.get('month', '')
        self.day_gz: str = bazi.get('day', '')
        self.hour_gz: str = bazi.get('hour', '')

        self.year_gan: str = self.year_gz[0] if len(self.year_gz) >= 1 else ''
        self.year_zhi: str = self.year_gz[1] if len(self.year_gz) >= 2 else ''
        self.month_gan: str = self.month_gz[0] if len(self.month_gz) >= 1 else ''
        self.month_zhi: str = self.month_gz[1] if len(self.month_gz) >= 2 else ''
        self.day_gan: str = self.day_gz[0] if len(self.day_gz) >= 1 else ''
        self.day_zhi: str = self.day_gz[1] if len(self.day_gz) >= 2 else ''
        self.hour_gan: str = self.hour_gz[0] if len(self.hour_gz) >= 1 else ''
        self.hour_zhi: str = self.hour_gz[1] if len(self.hour_gz) >= 2 else ''

        self.gans: List[str] = [self.year_gan, self.month_gan, self.day_gan, self.hour_gan]
        self.zhis: List[str] = [self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi]

        self.shishen: Dict[str, str] = bazi_data.get('shishen', {})
        self.kong_wang = bazi_data.get('kong_wang', {})
        self.di_zhi_relations = bazi_data.get('di_zhi_relations', {})
        self.input_data = bazi_data.get('input', {})
        self.bazi = bazi
        self._raw_bazi_data = bazi_data

        self.pillars = Pillars(
            year_gan=self.year_gan, year_zhi=self.year_zhi,
            month_gan=self.month_gan, month_zhi=self.month_zhi,
            day_gan=self.day_gan, day_zhi=self.day_zhi,
            hour_gan=self.hour_gan, hour_zhi=self.hour_zhi,
        )

    def _safe_compute(self, key: str, func, *args, **kwargs) -> Any:
        """执行单个模块计算（异常策略见 _PROPAGATE_KEYS/_MODULE_DEFAULTS 表注）。

        传导类模块异常 → EngineComputeError 包装抛出（关键失败让上游知道）；
        降级类模块异常 → logger.warning 记录并返回 None（由 _write 回写默认值）。
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if key in _PROPAGATE_KEYS:
                raise EngineComputeError(key, e) from e
            logger.warning(f"模块 {key} 计算失败: {e}", exc_info=True)
            return None

    def _write(self, result: Dict[str, Any], key: str, val: Any) -> None:
        """统一回写契约（H8 P1）：显式 is not None 判断；失败（None）写
        _MODULE_DEFAULTS 的明确结构（深拷贝防共享可变对象），不再裸 or {}
        或缺键。"""
        if val is not None:
            result[key] = val
        else:
            result[key] = copy.deepcopy(_MODULE_DEFAULTS[key])

    def _auto_liunian_list(self) -> List[Dict[str, Any]]:
        """无外部流年注入时，按当前年份自动构造流年柱（前后各一年，共三年）。

        每项 {'gz': 干支, 'year': 公历年}。公历年→年柱干支与 jiaoyun._year_gz
        同口径（公元 4 年甲子，干=(y-4)%10、支=(y-4)%12）。当前年份取系统当年，
        故应期链路在无外部流年数据时仍能基于当下输出。
        """
        try:
            cur_year = datetime.now().year
        except (OSError, OverflowError, ValueError) as e:
            # 白名单化（H8 P1）：仅系统时钟类异常可降级，且记录原因
            logger.warning(f"系统当前年份获取失败，自动流年缺省为空: {e}")
            return []
        return [
            {'gz': _year_gz(y), 'year': y}
            for y in (cur_year, cur_year - 1, cur_year + 1)
        ]

    def _current_age(self) -> Optional[int]:
        """当前虚岁口径年龄（当前年 − 出生年），与 _auto_liunian_list 的
        「当下」锚点同口径；无出生年返回 None。"""
        birth_year = self.input_data.get('year')
        if not birth_year:
            return None
        try:
            return datetime.now().year - int(birth_year)
        except (TypeError, ValueError) as e:
            # 白名单化（H8 P1）：出生年非数值属输入瑕疵，显式 None + 记录原因
            logger.info(f"出生年无法解析为整数，年龄缺省 None: {birth_year!r} ({e})")
            return None

    def _current_dayun(self, dy_list: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """定位「当下」所处大运：按当前年龄（当前年 − 出生年）匹配
        start_age/end_age 区间，与 _auto_liunian_list 的「当下」锚点
        （系统当前年）同口径。

        回退策略（保持旧行为/书例兼容）：无出生年、条目缺 start_age、
        或年龄未入任何区间（书例只喂单步相关大运）时取首步大运；
        年龄超出末步区间时取末步（不再错锚童年首运）。
        """
        if not dy_list:
            return None

        def _pair(entry: Any) -> Optional[Dict[str, str]]:
            gz = entry.get('gz', '') if isinstance(entry, dict) else ''
            if len(gz) < 2:
                return None
            pair: Dict[str, Any] = {'gan': gz[0], 'zhi': gz[1]}
            # K5：透传起讫年龄（liunian 分看/统看定位大运第几年用）；
            # 旧消费方只读 gan/zhi，附加键不改变其行为
            if isinstance(entry, dict):
                for k in ('start_age', 'end_age'):
                    if entry.get(k) is not None:
                        pair[k] = entry[k]
            return pair

        age = self._current_age()
        if age is not None:
            first_sa = last_ea = None
            for entry in dy_list:
                if not isinstance(entry, dict):
                    continue
                sa = entry.get('start_age')
                # H-fix-2a 守卫：非数值 start_age / 显式 end_age=None（旧码
                # TypeError 击穿 compute_all，engine.py:179 P1）显式跳过/缺省
                if not isinstance(sa, (int, float)) or isinstance(sa, bool):
                    continue
                ea = entry.get('end_age')
                if ea is None:
                    ea = sa + 10
                elif not isinstance(ea, (int, float)) or isinstance(ea, bool):
                    continue
                if first_sa is None:
                    first_sa = sa
                last_ea = ea
                if sa <= age < ea:
                    pair = _pair(entry)
                    if pair:
                        return pair
            # 超出末步区间 → 末步；未起运（童年）→ 首步（旧行为）
            if last_ea is not None and age >= last_ea:
                pair = _pair(dy_list[-1])
                if pair:
                    return pair
        return _pair(dy_list[0])

    def compute_all(self) -> Dict[str, Any]:
        """计算全部盲派分析结果。

        异常策略（H-fix-2a）：关键路径模块（_PROPAGATE_KEYS）失败抛
        EngineComputeError 传导；可选模块失败记 warning 并回写明确默认值，
        单个可选模块失败不影响其他模块。

        Returns:
            包含所有盲派分析模块结果的字典
        """
        result: Dict[str, Any] = {}
        p = self.pillars

        result['bazi'] = self.bazi
        result['input'] = self.input_data

        canggan_val = self._safe_compute('canggan', lambda: {
            z: get_canggan_mangpai(z) for z in self.zhis if z
        })
        self._write(result, 'canggan', canggan_val)

        cs_val = self._safe_compute('chang_sheng', lambda: {
            f'{pk}_zhi': get_changsheng_mangpai(self.day_gan, z)
            for pk, z in zip(['year', 'month', 'day', 'hour'], self.zhis) if z
        })
        self._write(result, 'chang_sheng', cs_val)

        pillar_gzs = [p.year_gz, p.month_gz, p.day_gz, p.hour_gz]
        self._write(result, 'nayin', self._safe_compute('nayin', lambda: [
            get_nayin_mangpai(gz) for gz in pillar_gzs if gz
        ]))
        self._write(result, 'nayin_work', self._safe_compute(
            'nayin_work', analyze_nayin_work, [gz for gz in pillar_gzs if gz]
        ))

        self._write(result, 'shensha', self._safe_compute(
            'shensha', compute_shensha_ext, self.day_gan, self.zhis,
            reference=self.shensha_reference,
        ))
        # 神煞单源透传（R2 复核后口径）：hunyin/zhiye/gongmen_wuzhi/zaihuo/
        # laoyu 经 resolve_shensha 优先取本值、随 shensha_reference 联动
        # （默认 'day'，F13）；xiangfa_ops 直接消费本值（engine.py:566）；
        # caiming/guanming 仅有预留形参、尚未消费（caiming.py:1803、
        # guanming.py:906）；liuqin.py:872 仍就地重算（配置断路备案，R2 P2）。

        self._write(result, 'binzhu', self._safe_compute(
            'binzhu', analyze_binzhu,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
            p.year_gan, p.month_gan, p.day_gan, p.hour_gan,
        ))

        self._write(result, 'tiyong', self._safe_compute(
            'tiyong', classify_tiyong, self.shishen, self.day_gan
        ))

        zg = self._safe_compute(
            'zuogong', analyze_zuogong,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
            kong_wang=self.kong_wang,
        )
        self._write(result, 'zuogong', zg)
        zg = result['zuogong']

        # 贼神捕神/包制/冲链（gongliang 上游信号源，只读消费 zuogong work_actions）。
        # 先于 gongliang 计算，使其净制/包制/冲链信号可被 gongliang 二次消费（zhi_jing
        # 增强 + 参考录入）。原局 zuogong 数据已就绪（zg）。
        zb_res = self._safe_compute(
            'zeishen_bushen', analyze_zeishen_bushen,
            self.day_gan, self.gans, self.zhis, zg,
        )
        if zb_res is None:
            zb_res = {}

        # 段氏四层功量（与 zuogong.work_level 并行的富贵量级体系，
        # 消费 zuogong 做功数据做二次量化，1-4 层；消费 zeishen_bushen 净制/包制信号）
        self._write(result, 'gongliang', self._safe_compute(
            'gongliang', analyze_gongliang,
            zg, self.day_gan, self.gans, self.zhis,
            zeishen_bushen_result=zb_res or None,
        ))

        self._write(result, 'muku', self._safe_compute(
            'muku', analyze_muku, self.zhis, self.gans))

        # F1 标注：anhe/biqi 两结果 prompt-only（进 selector→prompt，无任何
        # Python 判定逻辑消费其内容；主观层暗合走 zuogong work_actions 或自算）。
        self._write(result, 'anhe', self._safe_compute(
            'anhe', analyze_anhe,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ))

        self._write(result, 'biqi', self._safe_compute(
            'biqi', analyze_biqi,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ))

        self._write(result, 'wood_type', self._safe_compute(
            'wood_type', analyze_wood_type,
            p.day_gan,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ))

        self._write(result, 'soil', self._safe_compute(
            'soil', analyze_soil,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ))

        self._write(result, 'he_types', self._safe_compute(
            'he_types', classify_he_types,
            p.day_zhi,
            p.year_zhi, p.month_zhi, p.hour_zhi,
            p.year_gan, p.month_gan, p.day_gan, p.hour_gan,
        ))

        # （F1 批删除 result['zihe'] 死输出：guanming/yongshen/caiming 全部
        #  就地自调 detect_zihe，无任何模块读 result['zihe']，且不在 selectors
        #  不进 payload——engine↔模块双轨第四例，批10 审计定。）

        self._write(result, 'virtual_solid', self._safe_compute(
            'virtual_solid', analyze_virtual_solid,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
        ))

        self._write(result, 'zhengfan', self._safe_compute(
            'zhengfan', analyze_zhengfan,
            zg.get('work_actions', []), zg.get('day_he_type'),
            self.gans, self.zhis,
        ))

        self._write(result, 'shenshu', self._safe_compute(
            'shenshu', analyze_shenshu,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
        ))

        xiangfa_val = self._safe_compute('xiangfa', lambda: {
            'gan_xiang': {g: get_gan_xiang(g) for g in self.gans if g},
            'zhi_xiang': {z: get_zhi_xiang(z) for z in self.zhis if z},
            'shishen_xiang': {k: get_shishen_xiang(v) for k, v in self.shishen.items() if v},
            'gongwei_xiang': {
                'year': get_gongwei_xiang('年柱'),
                'month': get_gongwei_xiang('月柱'),
                'day': get_gongwei_xiang('日柱'),
                'hour': get_gongwei_xiang('时柱'),
            },
        })
        self._write(result, 'xiangfa', xiangfa_val)

        # 宫身（宫位六亲）分析：星宫关系/夫妻宫专断/宫位互动，基于 xiangfa 的宫位象
        self._write(result, 'gongshen', self._safe_compute(
            'gongshen', analyze_gongshen,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
            gender=self.input_data.get('gender', '男'),
        ))

        result['kong_wang'] = self.kong_wang
        result['di_zhi_relations'] = self.di_zhi_relations

        # 大运数据键名适配：calc_bazi_full 返回 'da_yun'（dict，内含 'dayun' 列表）；
        # 兼容旧调用方直传 'dayun'（dict 或 list）。优先取 da_yun。
        dayun_data = (self._raw_bazi_data.get('da_yun')
                      or self._raw_bazi_data.get('dayun') or {})

        dy_list = []
        start_age = None
        if isinstance(dayun_data, dict):
            dy_list = dayun_data.get('dayun', [])
            start_age = dayun_data.get('start_age')
        elif isinstance(dayun_data, list):
            dy_list = dayun_data

        if dy_list:
            fei_shen = zg.get('fei_shen', []) if zg else []
            self._write(result, 'dayun_analysis', self._safe_compute(
                'dayun_analysis', analyze_dayun_mangpai,
                dy_list, self.gans, self.zhis, self.day_gan,
                natal_fei_shen=fei_shen,
                kong_wang=self.kong_wang,
            ))

        liunian_data = self._raw_bazi_data.get('liunian')
        if not liunian_data and self.input_data:
            liunian_data = self.input_data.get('liunian')

        # 无外部流年注入时，按「当前年份」自动构造流年柱（前后各一年，
        # 共三年），使 liunian_analysis 在无外部数据时也能基于当下输出。
        # 大运/流年应期链路下游（yunfan/hunyingqi/hunyin）随之有 current 锚点。
        if not liunian_data and self.input_data.get('year'):
            liunian_data = self._auto_liunian_list()
            if liunian_data:
                self._auto_liunian_injected = True
                # R2 P3 备案：本属性仅此处条件赋值、__init__ 未初始化（读点
                # engine.py:497 getattr 兜底）；同实例复调 compute_all 会残留
                # True，无风险路径，文档批不初始化引擎仅标注。

        if liunian_data:
            ln_list = liunian_data if isinstance(liunian_data, list) else liunian_data.get('liunian', [])
            if ln_list:
                fei_shen = zg.get('fei_shen', []) if zg else []
                # 当下大运按当前年龄定位（与自动流年同锚点），非首步大运
                current_dy = self._current_dayun(dy_list) if isinstance(dy_list, list) else None
                self._write(result, 'liunian_analysis', self._safe_compute(
                    'liunian_analysis', analyze_liunian_mangpai,
                    ln_list, self.gans, self.zhis, self.day_gan,
                    current_dayun=current_dy,
                    natal_fei_shen=fei_shen,
                    kong_wang=self.kong_wang,
                    gender=self.input_data.get('gender'),
                    birth_year=self.input_data.get('year'),
                ))

        # 交运时间计算（用年柱纳音五行定交运，大运序列从月柱起）
        # F1 标注：jiaoyun_analysis 仅进 _build_summary 交运行，不在 selectors
        # 不进 payload（LLM 见不到交运时刻本体，批10 P1 备案）。
        if self.input_data.get('year') and self.month_gz:
            self._write(result, 'jiaoyun_analysis', self._safe_compute(
                'jiaoyun_analysis', safe_compute_jiaoyun,
                self.input_data.get('year', 2000),
                self.month_gz,
                dayun_list=dy_list,
                start_age=start_age,
            ))

        # 郑氏十排歌扩展分析（断语集锦 + 方法论）
        self._write(result, 'shipaige', self._safe_compute(
            'shipaige', analyze_shipaige,
            self.day_gan, self.day_zhi,
            self.year_gan, self.year_zhi,
            self.month_gan, self.month_zhi,
            self.hour_gan, self.hour_zhi,
        ))

        # ──────────────────────────────────────────────────────────────
        # 领域专辑 + 高级技法模块（subjective 判断层）
        # 一次性 detect_relations 供各领域模块复用，避免重复扫描四柱关系。
        # 各 analyze_* 自带缺省自调（relations/gongliang/muku/shensha 缺省回退），
        # 此处显式透传 engine 已算结果，做只读消费、不反写功量层。
        # ──────────────────────────────────────────────────────────────
        relations = self._safe_compute(
            'relations', detect_relations,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            self.kong_wang,
        )
        self._write(result, 'relations', relations)
        relations = result['relations']

        gl = result['gongliang']
        zg = result['zuogong']

        # 当前大运/流年干支（大运按当前年龄定位，与 liunian_analysis 之
        # current_dayun 同一「当下」锚点；无锚点时回退首步大运/首流年）
        cur_dy_gan, cur_dy_zhi = '', ''
        _cur_dy = self._current_dayun(dy_list) if isinstance(dy_list, list) else None
        if _cur_dy:
            cur_dy_gan, cur_dy_zhi = _cur_dy['gan'], _cur_dy['zhi']

        cur_ln_list = []
        if isinstance(liunian_data, list):
            cur_ln_list = liunian_data
        elif isinstance(liunian_data, dict):
            cur_ln_list = liunian_data.get('liunian', [])
        cur_ln_gan, cur_ln_zhi = '', ''
        if cur_ln_list:
            gz = (cur_ln_list[0].get('gz', '') if isinstance(cur_ln_list[0], dict) else '')
            if gz and len(gz) >= 2:
                cur_ln_gan, cur_ln_zhi = gz[0], gz[1]

        # 岁运反局：原局做功数据透传（缺省时 analyze_yunfan 自调 zuogong）。
        # 前置于 caiming/guanming/zhiye：其方向否决链（A1）消费「当前运岁」切片。
        self._write(result, 'yunfan', self._safe_compute(
            'yunfan', analyze_yunfan,
            self.gans, self.zhis, self.day_gan,
            dayun_list=dy_list,
            liunian_list=cur_ln_list,
            current_dayun={'gan': cur_dy_gan, 'zhi': cur_dy_zhi} if cur_dy_gan else None,
            natal_work_actions=zg.get('work_actions') if zg else None,
            natal_gong_shen=zg.get('gong_shen') if zg else None,
            natal_fei_shen=zg.get('fei_shen') if zg else None,
            natal_work_types=zg.get('work_types') if zg else None,
            day_he_type=zg.get('day_he_type') if zg else None,
            kong_wang=self.kong_wang,
        ))

        # A1 岁运反局切片：仅显式输入的运岁入否决链——大运须 da_yun 实给
        # （dy_list 非空），流年须外部注入（自动构造的三岁窗口仅作展示锚点，
        # 启发式命中率高，入否决会污染终身财命/官命口径）。
        yunfan_slice = current_fan_slice(
            result['yunfan'],
            f'{cur_dy_gan}{cur_dy_zhi}' if cur_dy_gan else '',
            include_dayun=bool(dy_list),
            include_liunian=bool(cur_ln_list) and not getattr(self, '_auto_liunian_injected', False),
        )

        # 修批D（R2 P2 direction 重算簇）：laoyu 提前算一次，与 engine 已算的
        # zhengfan 一起透传 direction 总线及 caiming/guanming/zhiye 三消费方
        # （原各自 _ensure_zhengfan/_ensure_laoyu 重跑——单次 compute_all
        # analyze_zuogong≈6 遍、analyze_laoyu≈6 遍，纯算力浪费）。
        # result['laoyu'] 键序不变（仍于原位置赋值）；calib 等直调方缺省
        # 仍走 yongshen._ensure_* 自算，口径不变。
        laoyu_res = self._safe_compute(
            'laoyu', analyze_laoyu,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            shensha_result=result.get('shensha'),
        )
        if laoyu_res is None:
            laoyu_res = {}

        # A3 方向总线：yongshen.assess_direction_signals 全引擎统一计算一次，
        # 透传各领域模块（hunyin/liuqin/xueli/zaihuo/gongmen_wuzhi 只读消费；
        # caiming/guanming/zhiye 已有内部否决链，口径同源）。
        # F1 标注：result['direction'] 仅模块间透传——payload(selectors)/
        # _build_summary/narrative 三出口均不可见（批10 备案，非纯死勿删）。
        self._write(result, 'direction', self._safe_compute(
            'direction', assess_direction_signals,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            zhengfan_result=result.get('zhengfan'),
            laoyu_result=laoyu_res,
            yunfan_result=yunfan_slice,
        ))

        self._write(result, 'caiming', self._safe_compute(
            'caiming', analyze_caiming,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            muku_result=result.get('muku'),
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
            zhengfan_result=result.get('zhengfan'),
            laoyu_result=laoyu_res,
        ))

        self._write(result, 'guanming', self._safe_compute(
            'guanming', analyze_guanming,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
            kong_wang=self.kong_wang,
            zhengfan_result=result.get('zhengfan'),
            laoyu_result=laoyu_res,
        ))

        self._write(result, 'hunyin', self._safe_compute(
            'hunyin', analyze_hunyin,
            self.day_gan, self.gans, self.zhis,
            self.input_data.get('gender', '男'),
            dayun_gan=cur_dy_gan, dayun_zhi=cur_dy_zhi,
            liunian_gan=cur_ln_gan, liunian_zhi=cur_ln_zhi,
            relations=relations,
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
        ))

        self._write(result, 'xueli', self._safe_compute(
            'xueli', analyze_xueli,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            direction_result=result.get('direction'),
        ))

        result['laoyu'] = laoyu_res  # 修批D：提前算于 direction 总线之前（键序不变）

        # 贼神捕神/包制/冲链：已于 gongliang 之前算得（zb_res，供 gongliang 二次
        # 消费），此处复用同一份，避免重复扫描四柱。
        result['zeishen_bushen'] = zb_res

        # 象法九原则操作层（消费 muku/shensha；缺省自调客观检测）
        # 修批A②：透传引擎已算的 zeishen_bushen 结果（zb_res），换象净制口径单源化
        self._write(result, 'xiangfa_ops', self._safe_compute(
            'xiangfa_ops', analyze_xiangfa_ops,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            muku_result=result.get('muku'),
            shensha_result=result.get('shensha'),
            zeishen_result=zb_res,
        ))

        self._write(result, 'zhiye', self._safe_compute(
            'zhiye', analyze_zhiye,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
            caiming_result=result.get('caiming'),  # M2 基础职业类目消费财命tier/取财法
            zhengfan_result=result.get('zhengfan'),
            laoyu_result=laoyu_res,
        ))

        # 修批A③：gongmen_wuzhi 正式弃用落 payload 通道——selectors 已摘除
        # （is_wuzhi 98.8% 恒真零信息量，R5 block-4），result 键保留供内部存档/
        # 测试消费，不进 LLM。
        self._write(result, 'gongmen_wuzhi', self._safe_compute(
            'gongmen_wuzhi', analyze_gongmen_wuzhi,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
        ))

        self._write(result, 'liuqin', self._safe_compute(
            'liuqin', analyze_liuqin,
            self.day_gan, self.gans, self.zhis,
            self.input_data.get('gender', '男'),
            relations=relations,
            direction_result=result.get('direction'),
        ))

        # D6b 子女岁运应期 + 借腹 marker（消费 liuqin 已算星宫定位，不重造；
        # 岁运序列=engine 已有 dy_list/cur_ln_list 供给，缺省空转）
        self._write(result, 'zinv', self._safe_compute(
            'zinv', analyze_zinv,
            self.day_gan, self.gans, self.zhis,
            self.input_data.get('gender', '男'),
            relations=relations,
            liuqin_result=result.get('liuqin'),
            dayun_list=dy_list if isinstance(dy_list, list) else [],
            liunian_list=cur_ln_list,
        ))

        # 缺口批1 迁移/远行 marker + 应期窗（马星查法复用 shensha._YI_MA，
        # 岁运序列=engine 已有 dy_list/cur_ln_list 供给，缺省空转；
        # 措辞上限「迁移/远行」，不出出国级断语——归档 §一）
        self._write(result, 'qianyi', self._safe_compute(
            'qianyi', analyze_qianyi,
            self.day_gan, self.gans, self.zhis,
            dayun_list=dy_list if isinstance(dy_list, list) else [],
            liunian_list=cur_ln_list,
        ))

        # 缺口批2 相貌 marker 层（纯 marker 无判定无档位，供叙事层消费；
        # wood_type 复用 result 已有键作活木判据；措辞红线不出「美/丑/帅」
        # 结论词——归档 §二.3）
        self._write(result, 'xiangmao', self._safe_compute(
            'xiangmao', analyze_xiangmao,
            self.day_gan, self.gans, self.zhis,
            gender=self.input_data.get('gender', ''),
            wood_type=result.get('wood_type') or {},
        ))

        # 灾祸（消费 yunfan A1 切片：detect_siwang 取岁运反局联动信号——
        # F14 修复批7/批10 A1 破口，与 caiming/guanming/zhiye 同口径；
        # F14 接入 laoyu_result：牢狱入灾祸 max_risk，ch11 牢狱为灾祸之首）
        self._write(result, 'zaihuo', self._safe_compute(
            'zaihuo', analyze_zaihuo,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            yunfan_result=yunfan_slice,
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
            laoyu_result=result.get('laoyu'),
        ))

        # 综合应期（原局=车，大运=路，流年=触发点；传 age 定位大限柱，
        # 三要素交集名副其实；无出生年则大限缺省空转）
        self._write(result, 'yingqi_subj', self._safe_compute(
            'yingqi_subj', infer_comprehensive_yingqi,
            self.day_gan, self.gans, self.zhis,
            cur_dy_gan, cur_dy_zhi, cur_ln_gan, cur_ln_zhi,
            age=self._current_age(),
        ))

        # 郝金阳叙事层：把引擎结构化结论压成一行【引擎结论】（软依赖，
        # 仅 summarize，不调 LLM；render_hao_narrative 留给调用方按需触发）
        self._write(result, 'narrative', self._safe_compute(
            'narrative', summarize_engine_result, result
        ))

        result['summary'] = self._build_summary(result)

        return result

    def _build_summary(self, result: Dict[str, Any]) -> str:
        """构建摘要字符串。"""
        parts: List[str] = []

        parts.append(f"日主：{self.day_gan}{self.day_zhi}")

        zg = result.get('zuogong', {})
        work_types = zg.get('work_types', [])
        if work_types:
            parts.append(f"做功类型：{'、'.join(work_types)}")
            parts.append(f"做功层次：{zg.get('work_tier', '')}（Level {zg.get('work_level', 0)}）")
            parts.append(f"做功效率：{zg.get('work_efficiency', '')}")
        else:
            parts.append("做功：无功")

        # 暗合做功提示
        work_actions = zg.get('work_actions', [])
        if any(wa.get('type') == '暗合' for wa in work_actions):
            parts.append('含暗合')

        zf = result.get('zhengfan', {})
        if zf.get('type') != 'neutral':
            parts.append(f"正反局：{zf.get('configuration', '')}")

        ss_ge = result.get('shenshu', {})
        if ss_ge.get('summary'):
            parts.append(f"十神歌诀：{ss_ge['summary']}")

        ty = result.get('tiyong', {})
        parts.append(f"体用：体{ty.get('ti_count', 0)}用{ty.get('yong_count', 0)}")

        wt = result.get('wood_type', {})
        if wt.get('is_wood'):
            parts.append(f"木性：{wt.get('wood_type', '')}")

        ss = result.get('shensha', {})
        ss_parts = []
        for name in ['羊刃', '劫煞', '灾煞', '孤辰', '寡宿', '桃花', '驿马',
                     '天乙贵人', '文昌', '华盖']:
            s = ss.get(name, {})
            if s.get('in_pillars'):
                ss_parts.append(f"{name}在{'、'.join(s['in_pillars'])}")
        if ss_parts:
            parts.append('、'.join(ss_parts))

        # 穿的特殊影响提示（摘要末尾）
        if zg.get('has_severe_harm'):
            parts.append('⚠️日柱被穿，做功质量严重受损')
        elif zg.get('has_active_harm'):
            parts.append('日柱穿他柱，做功有暗损')

        # 大运分析摘要
        dy = result.get('dayun_analysis', {})
        if dy.get('summary'):
            parts.append(f"大运：{dy['summary']}")

        # 交运时间摘要
        jy = result.get('jiaoyun_analysis', {})
        if isinstance(jy, dict) and jy.get('rule'):
            nx = jy.get('next_jiaoyun')
            if nx:
                parts.append(
                    f"交运：{jy['rule']}，下一交运{nx.get('gz', '')}"
                    f"（{nx.get('jiaoyun_iso', '')}）"
                )
            else:
                parts.append(f"交运：{jy['rule']}")

        return '；'.join(parts)


def calc_mangpai_full(
    year: int, month: int, day: int, hour: int, minute: int,
    gender: str, city_lon: float,
    yin_method: str = 'same_as_yang',
    shensha_reference: str = 'day',
) -> Dict[str, Any]:
    """盲派完整排盘便捷函数。

    内部调用 calc_bazi_full 计算四柱，再用 MangpaiEngine 计算盲派分析。

    Args:
        year: 公历年
        month: 公历月
        day: 公历日
        hour: 时（0-23）
        minute: 分（0-59）
        gender: '男' 或 '女'
        city_lon: 城市经度
        yin_method: 阴干起运方向，默认 'same_as_yang'（盲派阴阳同生同死）。
            （F1 标注：透传形参，calc_bazi_full 接收不用，全链路无消费方）
        shensha_reference: 神煞参考柱，默认 'day'（F13 起；gaoji:7912
            日支为主、年支同查，year_ref/day_ref 子键恒在）

    Returns:
        完整盲派排盘结果
    """
    bazi_data = calc_bazi_full(
        year, month, day, hour, minute, gender, city_lon,
        yin_method=yin_method,
        shensha_reference=shensha_reference,
    )
    engine = MangpaiEngine(bazi_data, shensha_reference=shensha_reference)
    return engine.compute_all()


__all__ = [
    'MangpaiEngine', 'calc_mangpai_full',
    'EngineInputError', 'EngineComputeError',
]
