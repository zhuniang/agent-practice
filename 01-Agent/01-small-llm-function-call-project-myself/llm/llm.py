"""LLM相关函数实现"""
from __future__ import annotations
import json
from openai import OpenAI
from tools import TOOLS
def call_llm(client: OpenAI, messages: list[dict], model: str):
    """调用大模型

    Args:
        client (OpenAI): _description_
        messages (list[dict]): _description_
        model (str): _description_
    """
    msg = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
    ).choices[0].message
    append_assistant(messages=messages,msg=msg)
    print_message(msg)
    return msg

def print_message(msg) -> None:
    """输出单条消息，过滤空值

    Args:
        msg (_type_): _description_
    """
    if hasattr(msg,"model_dump"):
        result = msg.model_dump(exclude_none=True)

    elif isinstance(msg,dict):
        result = {
            "role": msg["role"],
            "content": msg["content"],
        }
        if msg.get("tool_calls"):
            result["tool_calls"] = msg["tool_calls"]
    print("="*60)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("="*60)


def print_messages(messages: list[dict]) -> None:
    """输出多条消息

    Args:
        msg (_type_): _description_
    """
    for msg in messages:
        print_message(msg)

def append_assistant(messages: list[dict],msg):
    """添加message到上下文

    Args:
        msg (_type_): _description_
    """
    if hasattr(msg,"model_dump"):
        messages.append(msg.model_dump(exclude_none=True))
    elif isinstance(msg,dict):
        result = {
            "role": msg["role"],
            "content": msg["content"],
        }
        if msg.tool_calls:
            result["tool_calls"] = msg["tool_calls"]
        messages.append(result)
