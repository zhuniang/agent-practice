import os
from typing import Callable
from ..config import load_env
from openai import OpenAI
from .log import print_messages,print_message

_SYSTEM_PROMPT = (
    "You are a ReAct agent. Follow the requested format exactly. "
    "Output only ONE turn per response (Thought + Action + Action Input, OR Thought + Final Answer). "
    "Use tools when needed, then give Final Answer in the same language as the question."
)

def create_deepseek_llm(
        model: str = "deepseek-flash",
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
) -> Callable[[str], str]:
    """创建 DeepSeek 调用函数（OpenAI 兼容接口）。

    Args:
        model (str, optional): _description_. Defaults to "deepseek-flash".
        api_key (str | None, optional): _description_. Defaults to None.
        base_url (_type_, optional): _description_. Defaults to "https://api.deepseek.com".

    Returns:
        Callable[[str], str]: _description_
    """
    load_env()
    key = api_key or os.environ.get("API_KEY")
    if not key:
        raise ValueError(
            "未找到 API Key。请在项目根目录创建 .env 并设置 API_KEY，"
            "或设置系统环境变量，或在 create_deepseek_llm(api_key=...) 中传入。"
        )
    client = OpenAI(
        base_url=base_url,
        api_key=key
    )
    def llm(prompt: str) -> str:
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        print("\n====>>> LLM request \n")
        print_messages(messages)

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        msg = resp.choices[0].message
        print("\n====<<< LLM response\n")
        print_message(msg)

        print("\n\n")
        print(f"Model>\t {msg.content}")
        print("\n\n")
        return msg.content or ""

    return llm