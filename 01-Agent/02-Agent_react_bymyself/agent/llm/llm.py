"""返回大模型实例对象"""
import os
from ..config import load_env
from typing import Callable
from openai import OpenAI
from ..log import print_message
_SYSTEM_PROMPT=(
    "你是一个ReAct助手，严格按照要求的格式执行。"
    "每次回复仅输出一轮内容(Thought+Action+Action_Input或Thought+Final_Answer)"
    "需要时请调用工具，帮助用户解决问题，请用自然语言回答，回答语言与提问的语言一致。"
)

def  create_llm( api_key: str = None, model: str = "deepseek-flash", base_url: str = "https://api.deepseek.com") -> Callable[[str],str]:
    load_env()
    client = OpenAI(
        base_url = base_url,
        api_key = api_key or os.environ.get("API_KEY")
    )

    def llm(prompt: str) -> str:
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        resp = client.chat.completions.create(
            messages=messages,
            model=model
        )
        msg = resp.choices[0].message
        print("\n====<<< LLM response\n")
        print_message(msg)

        print("\n\n")
        print(f"Model>\t {msg.content}")
        print("\n\n")

        return msg.content or ""
        

    return llm