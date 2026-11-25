"""命令路由：自然语言排盘 + /help + /ver（细挖 focus=财运/婚姻 二期预留）。

排盘输入两种：
  阳历 2000-01-01 12:00 男 北京（虚构示例）   （农历请用户自转阳历；性别必填）
  四柱 己卯 丙子 戊午 戊午 男 [2000]（虚构示例）  （year 可选，影响虚岁/大限和流年锚）
城市名查内置经度表；未收录城市可直接写给定经度（如 114.07）。
"""
from __future__ import annotations

import os
import re
import urllib.parse
from datetime import date
from typing import Optional

from mangpai.feishu.service import paipan
from mangpai.objective.bazi_calc import prc_dst_bounds
from mangpai.subjective.llm_backend import _API_URL, _env_value, llm_enabled

# 常用城市东经（真太阳时校正用）；未收录 → 提示用户直给经度。
CITY_LON = {
    '北京': 116.41, '天津': 117.20, '上海': 121.47, '重庆': 106.55,
    '广州': 113.26, '深圳': 114.06, '杭州': 120.16, '南京': 118.80,
    '苏州': 120.58, '武汉': 114.30, '成都': 104.07, '西安': 108.94,
    '郑州': 113.62, '信阳': 114.07, '洛阳': 112.45, '开封': 114.35,
    '长沙': 112.94, '合肥': 117.23, '济南': 117.12, '青岛': 120.38,
    '沈阳': 123.43, '哈尔滨': 126.53, '昆明': 102.83, '贵阳': 106.63,
    '福州': 119.30, '厦门': 118.09, '兰州': 103.83, '太原': 112.55,
    '石家庄': 114.51, '南昌': 115.86, '南宁': 108.37, '海口': 110.32,
    '香港': 114.17, '台北': 121.56, '乌鲁木齐': 87.62, '拉萨': 91.12,
}

HELP = """盲派排盘用法：
· 阳历排盘：阳历 2000-01-01 12:00 男 北京（虚构示例）
  （农历请先自转阳历；性别必填；城市未收录可直接写给定经度，如 … 男 114.07）
  （1986–1991 年历史夏令时区间请在末尾注明「夏令时」或「标准时」）
· 四柱直排：四柱 己卯 丙子 戊午 戊午 男 [2000]（虚构示例）
· /ver 版本基线 · /help 本帮助
（细挖 focus=财运/婚姻 二期开放）
隐私提示：{privacy}
命理分析仅供参考，不构成人生决策依据。"""


def help_text() -> str:
    if not llm_enabled():
        privacy = '当前未启用 LLM，生辰与排盘特征不外发。'
    else:
        base_url = _env_value('MANGPAI_LLM_BASE_URL', '') or _API_URL
        host = urllib.parse.urlsplit(base_url).hostname or 'api.deepseek.com'
        privacy = f'排盘数据（生辰/性别及排盘特征）将提交至 {host} 生成叙述。'
    return HELP.format(privacy=privacy)

_DATE_RE = re.compile(r'(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})\s*日?')
_TIME_RE = re.compile(r'(?<![\d:：.])(\d{1,2})\s*[:：点时]\s*(\d{1,2})?\s*分?')  # 前导边界防 '123:45'→23:45 静默截断
_LON_RE = re.compile(r'(?<![\d.])(-?\d{1,3}(?:\.\d{1,4})?)(?![\d.])')
_PILLAR_RE = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')
_GENDERS = {'男': '男', '乾': '男', 'male': '男', '女': '女', '坤': '女', 'female': '女'}


class ParseError(ValueError):
    """输入无法解析为排盘命令。"""


def version_line() -> str:
    """版本基线 = CHANGELOG 最新批次标题。"""
    path = os.path.join(os.path.dirname(__file__), os.pardir, 'CHANGELOG.md')
    with open(path, encoding='utf-8') as f:
        heading = next((ln.strip('# ').strip() for ln in f if ln.startswith('## ')), '未知')
    return f'引擎基线：{heading}\n知识库/通道文档：docs/knowledge-base.md · docs/llm-channel-20260818.md'


def _pop_gender(rest: str) -> tuple[str, Optional[str]]:
    tokens = rest.split()
    for i, t in enumerate(tokens):
        if t in _GENDERS:
            tokens.pop(i)
            return ' '.join(tokens), _GENDERS[t]
    return rest, None


_PROVINCE_PREFIXES = frozenset(
    '北京 天津 上海 重庆 河北 河南 山东 山西 陕西 湖南 湖北 江西 江苏 浙江 安徽 '
    '福建 广东 广西 海南 四川 贵州 云南 辽宁 吉林 黑龙江 甘肃 青海 新疆 西藏 宁夏 内蒙古'
    .split())


