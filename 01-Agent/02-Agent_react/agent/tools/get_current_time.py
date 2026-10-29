"""获取当前时间；Action Input 填时区如 Asia/Shanghai，留空则用默认时区"""
from datetime import datetime
from zoneinfo import ZoneInfo
def run(area: str):
    tz = (area or "Asia/Shanghai").strip() or "Asia/Shanghai"
    try:
        now = datetime.now(ZoneInfo(tz))
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"ERROR: invalid timezone '{tz}': {e}"