from __future__ import annotations
from openai import OpenAI
from typing import Any,List
import json
from pprint import pprint
from dotenv import load_dotenv
import os
load_dotenv("D:\\projects\\AI-Engineer-from-scrach\\.env")
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)
MODEL = "deepseek-flash"
def getWeather(city: str):
    mock_data={
        "北京":"19℃",
        "上海":"26℃"
    }
    city=city.strip()
    return mock_data.get(city,f"暂无{city}数据")

# 工具名 -> 可调用对象。模型的 tool_calls 里给的是字符串名字，得靠这张表路由
TOOL_REGISTRY = {"getWeather": getWeather}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "getWeather",
            "description": "这是一个查询天气工具，当用户询问，某城市天气、气温、是否需要带伞时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，如 北京、上海",
                    }
                },
                "required": ["city"],
            }
        }
    },
]

messages=[{"role":"user","content":"北京多少度？"}]
MAX_STEPS=5
for step in range(MAX_STEPS):
    resp = client.chat.completions.create(
        messages=messages,
        tools=TOOLS,
        model=MODEL,
        tool_choice="auto"
    )
    msg = resp.choices[0].message
    print(msg.model_dump_json(indent=2,ensure_ascii=False))
    if not msg.tool_calls:
        print("最终回答：", msg.content)
        break

    # ① 先回填 assistant 那条（含 tool_calls）
    messages.append(msg.model_dump(exclude_none=True))
    # print(json.dumps(msg.model_dump(exclude_none=True), indent=2, ensure_ascii=False))
    # ② 再为每个 tool_call 回填一条 role="tool"，一个都不能少
    for tc in msg.tool_calls:
        fn = TOOL_REGISTRY.get(tc.function.name)
        if fn is None:
            result = f"未知工具：{tc.function.name}"
        else:
            try:
                result = fn(**json.loads(tc.function.arguments or "{}"))
            except Exception as e:
                result = f"工具执行失败：{e}"
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,          # 必须和 tc.id 完全一致
            "content": json.dumps(result, ensure_ascii=False),
        })
else:
    pprint(f"过了{MAX_STEPS}轮还未收敛")








