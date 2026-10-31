"""获取当前时间；Action Input 填时区如 Asia/Shanghai，留空则用默认时区"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Windows 上 Python 自带的 zoneinfo 没有 IANA 时区库，需要 PyPI 的 tzdata；
# 没装 tzdata 时退化为固定偏移，保证常见时区仍可用。
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
        offset = _FALLBACK_OFFSETS.get(key)
        if offset is None:
            raise
        hours, abbr = offset
        return timezone(timedelta(hours=hours), abbr)


def run(area: str):
    tz = (area or "Asia/Shanghai").strip() or "Asia/Shanghai"
    try:
        now = datetime.now(_load_tz(tz))
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"ERROR: invalid timezone '{tz}': {e}"
