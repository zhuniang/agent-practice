from ..base import Tool
from . import calculator, count_len, get_current_time

def build_tools_registry() ->dict[str, Tool]:
    return {
        "calculator": Tool(
            name = "calculator",
            description = "计算数学表达式，例如 21+21、233*233、(23+87)*23",
            run = calculator.run
        ),
        "count_len": Tool(
            name="count_len",
            description="统计字符串 长度,Action_Input填要统计的字符串",
            run= count_len.run
        ),
        "get_current_time": Tool(
            name= "get_current_time",
            description= "获取当前时间；Action_Input 填时区如 Asia/Shanghai，留空则用默认时区",
            run= get_current_time.run
        )
    }