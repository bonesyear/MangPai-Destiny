"""基础中性层（foundation）

存放流派无关、可被各命理流派共享的「中性」计算与规则。
与 mangpai（盲派特异层）相对：foundation 只收录各流派共识或经典原典中
不依附于某一流派解释机制的纯计算/纯规则，不引入盲派特有的做功、宾主、
虚实、墓库等概念。

分层方向（单向依赖）：
    foundation（中性） <- mangpai/objective（盲派客观） <- mangpai/subjective <- engine

依赖规则：
    - foundation 不得反向依赖 mangpai 或任何上层包。
    - mangpai 可 from foundation.objective.xxx import ... 复用中性计算。
"""
__all__ = ['objective']
