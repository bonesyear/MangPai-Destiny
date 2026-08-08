# 批5 逐例诊断：跑指定 case id，打印 caiming 关键字段 + 方向信号 + 从格判定
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import yaml
from mangpai.engine import MangpaiEngine
from blind_eval import _bazi_data

HERE = os.path.dirname(os.path.abspath(__file__))

def diag(cid):
    cases = yaml.safe_load(open(os.path.join(HERE, '..', 'trainset', 'cases.yaml'), encoding='utf-8')) + \
        yaml.safe_load(open(os.path.join(HERE, 'cases.yaml'), encoding='utf-8'))
    c = next(x for x in cases if x['id'] == cid)
    res = MangpaiEngine(_bazi_data(c)).compute_all()
    cm = res.get('caiming', {})
    print(f"== {cid}  bazi={c['bazi']}  verdict={c.get('verdicts',{}).get('财命')}")
    print(' tier_static:', cm.get('tier_static'), ' tier:', cm.get('tier'))
    print(' summary_static:', cm.get('summary_static'))
    lv = cm.get('level_static', {}) or {}
    print(' base_level:', lv.get('base_level'), ' adjust:', lv.get('adjust'))
    print(' desc:', lv.get('desc'))
    # 从格
    from mangpai.subjective.yongshen import classify_strength, classify_cong_target, assess_direction_signals
    b = c['bazi']
    if 'year_gan' in b:
        gans = [b.get('year_gan'), b.get('month_gan'), b.get('day_gan'), b.get('hour_gan')]
        zhis = [b.get('year_zhi'), b.get('month_zhi'), b.get('day_zhi'), b.get('hour_zhi')]
    else:
        gans = [b[k][0] for k in ('year', 'month', 'day', 'hour')]
        zhis = [b[k][1] for k in ('year', 'month', 'day', 'hour')]
    dg = gans[2]
    st = classify_strength(dg, gans, zhis)
    print(' strength:', st, ' cong_target:', classify_cong_target(dg, gans, zhis, st).get('label'))
    gl = res.get('gongliang', {})
    print(' gongliang level:', gl.get('level'), ' qual:', gl.get('qualitative', ''))
    ds = assess_direction_signals(dg, gans, zhis,
                                  gongliang_result=res.get('gongliang'),
                                  zhengfan_result=res.get('zhengfan'))
    print(' direction:', ds['direction'], ' fanju:', ds['fanju'])
    print(' reasons:', json.dumps(ds['reasons'], ensure_ascii=False))
    zf = res.get('zhengfan', {})
    print(' zhengfan:', zf.get('type'), zf.get('reason', zf.get('configuration', '')))

if __name__ == '__main__':
    for cid in sys.argv[1:]:
        try:
            diag(cid)
        except Exception as e:
            import traceback; traceback.print_exc()
        print()
