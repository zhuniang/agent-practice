from __future__ import annotations
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
load_dotenv()
MAX_STEPS = 5

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
def getWeather(city: str):
    wearther_map = {
        "北京":"19℃",
        "上海":"21℃",
    }
    return wearther_map.get(city,f"没有查找到{city}的天气")
MODEL = "deepseek-flash"
TOOLS_DICT = {
    "getWeather": getWeather
}
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "getWeather",
            "description": "这是一个查询城市天气的工具，请在用户询问某个城市天气、是否要下雨时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "中文城市名，例如：北京、上海",
                    }
                },
                "required": ["city"]
            }
        }
    }
]
messages = [{"role": "system","content": "你是一个天气查询助手，请根据用户的问题回答"}]
messages.append({"role": "user","content": "北京今天天气怎么样"})
for i in range(MAX_STEPS):
    resp = client.chat.completions.create(
        model=MODEL,
        tools=TOOLS,
        messages=messages,
        tool_choice="auto"
    )
    msg = resp.choices[0].message
    print(msg.model_dump_json(indent=2))
    messages.append(
        {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": [tc.model_dump() for tc in msg.tool_calls or []]
        }
    )
    if not msg.tool_calls:
        print(messages[-1].get("content"))
        break
    # messages.append(msg)

    # print(json.dumps(msg.model_dump(exclude_none=True),indent=2))
    for tc in msg.tool_calls:
        # print(tc.function.arguments)
        tcres = TOOLS_DICT.get(tc.function.name)(**(json.loads(tc.function.arguments)))
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": tcres})

    
    