"""第二层审查共用测试架：从干支直接构造 engine 结果（书例只给干支不给公历）。
只读诊断，不改引擎代码。用法：
  from harness import run, run_mod
  res = run(['癸','辛','乙','丁'], ['未','酉','酉','丑'])  # 返回 compute_all() 全量
"""
import sys
import os

# 仓库根目录（mangpai/tests/backtest/harness.py -> 上三级）
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from mangpai import MangpaiEngine
from mangpai.objective.zuogong_detect import detect_relations


def _bazi_data(gans, zhis, gender='男', year=1960):
    from mangpai.objective.bazi_calc import compute_shishen, get_kong_wang
    bazi = {
        'year': gans[0] + zhis[0], 'month': gans[1] + zhis[1],
        'day': gans[2] + zhis[2], 'hour': gans[3] + zhis[3],
    }
    shishen = compute_shishen(gans[2], bazi['year'], bazi['month'], bazi['day'], bazi['hour'])
    kong_wang = get_kong_wang(gans[2], zhis[2])
    return {
        'bazi': bazi, 'shishen': shishen, 'kong_wang': kong_wang,
        'di_zhi_relations': {}, 'input': {'gender': gender, 'year': year},
    }


def run(gans, zhis, gender='男', year=1960):
    """全量引擎结果（含 zuogong/gongliang/caiming/...）。"""
    return MangpaiEngine(_bazi_data(gans, zhis, gender, year)).compute_all()


def zuogong(gans, zhis):
    """直接调 analyze_zuogong（带 shishen/kong_wang 缺省）。"""
    from mangpai.subjective.zuogong_confirm import analyze_zuogong
    return analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3])


def gongliang(gans, zhis):
    from mangpai.subjective.gongliang import analyze_gongliang
    return analyze_gongliang(day_gan=gans[2], gans=gans, zhis=zhis)


def show(name, res):
    zg = res['zuogong']; gl = res['gongliang']
    print(f"【{name}】 {res['bazi']['year']} {res['bazi']['month']} {res['bazi']['day']} {res['bazi']['hour']}")
    print(f"  zuogong: types={zg.get('work_types')} primary={zg.get('primary_work')} "
          f"level={zg.get('work_level')}/{zg.get('work_tier')} eff={zg.get('work_efficiency')}")
    print(f"  gongliang: level={gl.get('level')} score={gl.get('score')} tier={gl.get('tier_name')} "
          f"points={gl.get('gong_points')} zhi_jing={gl.get('zhi_jing')} penalty={gl.get('penalty')}")
    print(f"  gongliang.reasons: {gl.get('reasons')}")
