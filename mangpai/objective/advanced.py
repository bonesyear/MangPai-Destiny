"""
objective/advanced — 向后兼容重导出（已拆分为独立模块）

此文件保留以兼容旧代码中的 from mangpai.objective.advanced import ... 调用。
新代码应直接从对应模块导入。

注意：早期版本在模块顶层 warnings.warn，会在 import mangpai.objective 时连带触发，
污染主包导入。已改为延迟触发：仅当显式访问 advanced 的导出符号时才告警。

⚠️ F1 批（2026-08-17）核实：6 个 eager re-export 符号（analyze_anhe 等）走
模块 globals 不触发 __getattr__，实际仅 analyze_zhengfan 单符号告警；
且全库零调用方（死 shim）。决议：保留最小兼容接口（防外部旧代码 import 炸），
不扩展、不新增引用。
"""
import warnings

from mangpai.objective.anhe import analyze_anhe
from mangpai.objective.biqi import analyze_biqi
from mangpai.objective.wood_type import analyze_wood_type
from mangpai.objective.soil_type import analyze_soil
from mangpai.objective.he_types import classify_he_types
from mangpai.objective.virtual_solid import analyze_virtual_solid
# analyze_zhengfan 已迁至 subjective 层；为避免 objective 反向依赖 subjective，
# 不在顶层 import，改由 __getattr__ 内 lazy-import（见下）。

_WARNED = False


def _deprecation_warn() -> None:
    """延迟触发弃用告警（仅在实际取用 advanced 导出符号时）。"""
    global _WARNED
    if not _WARNED:
        _WARNED = True
        warnings.warn(
            "objective.advanced 已拆分为独立模块，请直接从对应模块导入。"
            "例如：from mangpai.objective.anhe import analyze_anhe",
            DeprecationWarning,
            stacklevel=3,
        )


def __getattr__(name: str):
    if name in __all__:
        _deprecation_warn()
        if name == 'analyze_zhengfan':
            # 已迁至 subjective，lazy-import 避免客观层反向依赖主观层
            from mangpai.subjective.zhengfan import analyze_zhengfan
            return analyze_zhengfan
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'analyze_anhe', 'analyze_biqi', 'analyze_wood_type',
    'analyze_soil', 'classify_he_types', 'analyze_virtual_solid',
    'analyze_zhengfan',
]
