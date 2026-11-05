from typing import Callable
from openai import OpenAI
from ..config import load_env
from ..log import print_message
import os
SYSTEM_PROMPT = (
    "你是一个ReAct智能体，帮助用户解决问题"
    "每次回复仅输出一轮内容，(Thought+Action+Action Input 或 Thought+Final Answer)"
    "需要时调用工具，用自然语言回答，语言和问题一致。"
)
def create_llm(
    model: str = "deepseek-flash",
    base_url: str = "https://api.deepseek.com",
    api_key: str = None,
) -> Callable[[str], str]:
    load_env()
    client = OpenAI(
        api_key= api_key or os.environ.get("API_KEY"),
        base_url= base_url,
    )

    def llm(prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        resp = client.chat.completions.create(
            model= model,
            messages=messages,
        )
        msg = resp.choices[0].message
        print("="*88)
        print(f"LLM>>")
        print_message(msg)
        print("="*88)
        print()
        return msg.content or ""
    return llm
