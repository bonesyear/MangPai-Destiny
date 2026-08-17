"""
mangpai.engine - 盲派排盘编排器（orchestrator）

职责：位于 objective / subjective 两层之上，把"纯规则检测"与"解释性判断"
      串联成完整的 compute_all() 结果。本模块是唯一同时依赖两层的入口：
        objective  <- engine 依赖（确定性检测/分类）
        subjective <- engine 依赖（解释性判断）
      objective 自身不反向依赖 subjective，分层单向。

MangpaiEngine 接收 calc_bazi_full() 的输出，逐模块计算盲派分析结果，
每模块独立 try/except，单个失败不影响其他。
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any, List

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
from mangpai.objective.bazi_calc import calc_bazi_full
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
from mangpai.subjective.zaihuo import analyze_zaihuo
from mangpai.subjective.zeishen_bushen import analyze_zeishen_bushen
from mangpai.subjective.xiangfa_ops import analyze_xiangfa_ops
from mangpai.subjective.narrative import summarize_engine_result

logger = logging.getLogger(__name__)


class MangpaiEngine:
    """盲派排盘引擎。

    接收 calc_bazi_full() 的输出作为输入，计算盲派特有的分析结果。

    Args:
        bazi_data: calc_bazi_full() 返回的完整八字数据字典
        shensha_reference: 神煞参考柱，'year' 用年支（传统），
            'day' 用日支（盲派）。默认 'year'。
    """

    def __init__(self, bazi_data: Dict[str, Any], shensha_reference: str = 'year'):
        bazi = bazi_data.get('bazi', {})
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
        """安全执行单个模块计算，捕获异常并记录。"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"模块 {key} 计算失败: {e}", exc_info=True)
            return None

    def _auto_liunian_list(self) -> List[Dict[str, Any]]:
        """无外部流年注入时，按当前年份自动构造流年柱（前后各一年，共三年）。

        每项 {'gz': 干支, 'year': 公历年}。公历年→年柱干支与 jiaoyun._year_gz
        同口径（公元 4 年甲子，干=(y-4)%10、支=(y-4)%12）。当前年份取系统当年，
        故应期链路在无外部流年数据时仍能基于当下输出。
        """
        from datetime import datetime
        from mangpai.objective.jiaoyun import _year_gz
        try:
            cur_year = datetime.now().year
        except Exception:
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
            from datetime import datetime
            return datetime.now().year - int(birth_year)
        except Exception:
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
                if sa is None:
                    continue
                ea = entry.get('end_age', sa + 10)
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

        每个模块独立 try/except，单个模块失败不影响其他模块。

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
        if canggan_val is not None:
            result['canggan'] = canggan_val

        cs_val = self._safe_compute('chang_sheng', lambda: {
            f'{pk}_zhi': get_changsheng_mangpai(self.day_gan, z)
            for pk, z in zip(['year', 'month', 'day', 'hour'], self.zhis) if z
        })
        if cs_val is not None:
            result['chang_sheng'] = cs_val

        pillar_gzs = [p.year_gz, p.month_gz, p.day_gz, p.hour_gz]
        result['nayin'] = self._safe_compute('nayin', lambda: [
            get_nayin_mangpai(gz) for gz in pillar_gzs if gz
        ]) or []
        result['nayin_work'] = self._safe_compute(
            'nayin_work', analyze_nayin_work, [gz for gz in pillar_gzs if gz]
        ) or {}

        result['shensha'] = self._safe_compute(
            'shensha', compute_shensha_ext, self.day_gan, self.zhis,
            reference=self.shensha_reference,
        ) or {}
        # 已知（端到端断路审计·部分覆盖项）：shensha 透传给 caiming/guanming/
        # hunyin/zhiye/gongmen_wuzhi/zaihuo（经 resolve_shensha 优先取本值、缺省才
        # 就地重算），随本处 shensha_reference 联动；xiangfa/xiangfa_ops/zeishen 等
        # 其余下游仍各自就地重算神煞/取象（默认 'year'，不随本处 reference 联动）。

        result['binzhu'] = self._safe_compute(
            'binzhu', analyze_binzhu,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
            p.year_gan, p.month_gan, p.day_gan, p.hour_gan,
        ) or {}

        result['tiyong'] = self._safe_compute(
            'tiyong', classify_tiyong, self.shishen, self.day_gan
        ) or {}

        zg = self._safe_compute(
            'zuogong', analyze_zuogong,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
            kong_wang=self.kong_wang,
        )
        if zg is not None:
            result['zuogong'] = zg
        else:
            zg = {}

        # 贼神捕神/包制/冲链（gongliang 上游信号源，只读消费 zuogong work_actions）。
        # 先于 gongliang 计算，使其净制/包制/冲链信号可被 gongliang 二次消费（zhi_jing
        # 增强 + 参考录入）。原局 zuogong 数据已就绪（zg）。
        zb_res = self._safe_compute(
            'zeishen_bushen', analyze_zeishen_bushen,
            self.day_gan, self.gans, self.zhis, zg,
        ) or {}

        # 段氏四层功量（与 zuogong.work_level 并行的富贵量级体系，
        # 消费 zuogong 做功数据做二次量化，1-4 层；消费 zeishen_bushen 净制/包制信号）
        result['gongliang'] = self._safe_compute(
            'gongliang', analyze_gongliang,
            zg, self.day_gan, self.gans, self.zhis,
            zeishen_bushen_result=zb_res or None,
        ) or {}

        result['muku'] = self._safe_compute('muku', analyze_muku, self.zhis, self.gans) or {}

        # F1 标注：anhe/biqi 两结果 prompt-only（进 selector→prompt，无任何
        # Python 判定逻辑消费其内容；主观层暗合走 zuogong work_actions 或自算）。
        anhe_val = self._safe_compute(
            'anhe', analyze_anhe,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        )
        result['anhe'] = anhe_val or {'anhe': []}

        biqi_val = self._safe_compute(
            'biqi', analyze_biqi,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        )
        result['biqi'] = biqi_val or {'biqi': []}

        result['wood_type'] = self._safe_compute(
            'wood_type', analyze_wood_type,
            p.day_gan,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ) or {}

        result['soil'] = self._safe_compute(
            'soil', analyze_soil,
            p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi,
        ) or {}

        he_val = self._safe_compute(
            'he_types', classify_he_types,
            p.day_zhi,
            p.year_zhi, p.month_zhi, p.hour_zhi,
            p.year_gan, p.month_gan, p.day_gan, p.hour_gan,
        )
        result['he_types'] = he_val or {'he_types': []}

        # （F1 批删除 result['zihe'] 死输出：guanming/yongshen/caiming 全部
        #  就地自调 detect_zihe，无任何模块读 result['zihe']，且不在 selectors
        #  不进 payload——engine↔模块双轨第四例，批10 审计定。）

        result['virtual_solid'] = self._safe_compute(
            'virtual_solid', analyze_virtual_solid,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
        ) or {}

        result['zhengfan'] = self._safe_compute(
            'zhengfan', analyze_zhengfan,
            zg.get('work_actions', []), zg.get('day_he_type'),
            self.gans, self.zhis,
        ) or {'configuration': '无做功，不论正反', 'type': 'neutral'}

        result['shenshu'] = self._safe_compute(
            'shenshu', analyze_shenshu,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
        ) or {}

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
        if xiangfa_val is not None:
            result['xiangfa'] = xiangfa_val

        # 宫身（宫位六亲）分析：星宫关系/夫妻宫专断/宫位互动，基于 xiangfa 的宫位象
        result['gongshen'] = self._safe_compute(
            'gongshen', analyze_gongshen,
            p.day_gan, p.day_zhi,
            p.year_gan, p.year_zhi,
            p.month_gan, p.month_zhi,
            p.hour_gan, p.hour_zhi,
            shishen=self.shishen,
            gender=self.input_data.get('gender', '男'),
        ) or {}

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
            result['dayun_analysis'] = self._safe_compute(
                'dayun_analysis', analyze_dayun_mangpai,
                dy_list, self.gans, self.zhis, self.day_gan,
                natal_fei_shen=fei_shen,
                kong_wang=self.kong_wang,
            ) or {}

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

        if liunian_data:
            ln_list = liunian_data if isinstance(liunian_data, list) else liunian_data.get('liunian', [])
            if ln_list:
                fei_shen = zg.get('fei_shen', []) if zg else []
                # 当下大运按当前年龄定位（与自动流年同锚点），非首步大运
                current_dy = self._current_dayun(dy_list) if isinstance(dy_list, list) else None
                result['liunian_analysis'] = self._safe_compute(
                    'liunian_analysis', analyze_liunian_mangpai,
                    ln_list, self.gans, self.zhis, self.day_gan,
                    current_dayun=current_dy,
                    natal_fei_shen=fei_shen,
                    kong_wang=self.kong_wang,
                    gender=self.input_data.get('gender'),
                    birth_year=self.input_data.get('year'),
                ) or {}

        # 交运时间计算（用年柱纳音五行定交运，大运序列从月柱起）
        # F1 标注：jiaoyun_analysis 仅进 _build_summary 交运行，不在 selectors
        # 不进 payload（LLM 见不到交运时刻本体，批10 P1 备案）。
        if self.input_data.get('year') and self.month_gz:
            result['jiaoyun_analysis'] = self._safe_compute(
                'jiaoyun_analysis', safe_compute_jiaoyun,
                self.input_data.get('year', 2000),
                self.month_gz,
                dayun_list=dy_list,
                start_age=start_age,
            ) or {}

        # 郑氏十排歌扩展分析（断语集锦 + 方法论）
        result['shipaige'] = self._safe_compute(
            'shipaige', analyze_shipaige,
            self.day_gan, self.day_zhi,
            self.year_gan, self.year_zhi,
            self.month_gan, self.month_zhi,
            self.hour_gan, self.hour_zhi,
        ) or {}

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
        ) or {}
        result['relations'] = relations

        gl = result.get('gongliang', {})
        zg = result.get('zuogong', {}) if result.get('zuogong') is not None else {}

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
        result['yunfan'] = self._safe_compute(
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
        ) or {}

        # A1 岁运反局切片：仅显式输入的运岁入否决链——大运须 da_yun 实给
        # （dy_list 非空），流年须外部注入（自动构造的三岁窗口仅作展示锚点，
        # 启发式命中率高，入否决会污染终身财命/官命口径）。
        yunfan_slice = current_fan_slice(
            result['yunfan'],
            f'{cur_dy_gan}{cur_dy_zhi}' if cur_dy_gan else '',
            include_dayun=bool(dy_list),
            include_liunian=bool(cur_ln_list) and not getattr(self, '_auto_liunian_injected', False),
        )

        # A3 方向总线：yongshen.assess_direction_signals 全引擎统一计算一次，
        # 透传各领域模块（hunyin/liuqin/xueli/zaihuo/gongmen_wuzhi 只读消费；
        # caiming/guanming/zhiye 已有内部否决链，口径同源）。
        # F1 标注：result['direction'] 仅模块间透传——payload(selectors)/
        # _build_summary/narrative 三出口均不可见（批10 备案，非纯死勿删）。
        from mangpai.subjective.yongshen import assess_direction_signals
        result['direction'] = self._safe_compute(
            'direction', assess_direction_signals,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            yunfan_result=yunfan_slice,
        ) or {}

        result['caiming'] = self._safe_compute(
            'caiming', analyze_caiming,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            muku_result=result.get('muku'),
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
        ) or {}

        result['guanming'] = self._safe_compute(
            'guanming', analyze_guanming,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
            kong_wang=self.kong_wang,
        ) or {}

        result['hunyin'] = self._safe_compute(
            'hunyin', analyze_hunyin,
            self.day_gan, self.gans, self.zhis,
            self.input_data.get('gender', '男'),
            dayun_gan=cur_dy_gan, dayun_zhi=cur_dy_zhi,
            liunian_gan=cur_ln_gan, liunian_zhi=cur_ln_zhi,
            relations=relations,
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
        ) or {}

        result['xueli'] = self._safe_compute(
            'xueli', analyze_xueli,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            direction_result=result.get('direction'),
        ) or {}

        result['laoyu'] = self._safe_compute(
            'laoyu', analyze_laoyu,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
        ) or {}

        # 贼神捕神/包制/冲链：已于 gongliang 之前算得（zb_res，供 gongliang 二次
        # 消费），此处复用同一份，避免重复扫描四柱。
        result['zeishen_bushen'] = zb_res

        # 象法九原则操作层（消费 muku/shensha；缺省自调客观检测）
        result['xiangfa_ops'] = self._safe_compute(
            'xiangfa_ops', analyze_xiangfa_ops,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            muku_result=result.get('muku'),
            shensha_result=result.get('shensha'),
        ) or {}

        result['zhiye'] = self._safe_compute(
            'zhiye', analyze_zhiye,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            shensha_result=result.get('shensha'),
            yunfan_result=yunfan_slice,
            caiming_result=result.get('caiming'),  # M2 基础职业类目消费财命tier/取财法
        ) or {}

        result['gongmen_wuzhi'] = self._safe_compute(
            'gongmen_wuzhi', analyze_gongmen_wuzhi,
            self.day_gan, self.gans, self.zhis,
            relations=relations, gongliang_result=gl,
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
        ) or {}

        result['liuqin'] = self._safe_compute(
            'liuqin', analyze_liuqin,
            self.day_gan, self.gans, self.zhis,
            self.input_data.get('gender', '男'),
            relations=relations,
            direction_result=result.get('direction'),
        ) or {}

        # 灾祸（消费 yunfan_result：detect_siwang 取岁运反局联动信号）
        result['zaihuo'] = self._safe_compute(
            'zaihuo', analyze_zaihuo,
            self.day_gan, self.gans, self.zhis,
            relations=relations,
            yunfan_result=result.get('yunfan'),
            shensha_result=result.get('shensha'),
            direction_result=result.get('direction'),
        ) or {}

        # 综合应期（原局=车，大运=路，流年=触发点；传 age 定位大限柱，
        # 三要素交集名副其实；无出生年则大限缺省空转）
        result['yingqi_subj'] = self._safe_compute(
            'yingqi_subj', infer_comprehensive_yingqi,
            self.day_gan, self.gans, self.zhis,
            cur_dy_gan, cur_dy_zhi, cur_ln_gan, cur_ln_zhi,
            age=self._current_age(),
        ) or {}

        # 郝金阳叙事层：把引擎结构化结论压成一行【引擎结论】（软依赖，
        # 仅 summarize，不调 LLM；render_hao_narrative 留给调用方按需触发）
        result['narrative'] = self._safe_compute(
            'narrative', summarize_engine_result, result
        ) or ''

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
    shensha_reference: str = 'year',
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
        shensha_reference: 神煞参考柱，默认 'year'
            （F1 标注：全库 0 处传 'day'，配置断路，口径分歧留 shensha 修复批）

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
]
