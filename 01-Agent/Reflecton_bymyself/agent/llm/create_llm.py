from typing import Callable
from openai import OpenAI
from ..config import load_env
from ..log import print_message
import os

def create_llm(
    model: str = "deepseek-flash",
    base_url: str = "https://api.deepseek.com",
    api_key: str = None,
) -> Callable[[str, str], str]:
    load_env()
    client = OpenAI(
        api_key= api_key or os.environ.get("API_KEY"),
        base_url= base_url,
    )

    def llm(prompt: str, system_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
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