def _pop_lon_or_city(rest: str) -> tuple[str, Optional[float], str]:
    rest = rest.replace('北京时间', ' ').replace('（虚构示例）', ' ').replace('# synthetic', ' ')
    m = _LON_RE.search(rest)
    if m:
        lon = float(m.group(1))
        if re.search(r'西经|(?<![A-Za-z])[Ww](?=\s*-?\d)', rest):
            lon = -abs(lon)
        if -180.0 <= lon <= 180.0:
            return (rest[:m.start()] + rest[m.end():]), lon, f'经度{lon}'
    for name in sorted(CITY_LON, key=len, reverse=True):
        for word in rest.split():
            if word == name:
                return rest.replace(word, ' ', 1), CITY_LON[name], name
            for province in _PROVINCE_PREFIXES:
                if word == province + name:
                    return rest.replace(word, ' ', 1), CITY_LON[name], name
    return rest, None, ''


def parse_solar(text: str) -> dict:
    if re.search(r'农历|阴历|旧历', text):
        raise ParseError('农历/阴历输入请先换算为阳历，避免日期误排')
    is_dst = True if '夏令时' in text else (False if '标准时' in text else None)
    dm = _DATE_RE.search(text)
    if not dm:
        raise ParseError('没识别到阳历日期，示例：阳历 2000-01-01 12:00 男 北京（虚构示例）')
    rest = text[:dm.start()] + ' ' + text[dm.end():]
    tm = _TIME_RE.search(rest)
    if not tm:
        raise ParseError('没识别到出生时刻（时柱必需），示例：… 12:00 …')
    if re.match(r'\s*[:：]\s*\d', rest[tm.end():]):
        raise ParseError('时刻给到分钟即可，不支持秒位，示例：… 12:00 …')
    hour = int(tm.group(1))
    minute = 30 if re.match(r'\s*半', rest[tm.end():]) else int(tm.group(2) or 0)
    period = re.search(r'凌晨|上午|中午|下午|傍晚|晚上|AM|PM', rest, re.IGNORECASE)
    if period and period.group(0).upper() in ('下午', '傍晚', '晚上', 'PM'):
        if hour > 12:
            raise ParseError(f'{period.group(0)}与 24 小时制时刻矛盾，请核对')
        if hour < 12:
            hour += 12
    rest = rest[:tm.start()] + ' ' + rest[tm.end():]
    rest, gender = _pop_gender(rest)
    if not gender:
        raise ParseError('性别必填（男/女，大运方向依赖性别）')
    rest, lon, place = _pop_lon_or_city(rest)
    if lon is None:
        raise ParseError('请给出生地（内置城市表）或直接写给定经度，如：… 男 114.07')
    year, month, day = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
    bounds = prc_dst_bounds(year)
    if bounds and bounds[0].date() <= date(year, month, day) <= bounds[1].date() \
            and is_dst is None:
        raise ParseError('该日期可能处于历史夏令时，请在末尾注明「夏令时」或「标准时」')
    label = gender
    return {'kind': 'solar', 'year': year, 'month': month,
            'day': day, 'hour': hour, 'minute': minute, 'gender': gender, 'lon': lon,
            'is_dst': bool(is_dst), 'place': place, 'label': label}


def parse_pillars(text: str) -> dict:
    pillars = _PILLAR_RE.findall(text)
    rest = _PILLAR_RE.sub(' ', text)
    rest, gender = _pop_gender(rest)
    ym = re.search(r'(?<!\d)((?:19|20)\d{2})\s*年?', rest)
    return {'kind': 'pillars', 'pillars': pillars, 'gender': gender,
            'year': int(ym.group(1)) if ym else None,
            'label': f"四柱直排 {gender or ''}".strip()}


def handle(text: str, use_llm: Optional[bool] = None) -> str:
    """消息文本 → 回复文本。解析失败返回带示例的提示，不抛错。"""
    text = (text or '').strip()
    if not text or text in ('/help', 'help', '帮助', '？', '?'):
        return help_text()
    if text in ('/ver', '/version', '版本'):
        return version_line()
    try:
        if '四柱' in text and not _DATE_RE.search(text):
            # 触发词不抢占：文本同时含阳历日期 → 走阳历（阳历优先）
            return paipan(parse_pillars(text), use_llm=use_llm)
        return paipan(parse_solar(text), use_llm=use_llm)
    except (ParseError, ValueError) as e:
        return f'输入有误：{e}\n\n{help_text()}'
