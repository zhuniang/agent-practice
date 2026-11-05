from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# 常用时区 -> (UTC 偏移小时数, 缩写)；只在系统缺 tzdata 时兜底
_FALLBACK_OFFSETS = {
    "Asia/Shanghai": (8, "CST"),
    "Asia/Hong_Kong": (8, "HKT"),
    "Asia/Taipei": (8, "CST"),
    "Asia/Singapore": (8, "SGT"),
    "Asia/Tokyo": (9, "JST"),
    "Asia/Seoul": (9, "KST"),
    "UTC": (0, "UTC"),
}

def _load_tz(key: str):
    try:
        return ZoneInfo(key)
    except ZoneInfoNotFoundError:
        if key not in _FALLBACK_OFFSETS:
            raise
        hours, abbr = _FALLBACK_OFFSETS[key]
        return timezone(timedelta(hours=hours), abbr)

def run(area: str = "Asia/Shanghai") -> str:
    """返回指定时区的当前时间"""
    area = (area or "").strip().strip('"\'').strip()   # 去掉 LLM 常带的引号和空白
    if not area:
        area = "Asia/Shanghai"
    tz = _load_tz(area)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")